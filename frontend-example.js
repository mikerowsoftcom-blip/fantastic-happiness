// Example client for your static HTML site.
// Replace the endpoint and API key before use.
//
// SECURITY: A secret placed in browser JavaScript is not actually secret.
// For a public site, use a small backend/proxy to keep API_KEY private.

const LLAMA_API = "https://YOUR-SERVICE.onrender.com/v1/chat/completions";
const API_KEY = "YOUR_API_KEY";

export async function chat(messages) {
  const response = await fetch(LLAMA_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: "qwen3-0.6b",
      messages,
      temperature: 0.7,
      max_tokens: 512,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`LLM request failed (${response.status}): ${text}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}
