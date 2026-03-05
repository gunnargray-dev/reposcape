from __future__ import annotations

import hmac
from hashlib import sha256

import pytest

from src.web.stripe_webhook import (
    StripeWebhookError,
    parse_stripe_signature_header,
    verify_stripe_webhook,
)


def _sig(payload: bytes, secret: str, ts: int) -> str:
    signed = str(ts).encode("utf-8") + b"." + payload
    return hmac.new(secret.encode("utf-8"), msg=signed, digestmod=sha256).hexdigest()


def test_parse_header_ok() -> None:
    parsed = parse_stripe_signature_header("t=123,v1=abc,v1=def")
    assert parsed.timestamp == 123
    assert parsed.v1_signatures == ("abc", "def")


@pytest.mark.parametrize(
    "header",
    [
        "",
        "v1=abc",
        "t=123",
        "t=notanint,v1=abc",
    ],
)
def test_parse_header_errors(header: str) -> None:
    with pytest.raises(StripeWebhookError):
        parse_stripe_signature_header(header)


def test_verify_ok() -> None:
    payload = b"{\"type\":\"checkout.session.completed\"}"
    secret = "whsec_test"
    ts = 1_700_000_000
    header = f"t={ts},v1={_sig(payload, secret, ts)}"
    verify_stripe_webhook(
        payload=payload,
        signature_header=header,
        webhook_secret=secret,
        tolerance_seconds=300,
        now=ts,
    )


def test_verify_bad_signature() -> None:
    payload = b"{}"
    secret = "whsec_test"
    ts = 1_700_000_000
    header = f"t={ts},v1=deadbeef"
    with pytest.raises(StripeWebhookError):
        verify_stripe_webhook(
            payload=payload,
            signature_header=header,
            webhook_secret=secret,
            now=ts,
        )


def test_verify_out_of_tolerance() -> None:
    payload = b"{}"
    secret = "whsec_test"
    ts = 1_700_000_000
    header = f"t={ts},v1={_sig(payload, secret, ts)}"
    with pytest.raises(StripeWebhookError):
        verify_stripe_webhook(
            payload=payload,
            signature_header=header,
            webhook_secret=secret,
            tolerance_seconds=10,
            now=ts + 100,
        )
