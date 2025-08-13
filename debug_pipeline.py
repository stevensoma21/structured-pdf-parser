"""
Debug Pipeline Script

Tests each component of the ML pipeline step by step to identify issues.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_extraction():
    """Test PDF text extraction."""
    print("=" * 60)
    print("TESTING PDF EXTRACTION")
    print("=" * 60)
    
    try:
        import fitz
        doc = fitz.open('data/aircraft_maintenance_chapter.pdf')
        text = doc[0].get_text()
        doc.close()
        
        print(f"✅ PDF extraction successful")
        print(f"   Text length: {len(text)} characters")
        print(f"   First 100 chars: {text[:100]}...")
        print(f"   Contains 'maintenance': {'maintenance' in text.lower()}")
        print(f"   Contains 'responsibilities': {'responsibilities' in text.lower()}")
        
        return text
        
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return None

def test_nlp_processing(text):
    """Test NLP processing."""
    print("\n" + "=" * 60)
    print("TESTING NLP PROCESSING")
    print("=" * 60)
    
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text)
        
        print(f"✅ NLP processing successful")
        print(f"   Sentences: {len(list(doc.sents))}")
        print(f"   Tokens: {len(doc)}")
        print(f"   Entities: {len(doc.ents)}")
        
        # Test entity extraction
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"   Sample entities: {entities[:5]}")
        
        return doc
        
    except Exception as e:
        print(f"❌ NLP processing failed: {e}")
        return None

def test_pattern_matching(text):
    """Test pattern matching for procedural steps."""
    print("\n" + "=" * 60)
    print("TESTING PATTERN MATCHING")
    print("=" * 60)
    
    import re
    
    # Test various patterns
    patterns = [
        r'\b(?:step|procedure)\s+\d+[\.:]?\s*([^.!?]+[.!?])',
        r'\b(\d+)[\.)]\s*([^.!?]+[.!?])',
        r'\b(?:first|second|third|fourth|fifth|next|then|finally)\s+([^.!?]+[.!?])',
        r'\n\s*(\d+\.\s*[A-Z][^.!?]*?)(?=\n)',
        r'\n\s*([A-Z][A-Z\s]{3,})(?=\n)',
        r'\n\s*([A-Z][a-z]+[A-Z][a-z]*\s*[A-Za-z]*)(?=\n)',
    ]
    
    for i, pattern in enumerate(patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"   Pattern {i+1}: {len(matches)} matches")
        if matches:
            print(f"      Sample: {matches[0] if isinstance(matches[0], str) else matches[0][0]}")
    
    # Test specific patterns for the aircraft maintenance content
    specific_patterns = [
        r'Conduct scheduled inspections[^.!?]*[.!?]',
        r'Identify and resolve[^.!?]*[.!?]',
        r'Document and report[^.!?]*[.!?]',
        r'Adhere strictly[^.!?]*[.!?]',
    ]
    
    print(f"\n   Testing specific maintenance patterns:")
    for pattern in specific_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"      '{pattern[:30]}...': {len(matches)} matches")
        if matches:
            print(f"         Found: {matches[0][:60]}...")

def test_llm_availability():
    """Test LLM model availability."""
    print("\n" + "=" * 60)
    print("TESTING LLM AVAILABILITY")
    print("=" * 60)
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        tokenizer = AutoTokenizer.from_pretrained('gpt2')
        print(f"✅ GPT-2 tokenizer loaded successfully")
        
        # Try to load model (this might take time)
        print(f"   Attempting to load GPT-2 model...")
        model = AutoModelForCausalLM.from_pretrained('gpt2', torch_dtype='auto', low_cpu_mem_usage=True)
        print(f"✅ GPT-2 model loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM loading failed: {e}")
        return False

def test_simple_extraction():
    """Test simple extraction without full pipeline."""
    print("\n" + "=" * 60)
    print("TESTING SIMPLE EXTRACTION")
    print("=" * 60)
    
    try:
        # Extract text
        import fitz
        doc = fitz.open('data/aircraft_maintenance_chapter.pdf')
        text = doc[0].get_text()
        doc.close()
        
        # Simple pattern matching for modules
        import re
        
        # Find module headers
        module_patterns = [
            r'Chapter \d+:\s*([^.!?]+)',
            r'([A-Z][A-Z\s]{3,})',
            r'([A-Z][a-z]+[A-Z][a-z]*\s*[A-Za-z]*)',
        ]
        
        modules = []
        for pattern in module_patterns:
            matches = re.findall(pattern, text)
            modules.extend(matches)
        
        # Find procedural steps
        step_patterns = [
            r'Conduct scheduled inspections[^.!?]*[.!?]',
            r'Identify and resolve[^.!?]*[.!?]',
            r'Document and report[^.!?]*[.!?]',
            r'Adhere strictly[^.!?]*[.!?]',
            r'Preventive Maintenance[^.!?]*[.!?]',
            r'Corrective Maintenance[^.!?]*[.!?]',
            r'Predictive Maintenance[^.!?]*[.!?]',
        ]
        
        steps = []
        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            steps.extend(matches)
        
        print(f"✅ Simple extraction results:")
        print(f"   Modules found: {len(modules)}")
        for i, module in enumerate(modules[:3]):
            print(f"      {i+1}. {module}")
        
        print(f"   Steps found: {len(steps)}")
        for i, step in enumerate(steps[:3]):
            print(f"      {i+1}. {step[:60]}...")
        
        return len(modules) > 0 and len(steps) > 0
        
    except Exception as e:
        print(f"❌ Simple extraction failed: {e}")
        return False

def main():
    """Run all tests."""
    print("DEBUGGING ML PIPELINE COMPONENTS")
    print("=" * 60)
    
    # Test 1: PDF Extraction
    text = test_pdf_extraction()
    if not text:
        print("❌ Cannot proceed without PDF text")
        return
    
    # Test 2: NLP Processing
    doc = test_nlp_processing(text)
    
    # Test 3: Pattern Matching
    test_pattern_matching(text)
    
    # Test 4: LLM Availability
    llm_available = test_llm_availability()
    
    # Test 5: Simple Extraction
    extraction_success = test_simple_extraction()
    
    # Summary
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    print(f"✅ PDF Extraction: Working")
    print(f"✅ NLP Processing: {'Working' if doc else 'Failed'}")
    print(f"✅ LLM Availability: {'Available' if llm_available else 'Not Available'}")
    print(f"✅ Simple Extraction: {'Working' if extraction_success else 'Failed'}")
    
    if extraction_success:
        print("\n🎯 The issue is likely in the pipeline orchestration, not the individual components.")
        print("   The simple extraction shows that content can be extracted from the PDF.")
    else:
        print("\n❌ The issue is in the basic extraction patterns.")
        print("   Need to improve pattern matching for this specific document format.")

if __name__ == "__main__":
    main()
