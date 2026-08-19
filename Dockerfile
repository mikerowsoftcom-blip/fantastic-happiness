FROM python:3.11-slim

# Build tools needed to compile llama-cpp-python from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Build llama-cpp-python FROM SOURCE with every advanced CPU instruction set
# disabled. PyPI ships prebuilt wheels compiled with AVX2/FMA/AVX512, and if
# a matching wheel exists pip silently uses it instead of respecting
# CMAKE_ARGS below -- which crashes with "Illegal instruction" on hosts
# whose CPUs don't support those instructions (common on shared/free-tier
# cloud instances). --no-binary forces an actual source build so these
# flags take effect.
RUN CMAKE_ARGS="-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF" \
    pip install --no-cache-dir --force-reinstall --no-binary llama-cpp-python "llama-cpp-python==0.2.90"

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
