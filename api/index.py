import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from dotenv import load_dotenv
from agent import run_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Verify required environment variables
required_env_vars = [
    "GEMINI_API_KEY",
    "PINECONE_API_KEY",
    "YOUTUBE_API_KEY",
    "PINECONE_INDEX",
    "PINECONE_CLOUD",
    "PINECONE_REGION"
]

for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"Missing required environment variable: {var}")
        raise EnvironmentError(f"Missing required environment variable: {var}")

app = FastAPI()

# Configure CORS with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.post("/api/youtube")
async def youtube_question(request: Request):
    try:
        logger.info("Received YouTube question request")
        data = await request.json()
        question = data.get("question")
        
        if not question:
            logger.warning("Question field is missing in request")
            return JSONResponse(
                status_code=400,
                content={"error": "Question is required"}
            )
            
        logger.info(f"Processing YouTube question: {question}")
        result = run_agent(question, context="youtube")
        
        # Ensure consistent response format
        response_data = {
            "response": result.get("response") or result.get("answer"),
            "data": result.get("data") or result.get("youtube_data"),
            "success": True
        }
        
        if "error" in result:
            logger.error(f"Error processing YouTube question: {result['error']}")
            return JSONResponse(
                status_code=500,
                content={"error": result["error"], "success": False}
            )
            
        logger.info("Successfully processed YouTube question")
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Unexpected error in youtube_question: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}", "success": False}
        )

@app.post("/api/chat")
async def chat_question(request: Request):
    try:
        logger.info("Received chat question request")
        data = await request.json()
        question = data.get("question")
        
        if not question:
            logger.warning("Question field is missing in request")
            return JSONResponse(
                status_code=400,
                content={"error": "Question is required", "success": False}
            )
            
        logger.info(f"Processing chat question: {question}")
        result = run_agent(question, context="general")
        
        # Ensure consistent response format
        response_data = {
            "response": result.get("response") or result.get("answer"),
            "success": True
        }
        
        if "error" in result:
            logger.error(f"Error processing chat question: {result['error']}")
            return JSONResponse(
                status_code=500,
                content={"error": result["error"], "success": False}
            )
            
        logger.info("Successfully processed chat question")
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Unexpected error in chat_question: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}", "success": False}
        )

@app.get("/api/health")
async def health_check():
    try:
        logger.info("Health check request received")
        # Verify environment variables
        for var in required_env_vars:
            if not os.getenv(var):
                raise EnvironmentError(f"Missing {var}")
        return JSONResponse(
            content={"status": "ok", "message": "All services are operational"}
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Create handler for AWS Lambda
handler = Mangum(app) 