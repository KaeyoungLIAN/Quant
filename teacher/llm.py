import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)
# 确保日志能输出到 stderr（当 main.py 的 basicConfig 在 import 后才能生效时）
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

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


def build_lesson_prompt(module_key: str, mission: str, trackers_context: str, student_level: str) -> str:
    return f"""You are a quant trading teacher. Your student is a CS master graduate who wants to learn quantitative finance seriously (goal: {mission or 'become a quant trader'}).

## Student Progress
{trackers_context}

## Current Module
{module_key}

## Level
{student_level}

## Task
Generate ONE interactive lesson for this module. The lesson should:
1. Be self-contained — define everything from zero
2. Include a concrete numerical example with step-by-step calculation
3. Include Python code the student can run to verify
4. End with 2-3 checkpoint questions to test understanding

## Output Format
Return a JSON object with these fields:
{{
  "title": "Lesson title",
  "html_content": "Full HTML content with KaTeX math, Python code blocks, and explanations",
  "checkpoint": "Checkpoint questions"
}}

Write in Chinese. Make the HTML clean, dark-themed, with proper math rendering."""


def build_chat_prompt(user_message: str, context: str, history: str) -> str:
    return f"""You are a quant trading teacher. Your student is learning quantitative finance.

## Student Context
{context}

## Recent conversation history (last 10 turns)
{history}

## Current Question
{user_message}

Answer in Chinese. Be precise. If the question requires math, include formulas and examples. If it's about a concept the student hasn't studied yet, mention which prerequisite they need first."""
