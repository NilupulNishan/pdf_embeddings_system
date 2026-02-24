# src/pdf_loader.py
"""
Production-grade PDF loader with per-page document creation.

Hybrid mode:
- Extract embedded text using LlamaIndex PyMuPDFReader (fast)
- If a page has little/no embedded text AND contains images -> OCR that page (optional)
- Keeps existing metadata keys used by your pipeline: filename, file_path, page, total_pages, etc.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List, Tuple, Optional

from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document

logger = logging.getLogger(__name__)

# Optional OCR deps
try:
    import fitz  # PyMuPDF (low-level)
    from PIL import Image
    import pytesseract

    HAS_OCR_DEPS = True
except Exception:
    HAS_OCR_DEPS = False


class PDFLoader:
    """
    Loads PDFs with proper page-level metadata.

    Each page becomes a separate Document with complete metadata.
    LlamaIndex automatically propagates this metadata to all chunks.
    """

    def __init__(
        self,
        *,
        enable_ocr: bool = True,
        ocr_dpi: int = 200,
        ocr_min_chars: int = 60,
        ocr_min_images: int = 1,
        tesseract_cmd: Optional[str] = None,
    ):
        """
        Args:
            enable_ocr: Enable OCR fallback for scanned/image pages
            ocr_dpi: Rasterization DPI for OCR
            ocr_min_chars: If extracted text chars < this, page may be considered "empty"
            ocr_min_images: Minimum number of images on page to trigger OCR fallback
            tesseract_cmd: Optional explicit path to tesseract executable (prefer env var)
        """
        self.loader = PyMuPDFReader()

        # OCR config
        self.enable_ocr_requested = enable_ocr
        self.enable_ocr = bool(enable_ocr and HAS_OCR_DEPS)
        self.ocr_dpi = int(ocr_dpi)
        self.ocr_min_chars = int(ocr_min_chars)
        self.ocr_min_images = int(ocr_min_images)

        # Configure tesseract path safely (no hardcoding)
        if HAS_OCR_DEPS:
            cmd = tesseract_cmd or os.getenv("TESSERACT_CMD")
            if cmd:
                pytesseract.pytesseract.tesseract_cmd = cmd

        if self.enable_ocr_requested and not HAS_OCR_DEPS:
            logger.warning(
                "OCR requested but OCR dependencies not installed (fitz/PIL/pytesseract)."
            )

        logger.info("PDFLoader initialized (OCR=%s)", self.enable_ocr)

    # -----------------------------
    # Collection naming
    # -----------------------------
    def get_collection_name(self, pdf_path: Path) -> str:
        """
        Generate a valid ChromaDB collection name from PDF filename.

        ChromaDB collection names: alphanumeric + underscores only
        """
        name = pdf_path.stem
        collection_name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
        return collection_name.lower()

    # -----------------------------
    # OCR helpers
    # -----------------------------
    def _needs_ocr(self, page, extracted_text: str) -> bool:
        """
        Decide whether OCR is needed for this page.
        We trigger OCR if:
          - embedded extracted text is short AND
          - page contains at least N images
        """
        if len((extracted_text or "").strip()) >= self.ocr_min_chars:
            return False

        try:
            imgs = page.get_images(full=True)
        except Exception:
            imgs = []

        return len(imgs) >= self.ocr_min_images

    def _ocr_page(self, doc, page_index: int) -> str:
        """
        OCR a page by rasterizing it and running pytesseract.
        """
        page = doc.load_page(page_index)
        mat = fitz.Matrix(self.ocr_dpi / 72.0, self.ocr_dpi / 72.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return (pytesseract.image_to_string(img) or "").strip()

    @staticmethod
    def _looks_useful(text: str, min_chars: int = 40) -> bool:
        """
        Quick heuristic to ignore garbage OCR.
        """
        t = (text or "").strip()
        if len(t) < min_chars:
            return False
        alnum = sum(ch.isalnum() for ch in t)
        return (alnum / max(len(t), 1)) > 0.2

    # -----------------------------
    # Main loading functions
    # -----------------------------
    def load_pdf(self, pdf_path: Path) -> Tuple[List[Document], str]:
        """
        Load a PDF as separate page documents with metadata.
        Optionally OCR weak pages (scanned/image pages).

        Returns:
            (list_of_page_documents, collection_name)
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        logger.info("Loading PDF: %s", pdf_path.name)

        # 1) Extract embedded text per page via LlamaIndex reader
        try:
            page_docs = self.loader.load(file_path=pdf_path)  # one Document per page
        except Exception as e:
            logger.error("Failed to load %s via PyMuPDFReader: %s", pdf_path.name, e)
            raise

        if not page_docs:
            raise ValueError(f"No pages extracted from {pdf_path.name}")

        total_pages = len(page_docs)

        # Build embedded text lookup (1-indexed pages)
        extracted_text_by_page: dict[int, str] = {}
        for i, page_doc in enumerate(page_docs):
            extracted_text_by_page[i + 1] = page_doc.get_content() or ""

        # 2) OCR augmentation (only if enabled)
        ocr_text_by_page: dict[int, str] = {}
        if self.enable_ocr:
            # Best-effort warning if Tesseract isn't configured (esp. Windows)
            tcmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "") or ""
            if os.name == "nt" and tcmd and not Path(tcmd).exists():
                logger.warning(
                    "Tesseract executable not found at: %s (set TESSERACT_CMD env var or pass tesseract_cmd)",
                    tcmd,
                )

            try:
                pdf = fitz.open(str(pdf_path))
                for i in range(len(pdf)):
                    page_no = i + 1
                    page = pdf.load_page(i)
                    embedded_text = extracted_text_by_page.get(page_no, "")

                    if not self._needs_ocr(page, embedded_text):
                        continue

                    try:
                        ocr_text = self._ocr_page(pdf, i)
                    except Exception as e:
                        logger.warning(
                            "OCR failed for %s page %s: %s", pdf_path.name, page_no, e
                        )
                        continue

                    if self._looks_useful(ocr_text):
                        ocr_text_by_page[page_no] = ocr_text
                pdf.close()
            except Exception as e:
                logger.warning("OCR skipped for %s (fitz open failed): %s", pdf_path.name, e)

        # 3) Build final per-page Documents with your existing metadata schema
        enhanced_docs: List[Document] = []
        collection_name = self.get_collection_name(pdf_path)

        for page_no in range(1, total_pages + 1):
            embedded = (extracted_text_by_page.get(page_no, "") or "").strip()
            ocr_text = (ocr_text_by_page.get(page_no, "") or "").strip()

            is_ocr = False
            final_text = embedded

            # If OCR exists: replace weak embedded text; otherwise append as extra signal
            if ocr_text:
                if len(final_text) < self.ocr_min_chars:
                    final_text = ocr_text
                    is_ocr = True
                else:
                    final_text = f"{final_text}\n\n[OCR]\n{ocr_text}"
                    is_ocr = True

            enhanced_docs.append(
                Document(
                    text=final_text,
                    metadata={
                        # File information
                        "filename": pdf_path.name,
                        "file_path": str(pdf_path.absolute()),
                        "collection_name": collection_name,
                        # Page information
                        "page": page_no,
                        "total_pages": total_pages,
                        # Source tracking
                        "source": str(pdf_path),
                        "source_type": "pdf",
                        # OCR marker
                        "is_ocr": is_ocr,
                    },
                )
            )

        logger.info(
            "  ✓ Loaded %s pages from %s (OCR pages: %s)",
            len(enhanced_docs),
            pdf_path.name,
            len(ocr_text_by_page),
        )

        return enhanced_docs, collection_name

    def get_pdf_files(self, directory: Path) -> List[Path]:
        """
        Get all PDF files from a directory.

        Raises:
            ValueError: If directory doesn't exist or no PDFs found
        """
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        pdf_files = list(directory.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {directory}")

        logger.info("Found %s PDF(s) in %s", len(pdf_files), directory)
        return sorted(pdf_files)

    def load_all_pdfs(self, directory: Path) -> List[Tuple[List[Document], str, Path]]:
        """
        Load all PDFs from a directory.

        Returns:
            List of tuples: (page_documents, collection_name, pdf_path)
        """
        pdf_files = self.get_pdf_files(directory)
        results: List[Tuple[List[Document], str, Path]] = []

        logger.info("Loading %s PDF(s)", len(pdf_files))
        print("=" * 80)

        for pdf_path in pdf_files:
            try:
                documents, collection_name = self.load_pdf(pdf_path)
                results.append((documents, collection_name, pdf_path))
                print(f"✓ {pdf_path.name} → {collection_name} ({len(documents)} pages)")
            except Exception as e:
                logger.error("Failed to load %s: %s", pdf_path.name, e)
                print(f"✗ {pdf_path.name} - Error: {e}")
                continue

        print("=" * 80)
        logger.info("Successfully loaded %s/%s PDFs", len(results), len(pdf_files))
        return results


if __name__ == "__main__":
    # Quick local test
    logging.basicConfig(level=logging.INFO)

    # Example: enable OCR if deps installed + TESSERACT_CMD env var set
    loader = PDFLoader(enable_ocr=True)

    # Change to a real folder if you want to test manually
    test_dir = Path("data/pdfs")
    try:
        data = loader.load_all_pdfs(test_dir)
        print(f"\nLoaded {len(data)} PDFs.")
        if data:
            docs, coll, path = data[0]
            print(f"First PDF: {path.name} | Collection: {coll} | Pages: {len(docs)}")
            print("First page metadata:", docs[0].metadata)
            print("First page text preview:", docs[0].text[:200])
    except Exception as e:
        print("Test error:", e)