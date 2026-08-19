# llama-cpp-python on Render

A small OpenAI-compatible HTTP API around `llama-cpp-python`, intended for a static HTML/JS frontend.

## Model

The Docker image automatically downloads:

**Qwen3-0.6B Q4_K_M GGUF**

from the Qwen Hugging Face repository during the image build. The model is not stored in GitHub.

If you later want another GGUF, change `MODEL_URL` in `Dockerfile`.

## Deploy on Render

1. Push this directory to a GitHub repository.
2. In Render, create a **Web Service** from that repository.
3. Choose Docker as the runtime, or let Render detect `Dockerfile`.
4. Set:
   - `API_KEY` = a long random secret
   - `CORS_ORIGINS` = your static website's exact origin, e.g. `https://example.com`
5. Deploy.

The first build downloads the model and will therefore take longer than subsequent builds.

## Test

After deployment:

```text
GET https://YOUR-SERVICE.onrender.com/health
```

Expected:

```json
{"status":"ok","model_loaded":true}
```

Then:

```bash
curl https://YOUR-SERVICE.onrender.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "qwen3-0.6b",
    "messages": [
      {"role": "user", "content": "Hello! Tell me a short joke."}
    ],
    "temperature": 0.7,
    "max_tokens": 128
  }'
```

## Static website

The API accepts the standard OpenAI-style chat completion request:

```js
const response = await fetch(
  "https://YOUR-SERVICE.onrender.com/v1/chat/completions",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer YOUR_API_KEY"
    },
    body: JSON.stringify({
      model: "qwen3-0.6b",
      messages: [
        { role: "user", content: "Hello!" }
      ],
      temperature: 0.7,
      max_tokens: 512
    })
  }
);

const data = await response.json();
const reply = data.choices[0].message.content;
```

### Important security warning

Do **not** put a valuable long-lived Render API key into public browser JavaScript.

Anyone can inspect the JavaScript/network requests and reuse the key.

For a public website, the recommended production setup is:

```text
Browser
   ↓
Your website/backend proxy
   ↓
Render llama.cpp service
```

The proxy keeps the Render key private and can enforce rate limits.

For initial testing, however, the browser can call the Render endpoint directly. Set `CORS_ORIGINS` to your site's exact origin rather than `*`.

## Configuration

Defaults are intentionally conservative for a small CPU instance:

- `N_CTX=4096`
- `N_THREADS=2`
- `N_BATCH=256`
- `N_GPU_LAYERS=0`

If your Render instance has more CPU/RAM, these can be increased.

## Changing models

Change this line in `Dockerfile`:

```text
MODEL_URL=...
```

The URL must point to a compatible GGUF file.

The application will continue exposing:

```text
POST /v1/chat/completions
```
