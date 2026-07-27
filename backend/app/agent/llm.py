"""
Thin wrapper around the Groq client. Kept separate from tools.py so the
model name / retry logic lives in exactly one place.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"  # use if primary struggles with JSON reliability


def call_llm_json(system_prompt: str, user_prompt: str, model: str = PRIMARY_MODEL, max_retries: int = 2) -> dict:
    """
    Calls the LLM and enforces JSON output. Groq's OpenAI-compatible API
    supports response_format={"type": "json_object"} — use it, it's far
    more reliable than asking nicely in the prompt alone.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw = resp.choices[0].message.content
            return json.loads(raw)
        except (json.JSONDecodeError, Exception) as e:  # noqa: BLE001
            last_error = e
            if attempt == max_retries and model == PRIMARY_MODEL:
                # last resort: try the bigger model once
                model = FALLBACK_MODEL
                continue
    raise RuntimeError(f"LLM call failed after retries: {last_error}")
