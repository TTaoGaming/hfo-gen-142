#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, time, urllib.request, urllib.error
from dataclasses import dataclass

MAX_PROMPT_BYTES = 32768
MAX_RESPONSE_BYTES = 262144
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
KIMI_SUFFIX = "/coding/v1/chat/completions"

class AdapterHold(RuntimeError):
    pass

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

@dataclass(frozen=True)
class ProposalRoute:
    provider_id: str
    url: str
    model: str
    secret_env: str | None = None
    zero_marginal: bool = True

def validate_route(route: ProposalRoute) -> None:
    if route.provider_id == "openrouter_free":
        if route.url != OPENROUTER_URL or not route.model.endswith(":free"):
            raise AdapterHold("OPENROUTER_FREE_ROUTE_NOT_PROVEN_ZERO_COST")
        if route.secret_env != "OPENROUTER_API_KEY":
            raise AdapterHold("OPENROUTER_SECRET_BINDING_MISMATCH")
    elif route.provider_id == "kimi_cloudflare":
        if not route.url.startswith("https://") or not route.url.endswith(KIMI_SUFFIX):
            raise AdapterHold("KIMI_GATEWAY_ROUTE_MISMATCH")
        if not route.secret_env:
            raise AdapterHold("KIMI_GATEWAY_SECRET_BINDING_MISSING")
    elif route.provider_id == "local_openai":
        if not (route.url.startswith("http://127.0.0.1:") or route.url.startswith("http://localhost:")):
            raise AdapterHold("LOCAL_ROUTE_MUST_BE_LOOPBACK")
    else:
        raise AdapterHold("UNKNOWN_PROVIDER_ROUTE")
    if not route.zero_marginal:
        raise AdapterHold("PAID_ROUTE_NOT_AUTHORIZED")

def request_once(route: ProposalRoute, prompt: str, timeout_s: int = 120) -> tuple[str, dict]:
    validate_route(route)
    prompt_bytes = prompt.encode("utf-8")
    if not prompt_bytes or len(prompt_bytes) > MAX_PROMPT_BYTES:
        raise AdapterHold("PROMPT_SIZE_REFUSED")
    secret = ""
    if route.secret_env:
        secret = os.environ.get(route.secret_env, "")
        if not secret:
            raise AdapterHold("SECRET_ABSENT_BEFORE_NETWORK")
    body = {"model": route.model, "messages": [{"role": "user", "content": prompt}],
            "stream": False, "temperature": 0, "max_tokens": 2048}
    if route.provider_id == "openrouter_free":
        body["provider"] = {"allow_fallbacks": False,
                            "max_price": {"prompt": 0, "completion": 0, "request": 0}}
    body_bytes = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    headers = {"Content-Type": "application/json"}
    if secret:
        headers["Authorization"] = "Bearer " + secret
    req = urllib.request.Request(route.url, data=body_bytes, headers=headers, method="POST")
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read(MAX_RESPONSE_BYTES + 1)
            status = int(resp.status)
    except urllib.error.HTTPError as exc:
        raw = exc.read(MAX_RESPONSE_BYTES + 1)
        status = int(exc.code)
    latency_ms = round((time.monotonic() - started) * 1000)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise AdapterHold("RESPONSE_SIZE_REFUSED")
    if status < 200 or status >= 300:
        raise AdapterHold(f"HTTP_STATUS_{status}")
    doc = json.loads(raw.decode("utf-8"))
    text = doc["choices"][0]["message"].get("content") or ""
    if not isinstance(text, str) or not text.strip():
        raise AdapterHold("EMPTY_COMPLETION")
    receipt = {
        "schema": "hfo.proposal-provider-receipt.v1",
        "provider_id": route.provider_id,
        "model": route.model,
        "zero_marginal": route.zero_marginal,
        "request_sha256": sha256(body_bytes),
        "response_sha256": sha256(raw),
        "latency_ms": latency_ms,
        "http_status": status,
        "secret_env_name": route.secret_env,
        "secret_value_exported": False,
        "retries": 0,
    }
    usage = doc.get("usage")
    if isinstance(usage, dict):
        receipt["usage"] = usage
    return text, receipt
