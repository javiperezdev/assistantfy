# Pre-Deployment TODO

Ordered by what actually blocks shipping. 🔴 must be fixed before the MVP goes live. 🟠 is cheap insurance. 🟡 can ride behind.

---

## 🔴 BLOCKERS — fix before shipping

### Security
- Phone number must be unique

- [ ] **Webhook idempotency / dedup**
  Meta retries deliveries. Without a message-ID dedup (Redis `SETNX` on `value.messages[0].id`), duplicates double-book, double-reply and double-charge.
- [ ] **Redis auth + isolation**
  - [ ] `requirepass` in Redis + `REDIS_URL` with a hex password (`openssl rand -hex 24`)
  - [ ] Fix healthcheck: `redis-cli -a "$REDIS_PASSWORD" ping`
  - [ ] Remove `ports:` from `db` and `redis` in `docker-compose.yml` (min acceptable: `127.0.0.1:5433:5432`)
- [ ] **Session cookies secure in production**
  - [ ] `SESSION_COOKIE_SECURE=true` + HSTS (only after TLS is live)
- [ ] **Secrets hygiene**
  - [ ] `chmod 600 .env`
  - [ ] Create `.env.example` with placeholders
  - [ ] Rotate `AI_API_KEY` and `WHATSAPP_TOKEN` at deploy (WhatsApp token changes per server)

### Production build / serving
- [ ] **Reverse proxy with TLS (Caddy): 443 only, API + frontend on the same origin**
- [ ] **Build the frontend for production** (`npm run build` + static serve) — it currently ships the Vite dev server (`frontend/Dockerfile:7`)
- [ ] **Remove dev conveniences**: `--reload` (`docker-compose.yml:46`), code bind-mounts (`:35,57`), pin image versions

### Correctness / data safety
- [ ] **Fix service delete/modify when appointments are linked**
  `service_service.py:51` deletes with no error handling → FK `IntegrityError` → raw 500. Decide: 409, soft-delete, or cascade.
- [ ] **Fix the "business not in DB" case**
  `whatsapp.py:43` → `ai_service.py:27` runs `ZoneInfo(business.timezone)` on `None` → swallowed by the broad `except`; also leaks `context:None:<phone>`. Guard early + log explicitly.

---

## 🟠 STRONGLY RECOMMENDED — do now

- [ ] Multilanguage (At least spanish now): i18next on the frontend; research backend (AI + API error messages)
- [ ] **Database migrations (Alembic)** — schema is only `create_all` today (`database.py:17`)
- [ ] **Least-privilege Postgres role** (`assistantfy_app`, no superuser); app connects with it, not `admin`
- [ ] **Backups**: client-side encrypted `pg_dump` (age/gpg) + private bucket + a real restoration test
- [ ] **Provider security group / `DOCKER-USER` rules** (UFW does not filter Docker ports)
- [ ] **`/health` endpoint + `api` container healthcheck** — this is the "GET /health 404"
- [ ] **Global exception handler** (clean 500s, no stack-trace leaks) + initialize Sentry (already in `requirements.txt`)
- [ ] **Data constraints**: `CHECK` on `day_of_week` 1–7, `end_time > start_time`, positive price/duration, `NOT NULL` where required
- [ ] **Webhook payload validation hardening** (malformed/absent `entry`/`value` currently relies on a broad try/except)
- [ ] **Timezone model**: validate IANA names at input (`ZoneInfo` currently raises at runtime on bad data)

---

## 🟡 POST-MVP / NICE-TO-HAVE

### Bugs & polish
- [ ] Non-text messages reply to `None` phone (`whatsapp.py:47` — `client_phone_number` not set yet)
- [ ] Phone prefix normalization (`3466578907` vs `66578907`); setup trap: `Business.phone_number` must match Meta's `display_phone_number` exactly
- [ ] Center day selector and button for small devices
- [ ] Develop secondary buttons (navbar)
- [ ] Stale comment in `models.py:61` claims a composite index that doesn't exist; remove leftover `print()` in `available_slots.py:30`
- [ ] Research composite index on appointment (`start_time`, `end_time`) — overlap is already guarded by the gist exclusion constraint

### Features
- [ ] Add invite script (invite a business via email)
- [ ] Implement "I forgot my password"
- [ ] Business owner can modify their business info
- [ ] Better AI context management + cap context growth (Redis `context:{business}:{phone}`)
- [ ] Data consistency when AI mutates data vs frontend mutations (temporary `refetchInterval`; research websockets later)
- [ ] Seed data before backend testing

### Refactors (perf, not blocking)
- [ ] `update_business_hours` / `delete_business_hours` / `delete_worker`: direct UPDATE + `rowcount` instead of SELECT-then-change (2 round-trips → 1)
- [ ] Low priority: `update_worker_hours`, `delete_worker_hour`, `delete_service` same pattern (WHERE needs a subquery)

---

## 🔍 VERIFY BEFORE LAUNCH (likely implemented — confirm with tests)

- [ ] Authentication (login / logout / me)
- [ ] Authorization / tenant scoping (`require_business_id`, tenant-isolation tests)
- [ ] Password hashing (Argon2id)
- [ ] Business-scoped mutations
- [ ] Login rate limiting
- [ ] Background-task session lifetime: the webhook passes the request `session` to `generate_response`; SQLAlchemy sessions are reusable after `close()`, but confirm under load

---

# ✅ WINS
- [x] **Meta webhook signature validation (`X-Hub-Signature-256`)**
  `routers/whatsapp.py:35` processes any `POST /webhook`. Without HMAC verification anyone can send fake messages, book/cancel appointments as any client, spam WhatsApp as the business, and burn DeepSeek credits. Verify HMAC-SHA256 of the *raw* body against the Meta App Secret.
- Modify 'get_first_available_worker' so that it orders by the worker with less appointments assigned so it's fair for every worker.
- Mock login
- Long names doesn't appear in the appointment (do some research)
- style 404 page
- Configurations may be aligned to the center horizontally in small devices
- Develop delete endpoint and service function in the backend for appointments and then connect with the frontend (also I have to add icons, handler and that kind of stuff)
- Develop post endpoint and service function in the backend for appointments and then connect with the frontend (also I have to add icons, handler and that kind of stuff)
- Develop get endpoint and service function in the backend for appointments and then connect with the frontend
- [x] Fix bug when toggling BusinessHours data inside it erases
- [x] Fix bug when toggling a day, that doesn't turns off. Although network says it's okey it doesn't update the database.
- [x] Create worker hours from the frontend (maybe I should change the toggle thing before, we would investigate it)
- Fix bug when toggling day failing and showing that added correctly
- [x] Currently implementing the functionality to see the worker hours for each worker. It happened a problem because I have strange methods that I think I am going to refactor and my backend gives "09:00:00" and this methods accept "09:00" to do their conversion.
- [x] long-message return bug
- [x] business_id + phone_number Redis isolation
- [x] when a message arrives I should check if it isn't text so I would answer that the format is not supported try sending a text message...
- [x] Check how are workers being assigned for each task
- [x] add business_id to all queries to ensure multitenancy
- [x] inactive Worker/WorkerHours filtering
- [x] Review the methods related with checking available slots because they are giving bugs
- [x] Inject service catalogue creating a catalogue of services
- [x] Give states to an appointment (Booked, cancelled, no_show, completed)
- [x] Think about what to implement in the dashboard
- [x] Crear Pagina para el error 404 mostrando pagina no encontrada
- [x] Crear boton de retorno del menu de settings al dashboard
- [x] Crear la funcionalidad para que al clicar boton de settings nos lleve a settings.
- La tarea consiste en instalar y aprender como funciona react-router-dom
- [x] Create todos
- [x] Refactor svgs from /business so they are a component
