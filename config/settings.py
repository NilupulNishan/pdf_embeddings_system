"""
Configuration management for the PDF Embeddings System.
Loads settings from environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

# Model Deployments
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4o")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")

# Embedding Configuration
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", 3072))

# Processing Configuration
CHUNK_SIZES_STR = os.getenv("CHUNK_SIZES", "4096,1024,512")
CHUNK_SIZES = [int(size.strip()) for size in CHUNK_SIZES_STR.split(",")]
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", 6))

# Paths
PDF_DIRECTORY = PROJECT_ROOT / os.getenv("PDF_DIRECTORY", "data/pdfs")
CHROMA_DB_PATH = PROJECT_ROOT / os.getenv("CHROMA_DB_PATH", "data/chroma_db")

# Create directories if they don't exist
PDF_DIRECTORY.mkdir(parents=True, exist_ok=True)
CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)


def validate_config():
    """Validate that all required configuration is present."""
    required_vars = {
        "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
        "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please check your .env file."
        )
    
    print("✓ Configuration validated successfully")
    return True


if __name__ == "__main__":
    # Test configuration
    validate_config()
    print(f"\nConfiguration:")
    print(f"  PDF Directory: {PDF_DIRECTORY}")
    print(f"  ChromaDB Path: {CHROMA_DB_PATH}")
    print(f"  Chunk Sizes: {CHUNK_SIZES}")
    print(f"  Embedding Dimensions: {EMBEDDING_DIMENSIONS}")