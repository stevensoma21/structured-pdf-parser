"""
NLP Processing Module

Handles named entity recognition, dependency parsing, semantic search, and text classification.
"""

import logging
from typing import List, Dict, Optional, Tuple
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Handles natural language processing tasks."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize NLP processor with configuration."""
        self.config = config or {}
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # Initialize sentence transformer
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Could not load sentence transformer: {e}")
            self.sentence_model = None
            
        # Initialize NLTK components
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            logger.warning("NLTK data not found. Downloading...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Technical domain keywords
        self.technical_keywords = {
            'safety': ['safety', 'secure', 'danger', 'hazard', 'warning', 'caution'],
            'maintenance': ['maintenance', 'repair', 'service', 'inspect', 'check'],
            'procedure': ['procedure', 'step', 'process', 'method', 'protocol'],
            'equipment': ['equipment', 'tool', 'device', 'instrument', 'apparatus'],
            'measurement': ['measure', 'calibrate', 'test', 'verify', 'validate']
        }
        
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities with their types and positions
        """
        if not self.nlp:
            return []
            
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'description': spacy.explain(ent.label_)
            })
            
        return entities
    
    def extract_technical_entities(self, text: str) -> List[Dict]:
        """
        Extract technical domain-specific entities.
        
        Args:
            text: Input text
            
        Returns:
            List of technical entities
        """
        technical_entities = []
        
        # Extract equipment and tools
        equipment_patterns = [
            r'\b[A-Z][A-Z0-9\-\s]{2,}\b',  # All caps identifiers
            r'\b\d{1,3}\.\d{1,3}\b',       # Version numbers
            r'\b[A-Z]{2,}\d{2,}\b',        # Model numbers
        ]
        
        for pattern in equipment_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                technical_entities.append({
                    'text': match.group(),
                    'type': 'equipment_identifier',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8
                })
        
        # Extract measurements and units
        measurement_patterns = [
            r'\b\d+\.?\d*\s*(?:mm|cm|m|km|in|ft|yd|psi|bar|pa|kpa|mpa)\b',
            r'\b\d+\.?\d*\s*(?:volts?|v|amperes?|a|watts?|w|ohms?|Ω)\b',
            r'\b\d+\.?\d*\s*(?:degrees?|°|fahrenheit|f|celsius|c|kelvin|k)\b',
        ]
        
        for pattern in measurement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                technical_entities.append({
                    'text': match.group(),
                    'type': 'measurement',
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.9
                })
        
        return technical_entities
    
    def extract_procedural_steps(self, text: str) -> List[Dict]:
        """
        Extract procedural steps from text.
        
        Args:
            text: Input text
            
        Returns:
            List of procedural steps
        """
        steps = []
        
        # Common step patterns
        step_patterns = [
            r'\b(?:step|procedure|process)\s+\d+[\.:]?\s*([^.!?]+[.!?])',
            r'\b\d+[\.)]\s*([^.!?]+[.!?])',
            r'\b(?:first|second|third|fourth|fifth|next|then|finally)\s+([^.!?]+[.!?])',
        ]
        
        for pattern in step_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                step_text = match.group(1) if match.groups() else match.group()
                step_text = step_text.strip()
                
                if len(step_text) > 10:  # Minimum step length
                    steps.append({
                        'text': step_text,
                        'pattern': pattern,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.85
                    })
        
        # Remove duplicates and sort by position
        unique_steps = []
        seen_texts = set()
        
        for step in sorted(steps, key=lambda x: x['start']):
            normalized_text = re.sub(r'\s+', ' ', step['text'].lower())
            if normalized_text not in seen_texts:
                unique_steps.append(step)
                seen_texts.add(normalized_text)
        
        return unique_steps
    
    def extract_modules(self, text: str) -> List[Dict]:
        """
        Extract logical modules from text.
        
        Args:
            text: Input text
            
        Returns:
            List of identified modules
        """
        modules = []
        
        # Module header patterns
        module_patterns = [
            r'\n\s*(\d+\.\s*[A-Z][^.!?]*?)(?=\n)',
            r'\n\s*([A-Z][A-Z\s]{3,})(?=\n)',
            r'\n\s*([A-Z][a-z]+[A-Z][a-z]*\s*[A-Za-z]*)(?=\n)',
        ]
        
        for pattern in module_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                module_title = match.group(1).strip()
                
                # Find module content (until next module or end)
                start_pos = match.end()
                next_match = None
                
                for p in module_patterns:
                    next_m = re.search(p, text[start_pos:])
                    if next_m and (next_match is None or next_m.start() < next_match.start()):
                        next_match = next_m
                
                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = len(text)
                
                module_content = text[start_pos:end_pos].strip()
                
                if len(module_content) > 50:  # Minimum module content
                    modules.append({
                        'title': module_title,
                        'content': module_content,
                        'start': start_pos,
                        'end': end_pos,
                        'confidence': 0.8
                    })
        
        return modules
    
    def perform_dependency_parsing(self, text: str) -> List[Dict]:
        """
        Perform dependency parsing on text.
        
        Args:
            text: Input text
            
        Returns:
            List of dependency relationships
        """
        if not self.nlp:
            return []
            
        doc = self.nlp(text)
        dependencies = []
        
        for token in doc:
            dependencies.append({
                'text': token.text,
                'dep': token.dep_,
                'head': token.head.text,
                'pos': token.pos_,
                'lemma': token.lemma_
            })
        
        return dependencies
    
    def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """
        Perform semantic search using sentence transformers.
        
        Args:
            query: Search query
            documents: List of documents to search
            top_k: Number of top results to return
            
        Returns:
            List of search results with similarity scores
        """
        if not self.sentence_model:
            # Fallback to TF-IDF
            return self._tfidf_search(query, documents, top_k)
        
        # Encode query and documents
        query_embedding = self.sentence_model.encode([query])
        doc_embeddings = self.sentence_model.encode(documents)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'document': documents[idx],
                'similarity': float(similarities[idx]),
                'rank': len(results) + 1
            })
        
        return results
    
    def _tfidf_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """Fallback TF-IDF search when sentence transformers are not available."""
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Add query to documents for vectorization
        all_texts = documents + [query]
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate similarities
        query_vector = tfidf_matrix[-1]
        doc_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(query_vector, doc_vectors)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'document': documents[idx],
                'similarity': float(similarities[idx]),
                'rank': len(results) + 1
            })
        
        return results
    
    def classify_text(self, text: str) -> Dict:
        """
        Classify text into technical categories.
        
        Args:
            text: Input text
            
        Returns:
            Classification results with confidence scores
        """
        classifications = {}
        
        # Count technical keywords
        text_lower = text.lower()
        
        for category, keywords in self.technical_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                classifications[category] = {
                    'confidence': min(count / len(keywords), 1.0),
                    'keyword_count': count,
                    'keywords_found': [k for k in keywords if k in text_lower]
                }
        
        # Determine primary category
        if classifications:
            primary_category = max(classifications.items(), key=lambda x: x[1]['confidence'])
            classifications['primary_category'] = primary_category[0]
        
        return classifications
    
    def extract_decision_points(self, text: str) -> List[Dict]:
        """
        Extract decision points and conditional statements.
        
        Args:
            text: Input text
            
        Returns:
            List of decision points
        """
        decision_points = []
        
        # Decision patterns
        decision_patterns = [
            r'\b(?:if|when|whereas|while)\s+([^.!?]+?)\s+(?:then|proceed|continue|stop|halt)',
            r'\b(?:check|verify|confirm)\s+([^.!?]+?)\s+(?:before|prior|after)',
            r'\b(?:in case of|in the event of|should)\s+([^.!?]+?)\s+(?:then|proceed)',
        ]
        
        for pattern in decision_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                condition = match.group(1).strip()
                decision_points.append({
                    'condition': condition,
                    'full_text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8
                })
        
        return decision_points
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better NLP processing.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Tokenize and lemmatize
        tokens = word_tokenize(text.lower())
        
        # Remove stop words and lemmatize
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and token.isalnum():
                processed_tokens.append(self.lemmatizer.lemmatize(token))
        
        return ' '.join(processed_tokens)
