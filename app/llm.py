import json
import os
import re
import time

import httpx

from app.config import MODEL_BASE_URL
from app.privacy import redact_for_log

_JSON_OBJECT_OK = {}
RETRY_WAIT_SECONDS = 1.5
BUSY_STATUSES = {429, 413}


class ModelError(RuntimeError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def redact_secret(text, secret=""):
    secrets = [secret, os.environ.get("MODEL_API_KEY", ""), os.environ.get("FALLBACK_API_KEY", "")]
    for value in secrets:
        value = (value or "").strip()
        if value and value in text:
            text = text.replace(value, "[redacted]")
    return text


def _redact(text, secret):
    return redact_secret(text, secret)


def _json_mode_rejected(body):
    folded = body.casefold()
    return "response_format" in folded or "json_object" in folded or "json_schema" in folded


def _flag(value):
    return value.casefold() in {"1", "true", "yes"}


def _provider(prefix):
    key_name = "MODEL_API_KEY" if prefix == "MODEL" else "FALLBACK_API_KEY"
    base_name = "MODEL_BASE_URL" if prefix == "MODEL" else "FALLBACK_BASE_URL"
    model_name = "MODEL_NAME" if prefix == "MODEL" else "FALLBACK_MODEL_NAME"
    key = os.environ.get(key_name, "").strip()
    base = os.environ.get(base_name, MODEL_BASE_URL if prefix == "MODEL" else "").strip()
    model = os.environ.get(model_name, "").strip()
    if not key or not base or not model:
        return None
    return {
        "base": base,
        "model": model,
        "key": key,
        "effort": os.environ.get(f"{prefix}_REASONING_EFFORT", "").strip(),
        "include": os.environ.get(f"{prefix}_INCLUDE_REASONING", "").strip(),
    }


def providers():
    rows = []
    for prefix in ("MODEL", "FALLBACK"):
        row = _provider(prefix)
        if row:
            rows.append(row)
    return rows


def configured():
    return bool(providers())


def endpoint(base=None):
    root = (base if base is not None else os.environ.get("MODEL_BASE_URL", MODEL_BASE_URL)).rstrip("/")
    if root.endswith("/chat/completions"):
        return root
    if root.endswith("/v1"):
        return root + "/chat/completions"
    return root + "/chat/completions"


def request_body(provider, messages, json_mode=False, max_completion_tokens=2048):
    body = {
        "model": provider["model"],
        "temperature": 0.5,
        "top_p": 1,
        "max_completion_tokens": max_completion_tokens,
        "messages": messages,
    }
    if provider.get("effort"):
        body["reasoning_effort"] = provider["effort"]
    if provider.get("include"):
        body["include_reasoning"] = _flag(provider["include"])
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    return body


def _post(provider, body):
    return httpx.post(
        endpoint(provider["base"]),
        json=body,
        headers={"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"},
        timeout=60,
    )


def _read_content(response, key):
    if response.status_code >= 400:
        detail = redact_for_log(_redact(response.text[:500], key))
        raise ModelError(f"model request failed ({response.status_code}) {detail}", status=response.status_code)
    payload = response.json()
    choice = payload["choices"][0]
    finish = choice.get("finish_reason") or ""
    content = (choice.get("message") or {}).get("content") or ""
    if finish == "length":
        raise ModelError("finish_reason length")
    if not content.strip():
        raise ModelError("empty model reply")
    return content


def _call_provider(provider, messages, json_mode, max_completion_tokens):
    url = endpoint(provider["base"])
    use_json = json_mode and _JSON_OBJECT_OK.get(url, True)
    body = request_body(provider, messages, json_mode=use_json, max_completion_tokens=max_completion_tokens)
    response = _post(provider, body)
    if response.status_code == 400 and use_json and _json_mode_rejected(response.text):
        _JSON_OBJECT_OK[url] = False
        body.pop("response_format", None)
        response = _post(provider, body)
    if response.status_code in BUSY_STATUSES:
        time.sleep(RETRY_WAIT_SECONDS)
        response = _post(provider, body)
    return _read_content(response, provider["key"])


def complete(system, user, json_mode=False, max_completion_tokens=2048):
    rows = providers()
    if not rows:
        raise ModelError("no model configured")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    last = None
    for provider in rows:
        try:
            return _call_provider(provider, messages, json_mode, max_completion_tokens)
        except ModelError as exc:
            last = exc
    raise last


def parse_json_object(content):
    text = content.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ModelError("model reply was not a JSON object")
    return json.loads(text[start : end + 1])


def english_keywords(question):
    content = complete(
        "Rewrite the voter's question as English search keywords. "
        "Return keywords only, at most 30 words. Do not answer the question.",
        question,
        json_mode=False,
        max_completion_tokens=1024,
    )
    text = " ".join(content.strip().split())
    if not text or len(text.split()) > 40 or "{" in text:
        raise ModelError("keyword rewrite failed")
    return text
