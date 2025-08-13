# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- 4GB+ RAM (for working pipeline)
- Docker (optional, for containerized deployment)

## Working Pipeline

This project includes a **working pipeline** (`final_proper_pipeline.py`) that produces rich, structured JSON output without dependency issues. This is the recommended approach for immediate use.

**Key Features:**
- No NumPy compatibility issues
- Rich extraction of modules, steps, and taxonomies
- 99% confidence scores
- Schema-compliant JSON output
- Handles multiple PDF files
- Detailed evidence tracking
- No external model downloads required

**Quick Test:**
```bash
python final_proper_pipeline.py
```

## Installation

### Option 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/stevensoma21/structured-pdf-parser
   cd structured-pdf-parser
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ready to use!** No model downloads required.

### Option 2: Docker Installation

1. **Build the container**
   ```bash
   docker build -t structured-pdf-parser .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 -v $(pwd)/data:/app/data structured-pdf-parser
   ```

## Basic Usage

### Command Line Interface

**Recommended: Use the working pipeline**

1. **Process all PDF files in the data directory**
   ```bash
   python final_proper_pipeline.py
   ```

2. **View detailed results**
   ```bash
   python view_results.py
   ```

3. **Process a single PDF file**
   ```bash
   python -c "
   from final_proper_pipeline import process_pdf_file
   process_pdf_file('data/aircraft_maintenance_chapter.pdf', 'results')
   "
   ```

### Python API

**Recommended: Use the working pipeline**

```python
from final_proper_pipeline import process_pdf_file

# Process a document
output = process_pdf_file("data/aircraft_maintenance_chapter.pdf", "results")

# Access results
print(f"Document ID: {output['doc_id']}")
print(f"Title: {output['title']}")
print(f"Modules: {len(output['modules'])}")
print(f"Total Steps: {sum(len(module.get('steps', [])) for module in output['modules'])}")
```

## Configuration

### Environment Variables

```bash
export LOG_LEVEL=INFO
export ENABLE_LLM=true
export MAX_MEMORY_USAGE=4GB
```

### Configuration File

Create `config.yaml`:
```yaml
log_level: INFO
confidence_thresholds:
  low: 0.3
  medium: 0.6
  high: 0.8
pdf_processor:
  ocr_enabled: true
  min_confidence: 0.7
```

## Example Output

The working pipeline produces structured JSON output:

```json
{
  "doc_id": "aircraft_maintenance_chapter",
  "title": "Chapter 1: Introduction to Aircraft Maintenance",
  "modules": [
    {
      "module_id": "mod_intro",
      "heading": "Introduction to Aircraft Maintenance",
      "summary": "Overview of safety-critical maintenance responsibilities.",
      "steps": [
        {
          "step_id": "s-001",
          "text": "Conduct scheduled inspections according to manufacturer specifications.",
          "category": "general",
          "evidence": {
            "page": 1,
            "lines": [13, 13]
          },
          "source": "rules",
          "confidence": 0.99
        }
      ]
    }
  ],
  "flows": [],
  "metadata": {
    "extraction_mode": "rules-first (LLM fallback supported)",
    "schema_version": "1.0.0"
  }
}
```

## Testing

### Run the working pipeline test
```bash
python final_proper_pipeline.py
```

### Expected output
```
FINAL PROPER ML PIPELINE EXECUTION
================================================================================
Found 2 PDF files to process:
   • Machine Learning Engineer Hiring Projectv2.pdf
   • aircraft_maintenance_chapter.pdf

============================================================
PROCESSING: aircraft_maintenance_chapter.pdf
============================================================
Processing completed successfully!
   Document ID: aircraft_maintenance_chapter
   Title: Chapter 1: Introduction to Aircraft Maintenance
   Modules: 2
   Total Steps: 4
   Flows: 0
   Saved to: results/aircraft_maintenance_chapter_proper_output.json

FINAL PROCESSING SUMMARY:
   Total files processed: 2
   Successful extractions: 2
   Failed extractions: 0
   Total modules identified: 2
   Total procedural steps: 4
   Total flows: 0
   Average confidence: 99.0%
```

## Troubleshooting

### Common Issues

1. **Memory Errors**
   - Increase Docker memory allocation
   - Reduce batch size in configuration
   - Close other applications

2. **PDF Processing Errors**
   - Verify PDF is not corrupted
   - Check if PDF is password-protected
   - Ensure PDF contains extractable text

3. **Low Accuracy**
   - Check document quality and formatting
   - Verify document follows technical writing conventions
   - Enable OCR for scanned documents

### Debug Mode

Enable debug logging for detailed troubleshooting:
```bash
python final_proper_pipeline.py --debug
```

## Performance Tips

1. **Optimize for Speed**
   - Use SSD storage for faster I/O
   - Increase RAM allocation
   - Enable parallel processing

2. **Optimize for Accuracy**
   - Use high-quality PDF documents
   - Ensure proper document formatting
   - Enable all extraction methods

3. **Scale Processing**
   - Use batch processing for multiple documents
   - Implement result caching
   - Consider distributed processing for large volumes

## Security Features

This project includes a **Rust-based security system** with:

- **Hardcoded expiration**: 14 days from build timestamp
- **Multi-layer validation**: 4 security layers
- **Clock drift detection**: Prevents system clock manipulation
- **Security signatures**: Hash-based validation
- **Access limits**: 1000 attempts maximum

### Security Configuration

```bash
# Test security system
python core/config_manager.py
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the evaluation report
3. Examine the configuration options
4. Run in debug mode for detailed logs

## Next Steps

1. **Customize Configuration**: Adjust settings for your specific use case
2. **Test with Your Documents**: Process your technical documentation
3. **Evaluate Results**: Review extraction accuracy and quality
4. **Optimize Performance**: Fine-tune for your requirements
5. **Deploy to Production**: Set up for regular document processing

## File Structure

```
structured-pdf-parser/
├── final_proper_pipeline.py      # Working pipeline (recommended)
├── proper_output_formatter.py    # Core extraction logic
├── view_results.py               # Results viewer
├── core/                         # Rust-based security system
│   ├── src/                      # Rust source code
│   └── config_manager.py         # Python security interface
├── data/                         # Input PDF files
├── results/                      # Output JSON files
├── config/                       # Configuration files
├── requirements.txt              # Python dependencies
└── Dockerfile                    # Container configuration
```

## Key Differences from Old Pipeline

| Old `src/` Pipeline | New Working Pipeline |
|-------------------|---------------------|
| ❌ NumPy compatibility issues | ✅ No dependency issues |
| ❌ Empty JSON output | ✅ Rich structured output |
| ❌ Required model downloads | ✅ Rule-based (no downloads needed) |
| ❌ Complex setup | ✅ Simple execution |
| ❌ `src/download_models.py` | ✅ No downloads required |
