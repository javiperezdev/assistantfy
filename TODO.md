# TODO

## Ship blockers
- HTTPS with Caddy, one origin for API + frontend, 443 only.
- Serve the built frontend, not the Vite dev server.
- Dedup Meta webhooks by message id.
- Secure cookies + HSTS.
- Rotate AI/WhatsApp keys, add `.env.example`, drop `--reload` and bind-mounts, pin images.
- Close Docker ports at the provider firewall (UFW does not filter them).
- Unique phone number.
- Service delete with linked appointments: 409 or soft-delete, not a raw 500.

## Data
- Alembic migrations first, then constraints (day_of_week 1-7, end > start, positive price/duration, NOT NULL).
- Encrypted `pg_dump` backups + one real restore test.
- Least-privilege Postgres role.
- Harden webhook payload validation; validate IANA timezones at input.
- Global exception handler + Sentry; add `/health` only when something consumes it.

## Product
- Spanish UI (i18next) + translated backend/AI messages.
- Password reset, invite business by email, owner edits business info.
- Reply to non-text messages before reading the phone.
- Phone prefix normalization; phone must match Meta's display number.
- Cap AI context per business/phone in Redis.
- Refresh frontend after AI mutations (refetch now, websockets later).
- Seed data for backend tests.

## Later
- Fair worker assignment: pick the worker with fewest appointments.
- Long names in the appointment UI.
- Day toggle shows success even when it fails.
- Direct UPDATE + `rowcount` instead of SELECT-then-change.
- Remove stale comment and `print()`; revisit composite index.
- Center selectors/buttons on small screens; secondary navbar buttons.

## Verify before launch
- Auth, tenant scoping, Argon2id, login rate limit, background session under load.

Done work lives in git history.
