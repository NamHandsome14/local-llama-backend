import os
from typing import List, Generator
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ctransformers import AutoModelForCausalLM

# --- Configuration ---
# Using the specific file available in the environment
MODEL_PATH = "models/llama-2-7b-chat.Q4_K_M.gguf"
MODEL_TYPE = "llama"
CONTEXT_LENGTH = 2048
MAX_NEW_TOKENS = 512
GPU_LAYERS = 0

llm_model = None

# Store stop signals: session_id -> bool
# If session_id is in this set, generation should stop.
stop_signals = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    
    print(f"Loading model: {MODEL_PATH}...")
    try:
        # Load model using ctransformers
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
    yield
    llm_model = None
    print("Model unloaded.")

app = FastAPI(title="Local LLaMA Streaming Backend", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: str = "default" # Unique ID for the chat session

class StopRequest(BaseModel):
    session_id: str

# --- Helper Functions ---

def format_prompt(messages: List[Message]) -> str:
    """
    Formats the conversation history into a LLaMA 2 compatible prompt string.
    Format: <s>[INST] <<SYS>>\n{sys}\n<</SYS>>\n\n{user} [/INST] {model} </s>...
    """
    prompt = ""
    system_prompt = ""
    
    # Extract system prompt if present
    if messages and messages[0].role == "system":
        system_prompt = messages[0].content
        # Start the loop from the next message
        convo_messages = messages[1:]
    else:
        convo_messages = messages

    # Helper wrapper for system prompt
    sys_wrapper = ""
    if system_prompt:
        sys_wrapper = f"<<SYS>>\n{system_prompt}\n<</SYS>>\n\n"

    # Build conversation
    # Note: This is a simplified builder. 
    # Proper LLaMA 2 tokenization is strict about spaces and special tokens.
    
    for i, msg in enumerate(convo_messages):
        is_last = (i == len(convo_messages) - 1)
        
        if msg.role == "user":
            if i == 0:
                # First user message gets the system prompt
                prompt += f"[INST] {sys_wrapper}{msg.content} [/INST]"
            else:
                prompt += f"<s>[INST] {msg.content} [/INST]"
        elif msg.role == "assistant":
            if is_last:
                # If it's the last message, do not append EOS </s>
                # This allows the model to continue generation
                prompt += f" {msg.content}"
            else:
                prompt += f" {msg.content} </s>"
            
    return prompt

def response_generator(prompt: str, session_id: str = None) -> Generator[str, None, None]:
    """
    Generator that yields tokens from the LLM.
    """
    global llm_model
    if llm_model is None:
        yield "Error: Model not loaded."
        return

    # Stream=True returns a generator
    stream = llm_model(
        prompt, 
        stream=True, 
        max_new_tokens=MAX_NEW_TOKENS
    )
    
    for token in stream:
        # Check for stop signal
        if session_id and session_id in stop_signals:
            print(f"Stopping generation for session: {session_id}")
            break
        yield token

    # Cleanup stop signal after completion
    if session_id and session_id in stop_signals:
        stop_signals.remove(session_id)

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "Streaming LLaMA API is ready. POST to /chat/stream"}

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    global llm_model
    if not llm_model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Ensure fresh start for this session
    if request.session_id in stop_signals:
        stop_signals.remove(request.session_id)

    # 1. Format the prompt
    prompt = format_prompt(request.messages)
    
    # 2. Return StreamingResponse
    # media_type="text/plain" so clients can read it easily as text
    return StreamingResponse(
        response_generator(prompt, request.session_id), 
        media_type="text/plain"
    )

@app.post("/chat/continue")
async def chat_continue(request: ChatRequest):
    """
    Continues the last assistant message in the conversation.
    The request should include the history including the partial assistant message at the end.
    """
    global llm_model
    if not llm_model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Ensure fresh start for this session
    if request.session_id in stop_signals:
        stop_signals.remove(request.session_id)

    # 1. Format the prompt
    # format_prompt will notice the last message is 'assistant' and omit the EOS </s>
    # enabling the model to continue it.
    prompt = format_prompt(request.messages)
    
    # 2. Return StreamingResponse
    return StreamingResponse(
        response_generator(prompt, request.session_id), 
        media_type="text/plain"
    )

@app.post("/chat/stop")
async def chat_stop(request: StopRequest):
    """
    Signal the active generation for this session to stop.
    """
    stop_signals.add(request.session_id)
    return {"message": f"Stop signal received for session {request.session_id}"}

if __name__ == "__main__":
    import uvicorn
    # Run server locally
    print("Starting server on http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
