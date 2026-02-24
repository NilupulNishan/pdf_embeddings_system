"""
Centralized metadata management for page tracking and link generation.

Updated for Azure App Service (Docker):
- Generates HTTP(S) links using PDF_BASE_URL (e.g. https://<app>.azurewebsites.net/pdfs)
- Falls back to file:// links only if PDF_BASE_URL is NOT set
"""
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)


class MetadataManager:
    """
    Handles all metadata operations for page tracking and source citation.

    Responsibilities:
    - Extract page numbers from nodes
    - Merge consecutive page ranges
    - Generate hosted PDF URLs (preferred) or file:// URLs (fallback)
    - Validate metadata integrity
    """

    # If you set this in Azure App Service -> Configuration -> Application settings,
    # links will be:  https://<app>.azurewebsites.net/pdfs/<filename>.pdf#page=<n>
    #
    # Example:
    #   PDF_BASE_URL = "https://myapp.azurewebsites.net/pdfs"
    PDF_BASE_URL: str = getattr(settings, "PDF_BASE_URL", "").rstrip("/")

    @staticmethod
    def extract_page_from_node(node) -> Optional[int]:
        """
        Extract page number from a single node.

        Args:
            node: Node with metadata

        Returns:
            Page number or None if not found
        """
        if not hasattr(node, "metadata"):
            return None

        # Try 'page' key (standard)
        page = node.metadata.get("page")
        if page:
            try:
                return int(page)
            except Exception:
                return None

        # Try 'start_page' (fallback)
        page = node.metadata.get("start_page")
        if page:
            try:
                return int(page)
            except Exception:
                return None

        return None

    @staticmethod
    def extract_pages_from_nodes(nodes: List) -> List[int]:
        """
        Extract unique page numbers from multiple nodes.

        Args:
            nodes: List of nodes with metadata

        Returns:
            Sorted list of unique page numbers
        """
        pages = set()

        for node in nodes:
            page = MetadataManager.extract_page_from_node(node)
            if page is not None:
                pages.add(page)

        result = sorted(pages)
        logger.debug(f"Extracted {len(result)} unique pages from {len(nodes)} nodes")
        return result

    @staticmethod
    def merge_consecutive_pages(pages: List[int]) -> List[Tuple[int, int]]:
        """
        Merge consecutive page numbers into ranges.

        Examples:
            [1, 2, 3, 7, 8] → [(1, 3), (7, 8)]
            [5, 10, 15] → [(5, 5), (10, 10), (15, 15)]
            [1] → [(1, 1)]

        Args:
            pages: Sorted list of page numbers

        Returns:
            List of tuples (start_page, end_page)
        """
        if not pages:
            return []

        ranges: List[Tuple[int, int]] = []
        start = pages[0]
        end = pages[0]

        for page in pages[1:]:
            if page == end + 1:
                end = page
            else:
                ranges.append((start, end))
                start = page
                end = page

        ranges.append((start, end))
        logger.debug(f"Merged {len(pages)} pages into {len(ranges)} ranges")
        return ranges

    @staticmethod
    def format_page_range(start: int, end: int) -> str:
        """
        Format a page range for display.

        Args:
            start: Start page
            end: End page

        Returns:
            Formatted string like "Page 25" or "Pages 45-47"
        """
        return f"Page {start}" if start == end else f"Pages {start}-{end}"

    @staticmethod
    def generate_file_url(file_path: str, page: int) -> str:
        """
        Generate a URL that opens PDF at a specific page.

        Preferred (HOSTED):
            Uses settings.PDF_BASE_URL + filename
            Example:
              PDF_BASE_URL=https://myapp.azurewebsites.net/pdfs
              -> https://myapp.azurewebsites.net/pdfs/manual.pdf#page=25

        Fallback (LOCAL):
            file:///...#page=25 (works only on local machine)
        """
        try:
            filename = Path(file_path).name
        except Exception:
            filename = None

        # ✅ Hosted link (Azure / any web host)
        base = getattr(settings, "PDF_BASE_URL", "").rstrip("/")
        if base and filename:
            return f"{base}/{filename}#page={page}"

        # 🟡 Fallback to file:// (local dev)
        try:
            path = Path(file_path).absolute()

            # Windows drive letter handling
            if path.drive:
                return f"file:///{path.as_posix()}#page={page}"
            return f"file://{path.as_posix()}#page={page}"
        except Exception:
            # Last-resort: no link
            return ""

    @staticmethod
    def extract_file_path_from_nodes(nodes: List) -> Optional[str]:
        """
        Extract file path from nodes (assumes all from same file).

        Args:
            nodes: List of nodes

        Returns:
            File path or None
        """
        for node in nodes:
            if hasattr(node, "metadata"):
                file_path = node.metadata.get("file_path")
                if file_path:
                    return file_path
        return None

    @staticmethod
    def extract_filename_from_nodes(nodes: List) -> str:
        """
        Extract filename from nodes.

        Args:
            nodes: List of nodes

        Returns:
            Filename or "unknown.pdf"
        """
        for node in nodes:
            if hasattr(node, "metadata"):
                filename = node.metadata.get("filename")
                if filename:
                    return filename
        return "unknown.pdf"

    @staticmethod
    def validate_metadata(node) -> bool:
        """
        Validate that a node has required metadata.

        Args:
            node: Node to validate

        Returns:
            True if valid, False otherwise
        """
        if not hasattr(node, "metadata"):
            return False

        required_keys = ["page", "filename", "file_path"]
        return all(key in node.metadata for key in required_keys)

    @staticmethod
    def get_metadata_summary(nodes: List) -> Dict[str, Any]:
        """
        Get summary statistics about node metadata.

        Args:
            nodes: List of nodes

        Returns:
            Dictionary with summary info
        """
        pages = MetadataManager.extract_pages_from_nodes(nodes)
        file_path = MetadataManager.extract_file_path_from_nodes(nodes)
        filename = MetadataManager.extract_filename_from_nodes(nodes)

        valid_count = sum(1 for node in nodes if MetadataManager.validate_metadata(node))

        return {
            "total_nodes": len(nodes),
            "valid_metadata_count": valid_count,
            "unique_pages": len(pages),
            "page_range": (min(pages), max(pages)) if pages else None,
            "filename": filename,
            "file_path": file_path,
            "pdf_base_url": getattr(settings, "PDF_BASE_URL", "").rstrip("/") or None,
        }


if __name__ == "__main__":
    # Test metadata manager
    from llama_index.core.schema import TextNode

    test_nodes = [
        TextNode(
            text="Content 1",
            metadata={"page": 5, "filename": "test.pdf", "file_path": "/app/data/pdfs/test.pdf"},
        ),
        TextNode(
            text="Content 2",
            metadata={"page": 6, "filename": "test.pdf", "file_path": "/app/data/pdfs/test.pdf"},
        ),
        TextNode(
            text="Content 3",
            metadata={"page": 7, "filename": "test.pdf", "file_path": "/app/data/pdfs/test.pdf"},
        ),
        TextNode(
            text="Content 4",
            metadata={"page": 10, "filename": "test.pdf", "file_path": "/app/data/pdfs/test.pdf"},
        ),
    ]

    print("Testing MetadataManager:\n")

    pages = MetadataManager.extract_pages_from_nodes(test_nodes)
    print(f"1. Extracted pages: {pages}")

    ranges = MetadataManager.merge_consecutive_pages(pages)
    print(f"2. Merged ranges: {ranges}")

    for start, end in ranges:
        formatted = MetadataManager.format_page_range(start, end)
        print(f"3. Formatted: {formatted}")

    url = MetadataManager.generate_file_url("/app/data/pdfs/test.pdf", 5)
    print(f"4. Generated URL: {url}")

    summary = MetadataManager.get_metadata_summary(test_nodes)
    print(f"5. Metadata summary: {summary}")