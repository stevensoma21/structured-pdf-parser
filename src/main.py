"""
Main Entry Point

Command line interface and API endpoints for the technical document ML pipeline.
"""

import argparse
import logging
import json
import sys
from pathlib import Path
from typing import Dict, Optional
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .pipeline import TechnicalDocPipeline
from .config import load_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Technical Document ML Pipeline",
    description="A fully-contained ML pipeline for processing technical documentation",
    version="1.0.0"
)

# Global pipeline instance
pipeline: Optional[TechnicalDocPipeline] = None


class ProcessingRequest(BaseModel):
    """Request model for document processing."""
    input_path: str
    output_path: Optional[str] = None
    config: Optional[Dict] = None


class ProcessingResponse(BaseModel):
    """Response model for document processing."""
    success: bool
    results: Dict
    message: str


@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup."""
    global pipeline
    try:
        config = load_config()
        pipeline = TechnicalDocPipeline(config)
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        sys.exit(1)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Technical Document ML Pipeline API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    status = pipeline.get_processing_status()
    return JSONResponse(content=status)


@app.post("/process", response_model=ProcessingResponse)
async def process_document(request: ProcessingRequest):
    """Process a single document."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        # Update config if provided
        if request.config:
            pipeline.config.update(request.config)
        
        # Process document
        results = pipeline.process_document(request.input_path, request.output_path)
        
        return ProcessingResponse(
            success=len(results.get('errors', [])) == 0,
            results=results,
            message="Document processed successfully" if len(results.get('errors', [])) == 0 else "Processing completed with errors"
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/upload")
async def process_uploaded_document(file: UploadFile = File(...)):
    """Process an uploaded PDF document."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        results = pipeline.process_document(str(temp_path))
        
        # Clean up temporary file
        temp_path.unlink()
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"Error processing uploaded document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/batch")
async def process_directory(request: ProcessingRequest):
    """Process all PDF documents in a directory."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        # Update config if provided
        if request.config:
            pipeline.config.update(request.config)
        
        # Process directory
        results = pipeline.process_directory(request.input_path, request.output_path or "./results")
        
        return JSONResponse(content={
            "success": True,
            "processed_files": len(results),
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error processing directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get pipeline status and configuration."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        status = pipeline.get_processing_status()
        validation = pipeline.validate_configuration()
        
        return JSONResponse(content={
            "status": status,
            "validation": validation
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point for command line interface."""
    parser = argparse.ArgumentParser(description="Technical Document ML Pipeline")
    parser.add_argument("--input", "-i", required=True, help="Input PDF file or directory")
    parser.add_argument("--output", "-o", help="Output file or directory")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--host", default="127.0.0.1", help="Host for API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument("--api", action="store_true", help="Start API server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Setup logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        if args.api:
            # Start API server
            logger.info(f"Starting API server on {args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port)
        else:
            # Process documents directly
            pipeline = TechnicalDocPipeline(config)
            
            input_path = Path(args.input)
            output_path = Path(args.output) if args.output else None
            
            if input_path.is_file():
                # Process single file
                logger.info(f"Processing single file: {input_path}")
                results = pipeline.process_document(str(input_path), str(output_path) if output_path else None)
                
                # Print results
                print(json.dumps(results, indent=2))
                
            elif input_path.is_dir():
                # Process directory
                logger.info(f"Processing directory: {input_path}")
                output_dir = output_path or Path("./results")
                results = pipeline.process_directory(str(input_path), str(output_dir))
                
                # Print summary
                print(f"Processed {len(results)} files")
                print(f"Results saved to: {output_dir}")
                
            else:
                logger.error(f"Input path does not exist: {input_path}")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
