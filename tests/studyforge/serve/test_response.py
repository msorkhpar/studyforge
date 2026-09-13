"""Mirror of `src/studyforge/serve/response.py` (R12)."""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.serve.response import (
    API_VERSION,
    NO_STORE,
    Response,
    envelope,
    error,
    json_response,
)


def test_a_body_response_counts_its_bytes():
    assert Response(200, body=b"12345").length == 5


def test_a_file_response_counts_its_inclusive_span():
    assert Response(206, file=Path("clip"), span=(10, 19)).length == 10
    assert Response(200, file=Path("empty"), span=None).length == 0


def test_a_header_is_found_whatever_its_case():
    response = Response(200, (("Content-Type", "text/plain"),))
    assert response.header("content-type") == "text/plain"
    assert response.header("ETag") is None


def test_the_envelope_leads_with_the_api_version_and_keeps_unicode():
    body = envelope({"title": "café"})
    assert list(json.loads(body)) == ["api", "title"]
    assert json.loads(body)["api"] == API_VERSION
    assert "café".encode() in body
    assert body.endswith(b"\n")


def test_a_json_answer_is_never_stored_unless_its_caller_says_otherwise():
    assert json_response(200, {}).header("Cache-Control") == NO_STORE
    chosen = json_response(200, {}, (("Cache-Control", "no-cache"),))
    assert [v for k, v in chosen.headers if k == "Cache-Control"] == ["no-cache"]


def test_an_error_carries_only_its_message():
    response = error(404, "no such unit")
    assert response.status == 404
    assert json.loads(response.body) == {"api": API_VERSION, "error": "no such unit"}
