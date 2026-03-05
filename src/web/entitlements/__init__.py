"""Entitlements package.

This package holds small, dependency-free helpers for determining whether a
request has access to paid features.

The initial implementation is a simple cookie-based entitlement flag set by
billing success redirects. Later sessions can replace this with a Stripe
webhook-backed store.
"""
