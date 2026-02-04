import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ctransformers import AutoModelForCausalLM

# --- Configuration ---
# Path relative to the working directory
MODEL_PATH = "models/llama-2-7b-chat.Q4_K_M.gguf"
MODEL_TYPE = "llama"

# Model Parameters
CONTEXT_LENGTH = 2048
MAX_NEW_TOKENS = 256
GPU_LAYERS = 0  # 0 = CHỈ DÙNG CPU

# Global variable to hold the loaded model instance
llm_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the FastAPI application.
    Executes startup logic (loading model) and shutdown logic.
    """
    global llm_model
    
    # 1. Verification
    if not os.path.exists(MODEL_PATH):
        # Fail fast if model is missing
        error_msg = f"Model file not found at: {os.path.abspath(MODEL_PATH)}"
        print(error_msg)
        raise FileNotFoundError(error_msg)

    print(f"Initializing LLaMA model from: {MODEL_PATH}")
    print("Please wait, loading model into memory...")

    try:
        # 2. Load Model using ctransformers
        # This initializes the model once at startup
        llm_model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            model_type=MODEL_TYPE,
            gpu_layers=GPU_LAYERS,
            context_length=CONTEXT_LENGTH
        )
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Failed to load model: {e}")
        raise e

    yield  # Application runs here

    # 3. Shutdown / Cleanup
    print("Shutting down application...")
    llm_model = None

# Create FastAPI app with lifespan
app = FastAPI(title="Local LLaMA Backend", lifespan=lifespan)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Data Models ---

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "Local LLaMA API is running. Send POST requests to /ask."}

@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    POST endpoint to ask a question to the LLaMA model.
    """
    global llm_model

    # Ensure model is ready
    if llm_model is None:
        raise HTTPException(status_code=503, detail="AI Model is not ready/loaded.")

    try:
        # Extract prompt from request
        prompt = request.question

        # Generate response
        # Using the __call__ method of the ctransformers model
        generated_text = llm_model(
            prompt,
            max_new_tokens=MAX_NEW_TOKENS
        )

        return AskResponse(answer=generated_text)

    except Exception as e:
        print(f"Error during inference: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during inference")

if __name__ == "__main__":
    import uvicorn
    # Run server locally
    print("Starting server on http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
