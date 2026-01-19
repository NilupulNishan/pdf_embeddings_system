
"""
PDF processing module for loading and extracting text from PDF documents.
"""
from pathlib import Path
from typing import List, Tuple
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document

class PDFProcessor:
    """Handles PDF file loading and text extraction."""

    def __init__(self, pdf_directory: Path):
        self.reader = PyMuPDFReader()

    def get_pdf_files(self, directory: Path) -> List[Path]:
        """
        Get all PDF files from a directory.
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            List of PDF file paths
        """
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        pdf_files = list(directory.glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in {directory}")
        
        return sorted(pdf_files)
    

    def get_collection_name(self, pdf_path: Path) -> str:
        """
        Generate a ChromaDB collection name from PDF filename.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Valid collection name (no spaces or special chars)
        """
        # Remove extension and replace spaces/special chars with underscores
        name = pdf_path.stem
        # ChromaDB collection names must be alphanumeric with underscores
        collection_name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
        return collection_name.lower()
    
    def load_pdf(self, pdf_path: Path) -> Tuple[Document, str]:
        """
        Load a PDF and return a single Document with all pages stitched together.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (Document, collection_name)
        """
        print(f"Loading PDF: {pdf_path.name}")
        
        # Load PDF pages
        docs = self.loader.load(file_path=pdf_path)
        
        # Stitch pages together
        doc_text = "\n\n".join([d.get_content() for d in docs])
        
        # Create single document with metadata
        document = Document(
            text=doc_text,
            metadata={
                "filename": pdf_path.name,
                "source": str(pdf_path),
                "page_count": len(docs)
            }
        )
        
        collection_name = self.get_collection_name(pdf_path)
        
        print(f"  Pages: {len(docs)}")
        print(f"  Characters: {len(doc_text):,}")
        print(f"  Collection name: {collection_name}")
        
        return document, collection_name
    

    def load_all_pdfs(self, directory: Path) -> List[Tuple[Document, str, Path]]:
        """
        Load all PDFs from a directory.
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            List of tuples: (Document, collection_name, pdf_path)
        """
        pdf_files = self.get_pdf_files(directory)
        results = []
        
        print(f"\nFound {len(pdf_files)} PDF(s) in {directory}")
        print("=" * 80)
        
        for pdf_path in pdf_files:
            try:
                document, collection_name = self.load_pdf(pdf_path)
                results.append((document, collection_name, pdf_path))
                print()
            except Exception as e:
                print(f"  Error loading {pdf_path.name}: {e}")
                print()
                continue
        
        return results
    

if __name__ == "__main__":
    # Test the processor
    from config.settings import PDF_DIRECTORY
    
    processor = PDFProcessor()
    
    try:
        results = processor.load_all_pdfs(PDF_DIRECTORY)
        print(f"\nSuccessfully loaded {len(results)} PDF(s)")
        
        for doc, coll_name, path in results:
            print(f"  {path.name} → {coll_name}")
    except Exception as e:
        print(f"Error: {e}")