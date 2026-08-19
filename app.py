import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_cpp import Llama

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/models/model.gguf")
N_CTX = int(os.environ.get("N_CTX", "512"))
N_THREADS = int(os.environ.get("N_THREADS", "1"))

llm = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_batch=64,
        use_mlock=False,
        verbose=False,
    )
    yield


app = FastAPI(lifespan=lifespan)

# Allow calls from any static site. Tighten allow_origins to your domain
# (e.g. ["https://yoursite.com"]) once things are working.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int = 256
    temperature: float = 0.7


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": llm is not None}


@app.post("/generate")
def generate(req: GenerateRequest):
    if llm is None:
        raise HTTPException(503, "Model not loaded yet")
    start = time.time()
    out = llm(
        req.prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        stop=["</s>"],
    )
    text = out["choices"][0]["text"]
    return {"text": text, "seconds": round(time.time() - start, 2)}


@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest):
    if llm is None:
        raise HTTPException(503, "Model not loaded yet")
    messages = [m.model_dump() for m in req.messages]
    out = llm.create_chat_completion(
        messages=messages,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
    )
    return out
