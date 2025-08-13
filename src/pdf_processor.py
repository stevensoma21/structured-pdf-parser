"""
PDF Processing Module

Handles extraction, normalization, and cleaning of text from PDF documents.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import pytesseract
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF document processing and text extraction."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize PDF processor with configuration."""
        self.config = config or {}
        self.ocr_enabled = self.config.get('ocr_enabled', True)
        self.min_confidence = self.config.get('min_confidence', 0.7)
        
    def extract_text(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF document using multiple methods.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Try different extraction methods
        text_data = {
            'filename': pdf_path.name,
            'pages': [],
            'full_text': '',
            'metadata': {},
            'extraction_method': 'combined'
        }
        
        try:
            # Method 1: PyMuPDF (fastest, good for text-based PDFs)
            text_data = self._extract_with_pymupdf(pdf_path)
            
            # Method 2: PDFPlumber (better for complex layouts)
            if not text_data['full_text'].strip():
                text_data = self._extract_with_pdfplumber(pdf_path)
                
            # Method 3: OCR (for scanned documents)
            if not text_data['full_text'].strip() and self.ocr_enabled:
                text_data = self._extract_with_ocr(pdf_path)
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
            
        # Clean and normalize text
        text_data = self._clean_text(text_data)
        
        logger.info(f"Extracted {len(text_data['full_text'])} characters from {pdf_path}")
        return text_data
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> Dict:
        """Extract text using PyMuPDF."""
        doc = fitz.open(pdf_path)
        pages = []
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages.append({
                'page_number': page_num + 1,
                'text': text,
                'bbox': page.rect,
                'confidence': 0.9
            })
            full_text += text + "\n"
            
        metadata = doc.metadata
        
        doc.close()
        
        return {
            'filename': pdf_path.name,
            'pages': pages,
            'full_text': full_text,
            'metadata': metadata,
            'extraction_method': 'pymupdf'
        }
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> Dict:
        """Extract text using PDFPlumber."""
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            full_text = ""
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append({
                    'page_number': page_num + 1,
                    'text': text,
                    'bbox': page.bbox if page.bbox else None,
                    'confidence': 0.85
                })
                full_text += text + "\n"
                
            metadata = pdf.metadata
            
        return {
            'filename': pdf_path.name,
            'pages': pages,
            'full_text': full_text,
            'metadata': metadata,
            'extraction_method': 'pdfplumber'
        }
    
    def _extract_with_ocr(self, pdf_path: Path) -> Dict:
        """Extract text using OCR for scanned documents."""
        doc = fitz.open(pdf_path)
        pages = []
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Preprocess image for better OCR
            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR extraction
            text = pytesseract.image_to_string(binary, config='--psm 6')
            
            pages.append({
                'page_number': page_num + 1,
                'text': text,
                'bbox': page.rect,
                'confidence': 0.7  # Lower confidence for OCR
            })
            full_text += text + "\n"
            
        metadata = doc.metadata
        doc.close()
        
        return {
            'filename': pdf_path.name,
            'pages': pages,
            'full_text': full_text,
            'metadata': metadata,
            'extraction_method': 'ocr'
        }
    
    def _clean_text(self, text_data: Dict) -> Dict:
        """Clean and normalize extracted text."""
        full_text = text_data['full_text']
        
        # Remove excessive whitespace
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # Remove special characters but keep important punctuation
        full_text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', full_text)
        
        # Normalize line breaks
        full_text = re.sub(r'\n+', '\n', full_text)
        
        # Remove page numbers and headers/footers
        full_text = re.sub(r'^\d+\s*$', '', full_text, flags=re.MULTILINE)
        
        # Clean individual pages
        for page in text_data['pages']:
            page['text'] = re.sub(r'\s+', ' ', page['text'])
            page['text'] = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', ' ', page['text'])
        
        text_data['full_text'] = full_text.strip()
        return text_data
    
    def segment_document(self, text_data: Dict) -> Dict:
        """
        Segment document into logical sections.
        
        Args:
            text_data: Extracted text data
            
        Returns:
            Dictionary with segmented sections
        """
        text = text_data['full_text']
        sections = []
        
        # Split by common section markers
        section_patterns = [
            r'\n\s*\d+\.\s*[A-Z][^.]*\n',  # Numbered sections
            r'\n\s*[A-Z][A-Z\s]{3,}\n',    # ALL CAPS headers
            r'\n\s*[A-Z][a-z]+[A-Z][a-z]*\s*\n',  # TitleCase headers
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start = match.start()
                end = match.end()
                
                # Find next section or end of document
                next_match = re.search(pattern, text[end:])
                if next_match:
                    section_end = end + next_match.start()
                else:
                    section_end = len(text)
                
                section_text = text[start:section_end].strip()
                if len(section_text) > 50:  # Minimum section length
                    sections.append({
                        'title': match.group().strip(),
                        'content': section_text,
                        'start_pos': start,
                        'end_pos': section_end
                    })
        
        text_data['sections'] = sections
        return text_data
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """
        Extract tables from PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of extracted tables
        """
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    
                    for table_num, table in enumerate(page_tables):
                        if table and len(table) > 1:  # At least header and one row
                            tables.append({
                                'page': page_num + 1,
                                'table_number': table_num + 1,
                                'data': table,
                                'rows': len(table),
                                'columns': len(table[0]) if table else 0
                            })
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
            
        return tables
