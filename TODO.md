# 🎯 FOCUS

---

# 🧠 BRAIN DUMP
- Convert 'update_business_hours' and 'delete_business_hours' to a direct UPDATE with rowcount instead of SELECT-then-change: the fetched row is never used (the delete router already answers 204 and discards it), so each mutation would go from 2 DB round-trips to 1 and the "not found" guard becomes rowcount == 0.
- Convert 'delete_worker' (soft delete) to a direct UPDATE of is_active=False with rowcount: same reason as business hours, the frontend never reads the returned worker, it just refetches the list.
- Low priority: 'update_worker_hours', 'delete_worker_hour' and 'delete_service' could also be UPDATE/DELETE + rowcount, but their WHERE needs a subquery to check the worker belongs to the business (or drags a test change along) - do them last, if ever. For 'delete_service' the real pending fix is the FK bug when the service has appointments linked.
- Before testing backend introduce all the seed data
1. Redis context structure
6. webhook payload validation
7. duplicate webhook/idempotency
- Fix bug when business isnt introduced in the database

- Fix bug when deleting or modifyinfg a service that has appointments linked to.
- Add functionality so business owner can modify his business information
- Develop secondary buttons (needed for the navbar for example)
- Check why are we getting "GET /health HTTP/1.1" 404 Not Found"


- Security and integrity
8. authentication
9. authorization
10. password hashing
11. business-scoped mutations
12. Meta webhook signature validation

- Improve architecture as the project grows
13. database migrations
14. timezone model
15. data constraints
16. better error handling
17. better AI context management
- Problem of data consistency when data gets modified by AI with tools and not via mutations, for the moment I would just set a refetchInterval but in the future I have to do some research on websockets.
- Research if composite index are worth it for appointment (start_time and end_time)
- I should look how to append to the number of the phone the business owner introduce the prefix, because meta returns to me (3466578907) and a owner could write (66578907). I could just add a place where the prefix of the phone could be selected and set as default the country from where the business is.
- Center day selector and button for small devices.
- Make assistanfy multilanguage (i18next for de frontend) and research what to do in the backend (for ai errors and maybe backend errors)


       
---

# ✅ WINS
- Modify 'get_first_available_worker' so that it orders by the worker with less appointments assigned so it's fair for every worker.
- Mock login
- Long names doesn't appear in the appointment (do some research)
- style 404 page
- Configurations may be aligned to the center horizontally in small devices
- Develop delete endpoint and service function in the backend for appointments and then connect with the frontend (also I have to add icons, handler and that kind of stuff)
- Develop post endpoint and service function in the backend for appointments and then connect with the frontend (also I have to add icons, handler and that kind of stuff)
- Develop get endpoint and service function in the backend for appointments and then connect with  the frontend
- [x] Fix bug when toggling BusinessHours data inside it erases
- [x] Fix bug when toggling a day, that doesn't turns off. Although network says it's okey it doesn't update the database.
- [x] Create worker hours from the frontend (maybe I should change the toggle thing before, we would investigate it)
- Fix bug when toggling day failing and showing that added correctly
 - [x] Currently implementing the functionality to see the worker hours for each worker. It happened a problem because I have  strange methods that I think I am going to refactor and my backend gives "09:00:00" and this methods accept "09:00" to do their conversion.
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
la tarea consiste en instalar y aprender como funciona react-router-dom
- [x] Create todos
- [x] Refactor svgs from /business so they are a component
