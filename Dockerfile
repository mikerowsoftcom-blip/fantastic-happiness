FROM python:3.11-slim

# Build tools needed to compile llama-cpp-python from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# CPU-only build, keep it lean
RUN CMAKE_ARGS="-DLLAMA_NATIVE=off" pip install --no-cache-dir -r requirements.txt

# Bake the model into the image at build time (avoids a slow download on every cold start)
RUN mkdir -p /app/models && \
    curl -L -o /app/models/model.gguf \
    "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"

COPY app.py .

ENV MODEL_PATH=/app/models/model.gguf
ENV N_CTX=256
ENV N_THREADS=1

EXPOSE 10000

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]
