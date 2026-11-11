import re
import time
from collections import defaultdict

_ASK_PATHS = {"/api/ask", "/api/report"}
_WINDOW_SECONDS = 60
_ASK_LIMIT = 30
_FAIL_LIMIT = 8


def set_ask_limit(limit):
    global _ASK_LIMIT
    _ASK_LIMIT = limit
_HITS = defaultdict(list)
_FAILS = defaultdict(list)

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(value):
    return _CONTROL.sub("", value or "").strip()


def reset_limits():
    _HITS.clear()
    _FAILS.clear()


def too_many(path, host):
    if path not in _ASK_PATHS:
        return False
    key = f"{host}|{path}"
    if _count(_HITS, key) >= _ASK_LIMIT:
        return True
    _HITS[key].append(time.monotonic())
    return False


def too_many_failures(host):
    return _count(_FAILS, host) >= _FAIL_LIMIT


def note_failure(host):
    _prune(_FAILS, host)
    _FAILS[host].append(time.monotonic())


def clear_failures(host):
    _FAILS.pop(host, None)


def _count(table, key):
    _prune(table, key)
    return len(table[key])


def _prune(table, key):
    cutoff = time.monotonic() - _WINDOW_SECONDS
    table[key] = [stamp for stamp in table[key] if stamp >= cutoff]


def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; "
        "connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; "
        "form-action 'self'"
    )
    if "server" in response.headers:
        del response.headers["server"]
    return response
