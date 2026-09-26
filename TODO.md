# 🎯 FOCUS
3. inactive Worker/WorkerHours filtering

---

# 🧠 BRAIN DUMP
- *Priority*
1. Redis context structure
2. business_id + phone_number Redis isolation
- add business_id to all queries to ensure multitenancy
4. WorkerHours actually being persisted
5. long-message return bug
6. webhook payload validation
7. duplicate webhook/idempotency

- Investigar como crear rutas privadas para usuarios loggeados
- style 404 page
- Fix bug when business isnt introduced in the database
- Check how are workers being assigned for each task
- Create functionality to manage workerHours from the frontend (also develop endpoints in the backend)
- Modify 'get_first_available_worker' so that it orders by the worker with less appointments assigned so it's fair for every worker.
- Fix bug when deleting or modifyinfg a service that has appointments linked to.
- when a message arrives I should check if it isn't text so I would answer that the format is not supported try sending a text message...


- Security and integrity
8. authentication
9. authorization
10. password hashing
11. business-scoped mutations
12. Meta webhook signature validation
Improve architecture as the project grows
13. database migrations
14. timezone model
15. data constraints
16. better error handling
17. better AI context management


       
---

# ✅ WINS
- [x] Review the methods related with checking available slots because they are giving bugs
- [x] Inject service catalogue creating a catalogue of services
- [x] Give states to an appointment (Booked, cancelled, no_show, completed)
- [x] Think about what to implement in the dashboard
- [x] Crear Pagina para el error 404 mostrando pagina no encontrada
- [x] Crear boton de retorno del menu de settings al dashboard
- [x] Crear la funcionalidad para que al clicar boton de settings nos lleve a settings.
la tarea consiste en instalar y aprender como funciona react-router-dom
- [x] Create todos
- [x] Refactor svgs from /business so they are a component
