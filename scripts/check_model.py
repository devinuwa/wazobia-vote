import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import MODEL_NAME  # noqa: E402  loads .env without printing it
from app.llm import configured, providers, redact_secret, request_body, endpoint


def send(json_mode):
    provider = providers()[0]
    messages = [
        {"role": "system", "content": "Reply with one JSON object and nothing else."},
        {"role": "user", "content": "Return {\"ok\": true}."},
    ]
    probe = dict(provider)
    probe["effort"] = "low"
    body = request_body(probe, messages, json_mode=json_mode, max_completion_tokens=256)
    return httpx.post(
        endpoint(provider["base"]),
        json=body,
        headers={"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"},
        timeout=60,
    )


def show_error(response):
    print(redact_secret(f"HTTP {response.status_code}"))
    print(redact_secret(response.text[:800]))


def main():
    if not configured():
        print("FAIL no model configured")
        return 1
    print("model:", os.environ.get("MODEL_NAME") or MODEL_NAME)
    response = send(True)
    rejected = response.status_code == 400 and (
        "response_format" in response.text.casefold()
        or "json_object" in response.text.casefold()
        or "json_schema" in response.text.casefold()
    )
    if rejected:
        print("JSON mode: rejected")
        show_error(response)
        response = send(False)
        if response.status_code >= 400:
            print("plain prompt: FAIL")
            show_error(response)
            return 1
        print("plain prompt: success")
        return 0
    if response.status_code >= 400:
        print("FAIL")
        show_error(response)
        return 1
    print("JSON mode: accepted")
    print("success")
    return 0


if __name__ == "__main__":
    sys.exit(main())
