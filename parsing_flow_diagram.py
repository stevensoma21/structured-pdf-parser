"""
Parsing Flow Diagram

Visual representation of how the mechanical parsing process works.
"""

def print_parsing_flow_diagram():
    """Print a visual diagram of the parsing flow."""
    
    print("🔍 MECHANICAL PARSING FLOW DIAGRAM")
    print("=" * 80)
    
    print("""
📄 INPUT: PDF Document
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 1: TEXT EXTRACTION                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PyMuPDF (fitz) extracts raw text from PDF          │   │
│  │ • Handles text-based and scanned PDFs              │   │
│  │ • Preserves text structure and formatting          │   │
│  │ • Output: 991 characters of raw text               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 2: PATTERN MATCHING                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Regular Expression Patterns:                        │   │
│  │                                                     │   │
│  │ 🔍 Module Patterns:                                │   │
│  │    r'Chapter \\d+:\\s*([^.!?]+)'                    │   │
│  │    r'Types of Maintenance[^.!?]*[.!?]'             │   │
│  │                                                     │   │
│  │ 🔍 Step Patterns:                                   │   │
│  │    r'Conduct scheduled inspections[^.!?]*[.!?]'    │   │
│  │    r'Identify and resolve[^.!?]*[.!?]'             │   │
│  │    r'Document and report[^.!?]*[.!?]'              │   │
│  │    r'Adhere strictly[^.!?]*[.!?]'                  │   │
│  │                                                     │   │
│  │ 🔍 Flow Patterns:                                   │   │
│  │    r'if[^.!?]*then[^.!?]*[.!?]'                    │   │
│  │    r'when[^.!?]*proceed[^.!?]*[.!?]'               │   │
│  │    r'check[^.!?]*before[^.!?]*[.!?]'               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 3: ELEMENT EXTRACTION               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Extracted Elements:                                 │   │
│  │                                                     │   │
│  │ 📋 MODULES (2 found):                               │   │
│  │    • mod_intro: "Introduction to Aircraft Maintenance" │   │
│  │    • mod_types: "Types of Maintenance"              │   │
│  │                                                     │   │
│  │ 📋 STEPS (4 found):                                 │   │
│  │    • s-001: "Conduct scheduled inspections..."      │   │
│  │    • s-002: "Identify and resolve..."               │   │
│  │    • s-003: "Document and report..."                │   │
│  │    • s-004: "Adhere strictly..."                    │   │
│  │                                                     │   │
│  │ 🎯 FLOWS (0 found):                                 │   │
│  │    • No decision flows in this document             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 4: EVIDENCE TRACKING                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ For each extracted element:                         │   │
│  │                                                     │   │
│  │ 📍 Evidence Structure:                              │   │
│  │    {                                                 │   │
│  │      "page": 1,                                     │   │
│  │      "lines": [13, 13],                             │   │
│  │      "source": "rules",                             │   │
│  │      "confidence": 0.99                             │   │
│  │    }                                                │   │
│  │                                                     │   │
│  │ 🎯 Confidence Scoring:                              │   │
│  │    • 0.99: Specific, unambiguous patterns          │   │
│  │    • 0.85: General patterns with context           │   │
│  │    • 0.70: Fuzzy patterns requiring validation     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 5: TAXONOMY BUILDING                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Structured Knowledge Extraction:                    │   │
│  │                                                     │   │
│  │ 📚 Maintenance Types:                               │   │
│  │    • preventive: "Routine checks and servicing"     │   │
│  │    • corrective: "Repair or replacement..."         │   │
│  │    • predictive: "Diagnostic checks..."             │   │
│  │                                                     │   │
│  │ 🏷️  Categorization:                                 │   │
│  │    • general: Standard procedural steps             │   │
│  │    • safety: Safety-critical procedures             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 6: SCHEMA FORMATTING                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ JSON Schema Structure:                              │   │
│  │                                                     │   │
│  │ {                                                   │   │
│  │   "doc_id": "aircraft_maintenance_chapter",        │   │
│  │   "title": "Chapter 1: Introduction...",           │   │
│  │   "modules": [                                      │   │
│  │     {                                               │   │
│  │       "module_id": "mod_intro",                    │   │
│  │       "heading": "...",                            │   │
│  │       "steps": [                                   │   │
│  │         {                                           │   │
│  │           "step_id": "s-001",                      │   │
│  │           "text": "...",                           │   │
│  │           "category": "general",                   │   │
│  │           "evidence": {...},                       │   │
│  │           "confidence": 0.99                       │   │
│  │         }                                           │   │
│  │       ]                                             │   │
│  │     }                                               │   │
│  │   ],                                                │   │
│  │   "metadata": {...}                                 │   │
│  │ }                                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    STEP 7: INSIGHT GENERATION               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Actionable Insights:                                │   │
│  │                                                     │   │
│  │ ⚡ Safety-critical nature of aircraft maintenance   │   │
│  │ ⚡ Regulatory compliance requirements (FAA/EASA)    │   │
│  │ ⚡ Multi-system knowledge required                   │   │
│  │ ⚡ Documentation and reporting requirements          │   │
│  │ ⚡ Three types of maintenance identified            │   │
│  │                                                     │   │
│  │ 🔍 Insight Sources:                                 │   │
│  │    • Keyword analysis                               │   │
│  │    • Entity recognition                             │   │
│  │    • Context analysis                               │   │
│  │    • Pattern recognition                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
📄 OUTPUT: Structured JSON with Modules, Steps, and Insights
""")

def print_regex_pattern_explanation():
    """Explain the regex patterns in detail."""
    
    print("\n🔍 REGEX PATTERN BREAKDOWN")
    print("=" * 80)
    
    patterns = [
        {
            "name": "Chapter Header",
            "pattern": r'Chapter \d+:\s*([^.!?]+)',
            "explanation": [
                "Chapter \\d+: - Matches 'Chapter' followed by digits and colon",
                "\\s* - Matches optional whitespace",
                "([^.!?]+) - Captures text until sentence ending punctuation",
                "Group 1: Extracted chapter title"
            ]
        },
        {
            "name": "Procedural Step",
            "pattern": r'Conduct scheduled inspections[^.!?]*[.!?]',
            "explanation": [
                "Conduct scheduled inspections - Exact phrase match",
                "[^.!?]* - Matches any characters except sentence endings",
                "[.!?] - Matches sentence ending punctuation",
                "Result: Complete sentence from start phrase to end"
            ]
        },
        {
            "name": "Decision Flow",
            "pattern": r'if[^.!?]*then[^.!?]*[.!?]',
            "explanation": [
                "if - Matches conditional 'if'",
                "[^.!?]* - Matches condition text",
                "then - Matches 'then' connector",
                "[^.!?]* - Matches action text",
                "[.!?] - Matches sentence ending"
            ]
        }
    ]
    
    for pattern_info in patterns:
        print(f"\n📋 {pattern_info['name']}:")
        print(f"   Pattern: {pattern_info['pattern']}")
        print(f"   Explanation:")
        for explanation in pattern_info['explanation']:
            print(f"      • {explanation}")

def print_automation_benefits():
    """Show the benefits of this mechanical approach."""
    
    print("\n⚡ AUTOMATION BENEFITS")
    print("=" * 80)
    
    benefits = [
        {
            "category": "Consistency",
            "benefits": [
                "Same patterns applied across all documents",
                "Standardized output format",
                "Predictable extraction results"
            ]
        },
        {
            "category": "Scalability",
            "benefits": [
                "Process thousands of documents automatically",
                "No manual intervention required",
                "Parallel processing capability"
            ]
        },
        {
            "category": "Auditability",
            "benefits": [
                "Evidence tracking for each extraction",
                "Confidence scoring for quality assessment",
                "Source attribution for compliance"
            ]
        },
        {
            "category": "Integration",
            "benefits": [
                "Structured JSON for downstream systems",
                "API-ready output format",
                "Database-friendly schema"
            ]
        }
    ]
    
    for benefit_group in benefits:
        print(f"\n🔧 {benefit_group['category']}:")
        for benefit in benefit_group['benefits']:
            print(f"   • {benefit}")

def main():
    """Run the complete parsing flow explanation."""
    print_parsing_flow_diagram()
    print_regex_pattern_explanation()
    print_automation_benefits()
    
    print("\n" + "=" * 80)
    print("🎯 MECHANICAL PARSING SUMMARY")
    print("=" * 80)
    print("The system uses a systematic, rule-based approach to:")
    print("1. Extract raw text from PDFs using PyMuPDF")
    print("2. Apply regex patterns to identify structured content")
    print("3. Categorize and organize extracted elements")
    print("4. Track evidence and confidence for each extraction")
    print("5. Format results into standardized JSON schema")
    print("6. Generate actionable insights from extracted data")
    print("\nThis mechanical approach ensures consistency, scalability,")
    print("and reliability in converting unstructured documents to")
    print("structured, actionable data for automation systems.")

if __name__ == "__main__":
    main()
