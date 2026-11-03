import json

import openai

from app.core.config import settings

MODEL = "gpt-4o-mini"
TIMEOUT_SECONDS = 30


class LLMError(Exception):
    pass


def chat_json(system_prompt: str, user_text: str) -> dict:
    """Send one request and return the JSON reply as a dict."""
    client = openai.OpenAI(api_key=settings.openai_api_key, timeout=TIMEOUT_SECONDS, max_retries=0)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
    except openai.AuthenticationError:
        raise LLMError("OpenAI rejected the API key, check OPENAI_API_KEY")
    except openai.APITimeoutError:
        raise LLMError(f"OpenAI did not answer within {TIMEOUT_SECONDS}s")
    except openai.RateLimitError:
        raise LLMError("OpenAI rate limit or quota hit")
    except openai.APIError as e:
        raise LLMError(f"OpenAI request failed: {e}")

    content = resp.choices[0].message.content or ""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise LLMError("OpenAI reply was not valid JSON")
    if not isinstance(data, dict):
        raise LLMError("OpenAI reply was not a JSON object")
    return data
