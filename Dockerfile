FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MODEL_PATH=/models/model.gguf \
    N_CTX=4096 \
    N_THREADS=2 \
    N_BATCH=256 \
    N_GPU_LAYERS=0 \
    MODEL_URL=https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install llama-cpp-python==0.3.34 \
       --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

RUN mkdir -p /models \
    && curl -L --fail --retry 5 --retry-delay 3 \
       -o /models/model.gguf "$MODEL_URL" \
    && test -s /models/model.gguf

COPY app.py .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
