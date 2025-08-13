# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- 8GB+ RAM (recommended)
- Docker (optional, for containerized deployment)

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

4. **Download required models**
   ```bash
   python src/download_models.py
   ```

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

1. **Process a single PDF document**
   ```bash
   python -m src.main --input aircraft_maintenance_chapter.pdf --output result.json
   ```

2. **Process multiple documents**
   ```bash
   python -m src.main --input-dir ./data --output-dir ./results
   ```

3. **Start API server**
   ```bash
   python -m src.main --api --host 0.0.0.0 --port 8000
   ```

### Python API

```python
from src.pipeline import TechnicalDocPipeline

# Initialize pipeline
pipeline = TechnicalDocPipeline()

# Process a document
results = pipeline.process_document("path/to/document.pdf")

# Access results
print(f"Confidence: {results['document_info']['confidence_score']}")
print(f"Modules: {len(results['modules'])}")
print(f"Steps: {len(results['procedural_steps'])}")
```

### REST API

1. **Start the server**
   ```bash
   python -m src.main --api
   ```

2. **Process document via API**
   ```bash
   curl -X POST "http://localhost:8000/process" \
        -H "Content-Type: application/json" \
        -d '{"input_path": "document.pdf", "output_path": "result.json"}'
   ```

3. **Upload and process document**
   ```bash
   curl -X POST "http://localhost:8000/process/upload" \
        -F "file=@document.pdf"
   ```

## Configuration

### Environment Variables

```bash
export LOG_LEVEL=INFO
export LLM_MODEL_NAME=gpt2
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

The pipeline produces structured JSON output:

```json
{
  "document_info": {
    "filename": "aircraft_maintenance_chapter.pdf",
    "processing_timestamp": "2024-01-15T10:30:00Z",
    "confidence_score": 0.87
  },
  "modules": [
    {
      "id": "module_001",
      "name": "Safety Procedures",
      "description": "Pre-flight safety checks and procedures",
      "confidence": 0.92
    }
  ],
  "procedural_steps": [
    {
      "id": "step_001",
      "description": "Check aircraft exterior for visible damage",
      "estimated_time": "15 minutes",
      "required_tools": ["flashlight", "checklist"],
      "safety_notes": ["Ensure aircraft is properly secured"]
    }
  ],
  "decision_points": [
    {
      "id": "decision_001",
      "condition": "If damage is found, proceed to damage assessment",
      "actions": ["halt_procedure", "notify_supervisor"]
    }
  ]
}
```

## Testing

### Run the test script
```bash
python test_pipeline.py
```

### Expected output
```
==================================================
PIPELINE TEST RESULTS
==================================================
Document processed: sample_maintenance.txt
Confidence score: 0.85
Modules extracted: 2
Procedural steps: 3
Decision points: 2
Equipment identified: 2
Processing successful: True
==================================================
```

## Troubleshooting

### Common Issues

1. **Memory Errors**
   - Increase Docker memory allocation
   - Reduce batch size in configuration
   - Close other applications

2. **Model Download Failures**
   - Check internet connection
   - Verify disk space (2-4GB required)
   - Run `python src/download_models.py` manually

3. **PDF Processing Errors**
   - Verify PDF is not corrupted
   - Check if PDF is password-protected
   - Ensure PDF contains extractable text

4. **Low Accuracy**
   - Check document quality and formatting
   - Verify document follows technical writing conventions
   - Enable OCR for scanned documents

### Debug Mode

Enable debug logging for detailed troubleshooting:
```bash
python -m src.main --debug --input document.pdf
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
