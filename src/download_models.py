"""
Model Download Script

Downloads required models for the technical document ML pipeline.
"""

import os
import sys
import logging
from pathlib import Path
import subprocess
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def download_file(url: str, filepath: Path, chunk_size: int = 8192):
    """Download a file with progress bar."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=filepath.name) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        logger.info(f"Downloaded: {filepath}")
        
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        if filepath.exists():
            filepath.unlink()
        raise


def download_spacy_model(model_name: str = "en_core_web_sm"):
    """Download spaCy model."""
    try:
        logger.info(f"Downloading spaCy model: {model_name}")
        subprocess.run([
            sys.executable, "-m", "spacy", "download", model_name
        ], check=True)
        logger.info(f"Successfully downloaded spaCy model: {model_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading spaCy model: {e}")
        raise


def download_nltk_data():
    """Download NLTK data."""
    try:
        logger.info("Downloading NLTK data...")
        import nltk
        
        # Download required NLTK data
        nltk_data = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words'
        ]
        
        for data_name in nltk_data:
            logger.info(f"Downloading NLTK data: {data_name}")
            nltk.download(data_name, quiet=True)
        
        logger.info("Successfully downloaded NLTK data")
        
    except Exception as e:
        logger.error(f"Error downloading NLTK data: {e}")
        raise


def download_sentence_transformer_model(model_name: str = "all-MiniLM-L6-v2"):
    """Download sentence transformer model."""
    try:
        logger.info(f"Downloading sentence transformer model: {model_name}")
        from sentence_transformers import SentenceTransformer
        
        # This will automatically download the model
        model = SentenceTransformer(model_name)
        logger.info(f"Successfully downloaded sentence transformer model: {model_name}")
        
    except Exception as e:
        logger.error(f"Error downloading sentence transformer model: {e}")
        raise


def download_llm_model(model_name: str = "gpt2"):
    """Download LLM model."""
    try:
        logger.info(f"Downloading LLM model: {model_name}")
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Download tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        logger.info(f"Successfully downloaded LLM model: {model_name}")
        
    except Exception as e:
        logger.error(f"Error downloading LLM model: {e}")
        raise


def create_model_directories():
    """Create necessary model directories."""
    directories = [
        "models",
        "models/spacy",
        "models/transformers",
        "models/sentence_transformers",
        "models/nltk"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def main():
    """Main function to download all required models."""
    logging.basicConfig(level=logging.INFO)
    
    try:
        logger.info("Starting model download process...")
        
        # Create model directories
        create_model_directories()
        
        # Download spaCy model
        download_spacy_model()
        
        # Download NLTK data
        download_nltk_data()
        
        # Download sentence transformer model
        download_sentence_transformer_model()
        
        # Download LLM model
        download_llm_model()
        
        logger.info("All models downloaded successfully!")
        
    except Exception as e:
        logger.error(f"Error during model download: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
