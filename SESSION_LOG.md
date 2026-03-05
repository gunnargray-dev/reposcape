# Reposcape  Session Log

This file is updated at the end of every autonomous dev session.

---

## Session 47 (2026-03-05)

**PR:** #56 (squash merged)

### Focus
Introduce a real user identity system (GitHub OAuth) as a foundation for Pro + private repo access.

### Shipped
- Adds GitHub OAuth login routes: `/auth/github/login` + `/auth/github/callback`.
- Stores GitHub login + access token in an HMAC-signed cookie (requires `REPOSCAPE_WEB_SECRET`).
- Adds `src/web/auth/session.py` to read the auth cookie into a typed `UserSession`.
- Adds identity-aware entitlement check (`src/web/entitlements/identity.py`) that prefers `gh:<login>` when authenticated, with email query fallback.
- Dashboard now uses identity-aware Pro entitlement checks.

### Tests
- `python -m pytest tests/web/test_auth_cookie.py -q --tb=short`

---


## Session 45 (2026-03-05)

**PR:** #54 (squash merged)

### Focus
Use real Stripe Checkout Sessions (stdlib HTTP) and add a webhook verifier endpoint.

### Shipped
- `POST /api/billing/checkout` now creates a Stripe Checkout Session and returns `checkout_url`.
- Adds `src/web/stripe_client.py` (minimal Stripe API client) and `src/web/stripe_webhook.py` (signature parsing/verification).
- Adds `POST /api/billing/webhook` to verify Stripe-Signature (stdlib HMAC) and (temporarily) grant Pro cookie on `checkout.session.completed`.
- Updates ROADMAP.

### Tests
- `python -m pytest tests/web/test_stripe_webhook.py -q --tb=short`

---

## Session 44 (2026-03-05)

**PR:** #53 (squash merged)

### Focus
Add a placeholder Pro entitlement so the dashboard can hide watermark + show upgrade CTA.

### Shipped
- Add `src/web/entitlements/cookies.py`: tiny cookie-based entitlement helper.
- `/billing/success` sets HttpOnly cookie and redirects to `/dashboard`.
- Dashboard template uses request-based entitlement check.
- Updates ROADMAP.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/web/test_og.py -q --tb=short`

---

## Session 43 (2026-03-05)

**PR:** #52 (squash merged)

### Focus
Billing: centralize Stripe env reading.

### Shipped
- Add `src/web/stripe_env.py` to centralize reading Stripe env vars (`REPOSCAPE_BILLING_ENABLED`, `REPOSCAPE_STRIPE_SECRET_KEY`, `REPOSCAPE_STRIPE_WEBHOOK_SECRET`, `REPOSCAPE_STRIPE_PRICE_ID`).
- Billing route: returns 501 when billing is not enabled.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 42 (2026-03-05)

**PR:** #50 (squash merged)

### Focus
Start wiring the Pro upgrade flow: stable billing endpoints and a real dashboard Upgrade action.

### Shipped
- Server: adds `src/web/routes/billing.py` with stable endpoints:
  - `POST /api/billing/checkout` (stub returning internal redirect for now)
  - `GET /billing/success`
  - `GET /billing/cancel`
- Dashboard: adds watermark CTA + Upgrade click handler that calls `/api/billing/checkout` and redirects to `checkout_url`.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 41 (2026-03-05)

**PR:** #49 (squash merged)

### Focus
Paid tier stub: Pro gating + watermark CTA.

### Shipped
- Add `src/web/pro.py` with env-flag gating (`REPOSCAPE_PRO`).
- Dashboard: show a watermark/upgrade CTA when Pro is disabled.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 40 (2026-03-05)

**PR:** #48 (squash merged)

### Focus
Pro tier: improve snapshot export bundling + fix edge cases.

### Shipped
- Snapshots: zip bundling now uses stable ordering and avoids including hidden files.
- API: `/api/snapshots/{owner}/{repo}/download` now supports optional `tag` parameter.
- UI: add more explicit download messaging in dashboard.

### Tests
- `python -m pytest tests/test_history.py -q --tb=short`

---

## Session 39 (2026-03-05)

**PR:** #47 (squash merged)

### Focus
UI: snapshot timeline sparkline.

### Shipped
- Dashboard Snapshots: adds a small sparkline SVG showing snapshot frequency over time.
- API: add `GET /api/snapshots/{owner}/{repo}/series` (initial seed; expanded later).

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 38 (2026-03-05)

**PR:** #51 (squash merged)

### Focus
Pro tier: Stripe env helpers (enabled flag + secret/webhook/price IDs) + wire billing stub to use them.

### Shipped
- Add `src/web/stripe_env.py` to centralize reading Stripe env vars (`REPOSCAPE_BILLING_ENABLED`, `REPOSCAPE_STRIPE_SECRET_KEY`, `REPOSCAPE_STRIPE_WEBHOOK_SECRET`, `REPOSCAPE_STRIPE_PRICE_ID`).
- Billing route: returns 501 when billing is not enabled.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 46 (2026-03-05)

**PR:** #55 (squash merged)

### Focus
Start persisting Pro entitlements (webhook-driven) so Pro can be restored across sessions.

### Shipped
- Add SQLite-backed entitlement store keyed by email (`src/web/entitlements/store.py`).
- Stripe webhook: persist Pro grant when checkout email is present.
- Add `/billing/restore` flow to restore Pro cookie from stored entitlement.
- Dashboard Pro gating checks cookie/env override first, then best-effort `?email=` entitlement lookup.

### Tests
- `python -m pytest tests/web/test_stripe_webhook.py -q --tb=short`
- `python -m pytest tests/web/test_entitlements_store.py -q --tb=short`
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
