# Reposcape Session Log

This file tracks what each scheduled session shipped.

---

## Session 44 (2026-03-05)

**PR:** #53 (squash merged)

### Focus
Pro tier UX: cookie-based entitlement placeholder to unblock end-to-end Upgrade flow.

### Shipped
- Billing: `/billing/success` now sets an HttpOnly Pro cookie and redirects to `/dashboard`.
- Pages: dashboard template context now checks Pro entitlements per-request (env var OR cookie), enabling watermark removal after “Upgrade”.
- Add `src/web/entitlements/` package to centralize request-based gating.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`
- `python -m pytest tests/web/test_og.py -q --tb=short`

---

## Session 43 (2026-03-04)

**PR:** #52 (squash merged)

### Focus
Pro tier: Stripe env helpers (enabled flag + secret/webhook/price IDs) + wire billing stub to use them.

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
UI: snapshot metric chips for Snapshot B.

### Shipped
- Dashboard Snapshots: show a compact chip bar for Snapshot B (as_of, total_source_lines, file count, TODOs, debt, average complexity).
- UI polish: minor spacing + status messaging improvements.

### Tests
- `python -m pytest tests/web/test_story_route.py -q --tb=short`

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
