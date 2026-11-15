import json

import openai

from app.core.config import settings

MODEL = "gpt-4o-mini"
TIMEOUT_SECONDS = 30


class LLMError(Exception):
    pass


class LLMBadReply(LLMError):
    """The call worked but the reply was not a JSON object."""


def _llm_error(e: openai.APIError) -> LLMError:
    if isinstance(e, openai.AuthenticationError):
        return LLMError("OpenAI rejected the API key, check OPENAI_API_KEY")
    if isinstance(e, openai.APITimeoutError):
        return LLMError(f"OpenAI did not answer within {TIMEOUT_SECONDS}s")
    if isinstance(e, openai.RateLimitError):
        return LLMError("OpenAI rate limit or quota hit")
    return LLMError(f"OpenAI request failed: {e}")


def _client() -> openai.OpenAI:
    return openai.OpenAI(api_key=settings.openai_api_key, timeout=TIMEOUT_SECONDS, max_retries=0)


def chat_json(system_prompt: str, user_text: str) -> dict:
    """Send one request and return the JSON reply as a dict."""
    try:
        resp = _client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
    except openai.APIError as e:
        raise _llm_error(e)

    content = resp.choices[0].message.content or ""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise LLMBadReply("OpenAI reply was not valid JSON")
    if not isinstance(data, dict):
        raise LLMBadReply("OpenAI reply was not a JSON object")
    return data


def chat_stream(system_prompt: str, user_text: str, temperature: float = 0.7):
    """Send one request and yield the reply as text chunks as they arrive."""
    try:
        with _client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=temperature,
            stream=True,
        ) as stream:
            for chunk in stream:
                if not chunk.choices:
                    continue
                piece = chunk.choices[0].delta.content
                if piece:
                    yield piece
    except openai.APIError as e:
        raise _llm_error(e)
