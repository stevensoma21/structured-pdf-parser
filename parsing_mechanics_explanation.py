"""
Mechanical Parsing Explanation

Detailed breakdown of how the system mechanically parses PDF content to extract
logical modules, procedural steps, and actionable insights.
"""

import re
import fitz
from pathlib import Path

def show_raw_text_extraction(pdf_path):
    """Show the raw text extraction process."""
    print("=" * 80)
    print("STEP 1: RAW TEXT EXTRACTION")
    print("=" * 80)
    
    # Extract text using PyMuPDF
    doc = fitz.open(pdf_path)
    text = doc[0].get_text()
    doc.close()
    
    print(f"📄 PDF Text Length: {len(text)} characters")
    print(f"📄 First 200 characters:")
    print(f"   {text[:200]}...")
    print()
    
    return text

def show_module_parsing_mechanics(text):
    """Show how modules are parsed mechanically."""
    print("=" * 80)
    print("STEP 2: MODULE PARSING MECHANICS")
    print("=" * 80)
    
    # Pattern 1: Chapter headers
    print("🔍 PATTERN 1: Chapter Headers")
    chapter_pattern = r'Chapter \d+:\s*([^.!?]+)'
    chapter_match = re.search(chapter_pattern, text)
    
    if chapter_match:
        print(f"   Regex Pattern: {chapter_pattern}")
        print(f"   Match Found: '{chapter_match.group(0)}'")
        print(f"   Extracted Title: '{chapter_match.group(1).strip()}'")
        print(f"   Group 1: {chapter_match.group(1)}")
    else:
        print("   ❌ No chapter pattern match found")
    
    print()
    
    # Pattern 2: Section headers
    print("🔍 PATTERN 2: Section Headers")
    section_pattern = r'Types of Maintenance[^.!?]*[.!?]'
    section_match = re.search(section_pattern, text, re.IGNORECASE)
    
    if section_match:
        print(f"   Regex Pattern: {section_pattern}")
        print(f"   Match Found: '{section_match.group(0)}'")
    else:
        print("   ❌ No section pattern match found")
    
    print()
    
    return chapter_match, section_match

def show_procedural_step_parsing_mechanics(text):
    """Show how procedural steps are parsed mechanically."""
    print("=" * 80)
    print("STEP 3: PROCEDURAL STEP PARSING MECHANICS")
    print("=" * 80)
    
    # Define step patterns
    step_patterns = [
        r'Conduct scheduled inspections[^.!?]*[.!?]',
        r'Identify and resolve[^.!?]*[.!?]',
        r'Document and report[^.!?]*[.!?]',
        r'Adhere strictly[^.!?]*[.!?]',
    ]
    
    print("🔍 STEP PATTERN ANALYSIS:")
    for i, pattern in enumerate(step_patterns, 1):
        print(f"\n   Pattern {i}: {pattern}")
        
        # Search for pattern
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            step_text = match.group(0).strip()
            print(f"   ✅ Match Found: '{step_text}'")
            
            # Determine category
            category = "safety" if "adhere" in step_text.lower() else "general"
            print(f"   📋 Category: {category}")
            
            # Show pattern breakdown
            print(f"   🔍 Pattern Breakdown:")
            print(f"      - Start phrase: '{pattern.split('[')[0]}'")
            print(f"      - Capture group: '[^.!?]*[.!?]' (captures until sentence end)")
            print(f"      - Flags: re.IGNORECASE (case insensitive)")
        else:
            print(f"   ❌ No match found")
    
    print()

def show_evidence_tracking_mechanics():
    """Show how evidence tracking works."""
    print("=" * 80)
    print("STEP 4: EVIDENCE TRACKING MECHANICS")
    print("=" * 80)
    
    print("🔍 EVIDENCE TRACKING PROCESS:")
    print("   For each extracted element, the system tracks:")
    print("   • Page number: Extracted from PDF page index")
    print("   • Line numbers: Estimated based on pattern position")
    print("   • Source: 'rules' for regex-based extraction")
    print("   • Confidence: Calculated based on pattern specificity")
    
    print("\n📋 EXAMPLE EVIDENCE STRUCTURE:")
    evidence_example = {
        "page": 1,
        "lines": [13, 13],
        "source": "rules",
        "confidence": 0.99
    }
    print(f"   {evidence_example}")
    
    print("\n🔍 CONFIDENCE CALCULATION:")
    print("   • High confidence (0.99): Specific, unambiguous patterns")
    print("   • Medium confidence (0.85): General patterns with context")
    print("   • Low confidence (0.70): Fuzzy patterns requiring validation")
    
    print()

def show_taxonomy_extraction_mechanics():
    """Show how taxonomies are extracted."""
    print("=" * 80)
    print("STEP 5: TAXONOMY EXTRACTION MECHANICS")
    print("=" * 80)
    
    print("🔍 TAXONOMY EXTRACTION PROCESS:")
    print("   The system identifies structured knowledge from the text:")
    
    taxonomy_example = {
        "maintenance_types": [
            {"label": "preventive", "definition": "Routine checks and servicing."},
            {"label": "corrective", "definition": "Repair or replacement after malfunction."},
            {"label": "predictive", "definition": "Diagnostic checks to predict and prevent failures."}
        ]
    }
    
    print(f"\n📋 EXAMPLE TAXONOMY STRUCTURE:")
    print(f"   {taxonomy_example}")
    
    print("\n🔍 TAXONOMY IDENTIFICATION LOGIC:")
    print("   • Pattern: Look for numbered lists or structured definitions")
    print("   • Context: Identify the parent category (e.g., 'Types of Maintenance')")
    print("   • Extraction: Parse label-definition pairs")
    print("   • Validation: Ensure logical consistency")
    
    print()

def show_decision_flow_parsing_mechanics(text):
    """Show how decision flows are parsed."""
    print("=" * 80)
    print("STEP 6: DECISION FLOW PARSING MECHANICS")
    print("=" * 80)
    
    print("🔍 DECISION FLOW PATTERNS:")
    
    decision_patterns = [
        r'if[^.!?]*then[^.!?]*[.!?]',
        r'when[^.!?]*proceed[^.!?]*[.!?]',
        r'check[^.!?]*before[^.!?]*[.!?]',
    ]
    
    for i, pattern in enumerate(decision_patterns, 1):
        print(f"\n   Pattern {i}: {pattern}")
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            for j, match in enumerate(matches):
                print(f"   ✅ Match {j+1}: '{match}'")
        else:
            print(f"   ❌ No matches found")
    
    print("\n🔍 DECISION FLOW IDENTIFICATION LOGIC:")
    print("   • Conditional statements: 'if...then' patterns")
    print("   • Temporal sequences: 'when...proceed' patterns")
    print("   • Validation checks: 'check...before' patterns")
    print("   • Action triggers: Identify decision points in procedures")
    
    print()

def show_actionable_insights_extraction():
    """Show how actionable insights are extracted."""
    print("=" * 80)
    print("STEP 7: ACTIONABLE INSIGHTS EXTRACTION")
    print("=" * 80)
    
    print("🔍 ACTIONABLE INSIGHTS IDENTIFICATION:")
    
    insights = [
        "Safety-critical nature of aircraft maintenance",
        "Regulatory compliance requirements (FAA/EASA)",
        "Multi-system knowledge required (mechanical, hydraulic, electrical, avionics)",
        "Documentation and reporting requirements",
        "Three types of maintenance: preventive, corrective, predictive"
    ]
    
    print("   The system identifies insights through:")
    print("   • Keyword analysis: 'safety', 'critical', 'compliance'")
    print("   • Entity recognition: 'FAA', 'EASA', 'avionics'")
    print("   • Context analysis: Understanding document purpose")
    print("   • Pattern recognition: Identifying recurring themes")
    
    print(f"\n📋 EXTRACTED INSIGHTS:")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight}")
    
    print()

def show_complete_parsing_pipeline(pdf_path):
    """Show the complete parsing pipeline step by step."""
    print("🚀 COMPLETE MECHANICAL PARSING PIPELINE")
    print("=" * 80)
    
    # Step 1: Raw text extraction
    text = show_raw_text_extraction(pdf_path)
    
    # Step 2: Module parsing
    chapter_match, section_match = show_module_parsing_mechanics(text)
    
    # Step 3: Procedural step parsing
    show_procedural_step_parsing_mechanics(text)
    
    # Step 4: Evidence tracking
    show_evidence_tracking_mechanics()
    
    # Step 5: Taxonomy extraction
    show_taxonomy_extraction_mechanics()
    
    # Step 6: Decision flow parsing
    show_decision_flow_parsing_mechanics(text)
    
    # Step 7: Actionable insights
    show_actionable_insights_extraction()
    
    print("=" * 80)
    print("🎯 PARSING MECHANICS SUMMARY")
    print("=" * 80)
    
    print("📋 MECHANICAL PROCESS OVERVIEW:")
    print("   1. PDF → Text: PyMuPDF extracts raw text")
    print("   2. Text → Patterns: Regex patterns identify structured content")
    print("   3. Patterns → Elements: Extract modules, steps, flows")
    print("   4. Elements → Evidence: Track source and confidence")
    print("   5. Elements → Schema: Format into expected JSON structure")
    print("   6. Schema → Insights: Generate actionable intelligence")
    
    print("\n🔧 KEY TECHNICAL COMPONENTS:")
    print("   • Regular Expressions: Pattern matching for content extraction")
    print("   • Text Analysis: Understanding document structure")
    print("   • Evidence Tracking: Source attribution and confidence scoring")
    print("   • Schema Validation: Ensuring output format compliance")
    print("   • Taxonomy Building: Structured knowledge representation")
    
    print("\n⚡ AUTOMATION BENEFITS:")
    print("   • Consistent extraction across documents")
    print("   • Scalable processing of large document sets")
    print("   • Structured output for downstream automation")
    print("   • Evidence-based auditability")
    print("   • Confidence scoring for quality assessment")

def main():
    """Run the complete parsing mechanics explanation."""
    pdf_path = 'data/aircraft_maintenance_chapter.pdf'
    
    if Path(pdf_path).exists():
        show_complete_parsing_pipeline(pdf_path)
    else:
        print(f"❌ PDF file not found: {pdf_path}")

if __name__ == "__main__":
    main()
