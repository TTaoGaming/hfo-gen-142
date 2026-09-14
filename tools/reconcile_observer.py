#!/usr/bin/env python3
"""Trusted readback observer for the Gen142 deterministic reconciler.

This module owns no scheduler, queue, lease, actor state, credentials, or effects.
It performs bounded GET readbacks from allowlisted controller/API surfaces,
derives provenance from the request it actually made, projects only semantic
state, and feeds the pure reconcile kernel.

Authority metadata inside a response body is never trusted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from tools import reconcile_kernel as rk

SOURCE_SCHEMA = "hfo.reconcile_sources.v0"
OBSERVER_VERSION = "gen142-trusted-observer-r0"
MAX_RESPONSE_BYTES = 1_048_576
REQUIRED_KINDS = {
    "actor": dict,
    "demand": list,
    "dispatches": list,
    "worker_routes": list,
    "human_boundary": dict,
}
SOURCE_OWNERS = {
    "actor": "hfo-sigrun-va-r0",
    "demand": "github",
    "dispatches": "github-actions",
    "worker_routes": "github",
    "human_boundary": "github",
}
ACTOR_HOST = "hfo-sigrun-va-r0.tommytai3.workers.dev"
GITHUB_HOSTS = {"api.github.com", "raw.githubusercontent.com"}
ALLOWED_GITHUB_REPOS = {"hfo-gen-142", "cdev-control"}


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


def digest_bytes(value: bytes):
    return hashlib.sha256(value).hexdigest()


def hold(code, **detail):
    return {"decision": "HOLD", "reason": code, **detail}


def utc_text(now=None):
    dt = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def trusted_url(kind, url):
    try:
        p = urlsplit(str(url))
    except Exception:
        return False
    if p.scheme != "https" or p.username or p.password or p.fragment:
        return False
    host = (p.hostname or "").lower()
    if kind == "actor":
        return host == ACTOR_HOST and p.path.startswith("/")
    if host not in GITHUB_HOSTS:
        return False
    parts = [x for x in p.path.split("/") if x]
    if host == "api.github.com":
        return (
            len(parts) >= 3
            and parts[0] == "repos"
            and parts[1] == "TTaoGaming"
            and parts[2] in ALLOWED_GITHUB_REPOS
        )
    return (
        len(parts) >= 2
        and parts[0] == "TTaoGaming"
        and parts[1] in ALLOWED_GITHUB_REPOS
    )


def resolve_pointer(payload, pointer):
    if pointer in (None, "", []):
        return payload
    if not isinstance(pointer, list) or not all(isinstance(x, (str, int)) for x in pointer):
        raise ValueError("pointer_type")
    cur = payload
    for part in pointer:
        if isinstance(part, int):
            if not isinstance(cur, list) or part < 0 or part >= len(cur):
                raise KeyError(part)
            cur = cur[part]
        else:
            if not isinstance(cur, dict) or part not in cur:
                raise KeyError(part)
            cur = cur[part]
    return cur


def project(kind, data):
    expected = REQUIRED_KINDS[kind]
    if not isinstance(data, expected):
        raise TypeError(expected.__name__)
    if kind == "actor":
        # Endpoint identity supplies semantic ownership. A response cannot
        # self-declare a different owner or forge provenance metadata.
        out = dict(data)
        out["owner"] = rk.ACTOR_OWNER
        for key in (
            "source_owner",
            "provenance_ref",
            "source_receipt_sha256",
            "self_attested",
            "observed_utc",
        ):
            out.pop(key, None)
        return out
    if isinstance(data, dict):
        out = dict(data)
        for key in (
            "source_owner",
            "provenance_ref",
            "source_receipt_sha256",
            "self_attested",
            "observed_utc",
        ):
            out.pop(key, None)
        return out
    return list(data)


def _auth_headers(kind, url):
    headers = {
        "Accept": "application/json",
        "User-Agent": "hfo-gen142-reconcile-observer/1",
    }
    host = (urlsplit(url).hostname or "").lower()
    token = None
    if host == "api.github.com":
        token = os.environ.get("GITHUB_TOKEN")
    elif kind == "actor":
        token = os.environ.get("SVA_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def http_fetch(url, headers):
    req = Request(url, method="GET", headers=headers)
    with urlopen(req, timeout=15) as resp:
        raw = resp.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("response_too_large")
    return raw


def observe(source_doc, fetcher=http_fetch, now=None):
    if not isinstance(source_doc, dict):
        return hold("SOURCE_DOC_TYPE")
    if source_doc.get("schema") != SOURCE_SCHEMA:
        return hold("SOURCE_DOC_SCHEMA", declared=source_doc.get("schema"))
    sources = source_doc.get("sources")
    if not isinstance(sources, list):
        return hold("SOURCE_LIST_INVALID")

    by_kind = {}
    evidence = {}
    observed_utc = utc_text(now)

    for spec in sources:
        if not isinstance(spec, dict):
            return hold("SOURCE_SPEC_TYPE")
        kind = spec.get("kind")
        if kind not in REQUIRED_KINDS:
            return hold("SOURCE_KIND_INVALID", declared=kind)
        if kind in by_kind:
            return hold("DUPLICATE_SOURCE_KIND", kind=kind)
        url = str(spec.get("url") or "")
        if not trusted_url(kind, url):
            return hold("UNTRUSTED_SOURCE_URL", kind=kind)
        try:
            raw = fetcher(url, _auth_headers(kind, url))
        except Exception as exc:
            return hold("SOURCE_FETCH_FAILED", kind=kind, error=type(exc).__name__)
        if not isinstance(raw, (bytes, bytearray)):
            return hold("SOURCE_FETCH_TYPE", kind=kind)
        raw = bytes(raw)
        if len(raw) > MAX_RESPONSE_BYTES:
            return hold("SOURCE_RESPONSE_TOO_LARGE", kind=kind)
        try:
            payload = json.loads(raw.decode("utf-8"))
            selected = resolve_pointer(payload, spec.get("pointer"))
            data = project(kind, selected)
        except Exception as exc:
            return hold("SOURCE_PROJECTION_FAILED", kind=kind, error=type(exc).__name__)

        by_kind[kind] = data
        evidence[kind] = {
            "authority": "controller_fetch",
            "source_owner": SOURCE_OWNERS[kind],
            "provenance_ref": url,
            "observed_utc": observed_utc,
            "response_sha256": digest_bytes(raw),
            "data_sha256": digest(data),
            "self_attested": False,
        }

    missing = sorted(set(REQUIRED_KINDS) - set(by_kind))
    if missing:
        return hold("REQUIRED_SOURCE_MISSING", missing=missing)

    snapshot = {
        "schema": rk.SCHEMA,
        "policy_version": rk.POLICY_VERSION,
        "actor": by_kind["actor"],
        "demand": by_kind["demand"],
        "dispatches": by_kind["dispatches"],
        "worker_routes": by_kind["worker_routes"],
        "human_boundary": by_kind["human_boundary"],
        "observation": {
            "observer_version": OBSERVER_VERSION,
            "snapshot_observed_utc": observed_utc,
            "evidence": evidence,
        },
    }
    return {
        "decision": "PASS",
        "snapshot": snapshot,
        "snapshot_sha256": digest(snapshot),
        "plan": rk.evaluate(snapshot),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sources")
    args = p.parse_args()
    try:
        source_doc = json.loads(open(args.sources, encoding="utf-8").read())
    except Exception as exc:
        print(json.dumps(hold("SOURCE_DOC_UNREADABLE", error=type(exc).__name__), sort_keys=True))
        return 2
    result = observe(source_doc)
    print(json.dumps(result, sort_keys=True))
    if result["decision"] != "PASS":
        return 2
    return 2 if result["plan"]["decision"] == "HOLD" else 0


if __name__ == "__main__":
    raise SystemExit(main())
