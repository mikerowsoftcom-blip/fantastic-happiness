# llama-cpp-python on Render

This service exposes an OpenAI-compatible `/v1/chat/completions` API using llama-cpp-python and Qwen3-0.6B.

## Current model

The Docker build downloads the **Qwen3-0.6B Q4_K_M GGUF** from an immutable Hugging Face revision. The pinned file is about 397 MB.

The immutable revision is used because the Qwen repository's current `main` branch no longer exposes this Q4_K_M file; using `main` caused the Render `curl: (22) 404` build failure.

## Deploy

Push the repository to GitHub and redeploy the Render service.

Environment variables:

- `API_KEY`: long random secret
- `CORS_ORIGINS`: your website origin, e.g. `https://example.com`

Health check:

`GET /health`

Chat:

`POST /v1/chat/completions`

## Important

A browser-visible API key is not secret. For a public website, put a small backend/proxy in front of this service so the Render key is never exposed to visitors.
