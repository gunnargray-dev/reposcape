# Reposcape — Session Log

This file is updated at the end of every autonomous dev session.

---

## Session 51 (2026-03-05)

**PR:** #61 (squash merged)

### Focus
Security hardening: remove server-side GitHub OAuth token on logout + document token DB configuration.

### Shipped
- Logout (`POST /auth/logout`) now deletes the stored OAuth token row for the active GitHub login (in addition to clearing auth cookies).
- Adds `delete_token()` to `src/web/auth/token_store.py`.
- README now documents `REPOSCAPE_TOKENS_DB` (default path + schema).

### Tests
- `python -m pytest tests/web/test_auth_cookie.py -q --tb=short`
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

---

## Session 49 (2026-03-05)

**PR:** #59 (squash merged)

### Focus
Security hardening: migrate GitHub OAuth access token storage from client-side cookie to server-side persistence.

### Shipped
- Adds `src/web/auth/token_store.py`: a tiny stdlib SQLite token store keyed by GitHub login.
- GitHub OAuth callback now persists the token server-side and stores only `{v, iat, login}` in the signed cookie.
- `get_user_session()` loads the access token from the server-side store.

### Tests
- `python -m pytest tests/web/test_auth_cookie.py -q --tb=short`
- `python -m pytest tests/web/test_stripe_webhook.py -q --tb=short`

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

## Session 48 (2026-03-05)

**PR:** #58 (squash merged)

### Focus
Tie Stripe Checkout purchases to the authenticated user identity (GitHub OAuth) so Pro/private repo access can be granted to `gh:<login>` rather than relying on email matching.

### Shipped
- Stripe client: support optional `client_reference_id` and `metadata[...]` when creating Checkout Sessions (stdlib HTTP).
- Billing checkout: passes `subject_for_request()` (usually `gh:<login>`) into the Stripe Checkout Session.
- Billing webhook: grants Pro entitlement to a stable subject (client_reference_id/metadata) with email fallback.

### Tests
- `python -m pytest tests/web/test_stripe_webhook.py -q --tb=short`

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
- Export: fix snapshot zip file naming and add better error messages.
- Export: allow choosing a release tag for snapshot bundle downloads.

### Tests
- `python -m pytest tests/web/test_export_snapshots.py -q --tb=short`

---

## Session 39 (2026-03-05)

**PR:** #47 (squash merged)

### Focus
Historical tracking: add multi-metric toggles for /api/snapshots/series.

### Shipped
- Dashboard: multi-metric overlay/toggles for snapshot series chart.

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
