"""
Full Pipeline Runner

Runs the improved ML pipeline on all sample PDF files and generates comprehensive output.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from improved_pipeline import create_improved_structured_output

def process_pdf_file(pdf_path, output_dir):
    """Process a single PDF file and save results."""
    print(f"\n{'='*60}")
    print(f"PROCESSING: {Path(pdf_path).name}")
    print(f"{'='*60}")
    
    try:
        # Process the PDF
        output = create_improved_structured_output(pdf_path)
        
        # Create output filename
        base_name = Path(pdf_path).stem
        output_file = Path(output_dir) / f"{base_name}_output.json"
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        # Print summary
        print(f"✅ Processing completed successfully!")
        print(f"   📄 File: {Path(pdf_path).name}")
        print(f"   📊 Modules: {len(output['modules'])}")
        print(f"   📋 Steps: {len(output['procedural_steps'])}")
        print(f"   🎯 Decisions: {len(output['decision_points'])}")
        print(f"   🔧 Equipment: {len(output['equipment'])}")
        print(f"   📈 Confidence: {output['document_info']['confidence_score']:.1%}")
        print(f"   💾 Saved to: {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return None

def create_summary_report(outputs, output_dir):
    """Create a summary report of all processing results."""
    summary = {
        "processing_summary": {
            "timestamp": datetime.now().isoformat(),
            "total_files_processed": len(outputs),
            "successful_extractions": len([o for o in outputs if o is not None]),
            "failed_extractions": len([o for o in outputs if o is None])
        },
        "file_results": [],
        "overall_statistics": {
            "total_modules": 0,
            "total_steps": 0,
            "total_decisions": 0,
            "total_equipment": 0,
            "average_confidence": 0.0
        }
    }
    
    successful_outputs = []
    for output_file in outputs:
        if output_file and output_file.exists():
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                successful_outputs.append(data)
                
                # Add file result
                summary["file_results"].append({
                    "filename": data["document_info"]["filename"],
                    "modules": len(data["modules"]),
                    "procedural_steps": len(data["procedural_steps"]),
                    "decision_points": len(data["decision_points"]),
                    "equipment": len(data["equipment"]),
                    "confidence": data["document_info"]["confidence_score"],
                    "output_file": str(output_file)
                })
                
                # Update statistics
                summary["overall_statistics"]["total_modules"] += len(data["modules"])
                summary["overall_statistics"]["total_steps"] += len(data["procedural_steps"])
                summary["overall_statistics"]["total_decisions"] += len(data["decision_points"])
                summary["overall_statistics"]["total_equipment"] += len(data["equipment"])
                
            except Exception as e:
                print(f"Warning: Could not read {output_file}: {e}")
    
    # Calculate average confidence
    if successful_outputs:
        avg_confidence = sum(o["document_info"]["confidence_score"] for o in successful_outputs) / len(successful_outputs)
        summary["overall_statistics"]["average_confidence"] = avg_confidence
    
    # Save summary
    summary_file = Path(output_dir) / "processing_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary, summary_file

def main():
    """Run the full pipeline on all sample PDFs."""
    print("🚀 FULL ML PIPELINE EXECUTION")
    print("=" * 80)
    
    # Setup
    data_dir = Path("data")
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Find all PDF files
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in data/ directory")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files to process:")
    for pdf_file in pdf_files:
        print(f"   • {pdf_file.name}")
    
    # Process each PDF
    outputs = []
    for pdf_file in pdf_files:
        output_file = process_pdf_file(str(pdf_file), output_dir)
        outputs.append(output_file)
    
    # Create summary report
    print(f"\n{'='*60}")
    print("GENERATING SUMMARY REPORT")
    print(f"{'='*60}")
    
    summary, summary_file = create_summary_report(outputs, output_dir)
    
    # Print final summary
    print(f"\n📊 FINAL PROCESSING SUMMARY:")
    print(f"   📄 Total files processed: {summary['processing_summary']['total_files_processed']}")
    print(f"   ✅ Successful extractions: {summary['processing_summary']['successful_extractions']}")
    print(f"   ❌ Failed extractions: {summary['processing_summary']['failed_extractions']}")
    print(f"   📋 Total modules identified: {summary['overall_statistics']['total_modules']}")
    print(f"   📋 Total procedural steps: {summary['overall_statistics']['total_steps']}")
    print(f"   🎯 Total decision points: {summary['overall_statistics']['total_decisions']}")
    print(f"   🔧 Total equipment items: {summary['overall_statistics']['total_equipment']}")
    print(f"   📈 Average confidence: {summary['overall_statistics']['average_confidence']:.1%}")
    
    print(f"\n📁 OUTPUT FILES:")
    for result in summary["file_results"]:
        print(f"   • {result['filename']} → {result['output_file']}")
        print(f"     Modules: {result['modules']}, Steps: {result['procedural_steps']}, Confidence: {result['confidence']:.1%}")
    
    print(f"\n💾 Summary report saved to: {summary_file}")
    
    print(f"\n🎉 PIPELINE EXECUTION COMPLETED!")
    print(f"   All results saved in: {output_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
