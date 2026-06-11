import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")


def call_llm(prompt: str, temperature: float = 0.5, max_tokens: int = 2000) -> str | None:
    logger.info(f"LLM call start... key_set={bool(LLM_API_KEY)} base={LLM_BASE_URL} model={LLM_MODEL}")
    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY not set")
        return None
    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None
