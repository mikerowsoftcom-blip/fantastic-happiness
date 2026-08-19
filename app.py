import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from llama_cpp import Llama

MODEL_PATH = os.getenv("MODEL_PATH", "/models/model.gguf")
API_KEY = os.getenv("API_KEY", "")
N_CTX = int(os.getenv("N_CTX", "4096"))
N_THREADS = int(os.getenv("N_THREADS", str(max(1, (os.cpu_count() or 2) - 1))))
N_BATCH = int(os.getenv("N_BATCH", "256"))
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "0"))

app = FastAPI(title="Llama.cpp Python API", version="1.0.0")

cors_origins = os.getenv("CORS_ORIGINS", "*")
origins = [x.strip() for x in cors_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm: Optional[Llama] = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "qwen3-0.6b"
    messages: list[Message]
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=512, ge=1, le=4096)
    top_p: float = Field(default=0.9, ge=0, le=1)

def check_auth(authorization: Optional[str]):
    if not API_KEY:
        return
    expected = f"Bearer {API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.on_event("startup")
def load_model():
    global llm
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(
            f"Model not found at {MODEL_PATH}. "
            "Set MODEL_PATH to a mounted/downloaded GGUF file."
        )
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_batch=N_BATCH,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False,
    )

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": llm is not None}

@app.post("/v1/chat/completions")
def chat_completions(
    request: ChatRequest,
    authorization: Optional[str] = Header(default=None),
):
    check_auth(authorization)
    if llm is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")

    result = llm.create_chat_completion(
        messages=[m.model_dump() for m in request.messages],
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens,
    )

    return result
