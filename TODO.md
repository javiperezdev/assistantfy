# 🎯 FOCUS
Develop get endpoint and service function in the backend for appointments and then connect with  the frontend
---

# 🧠 BRAIN DUMP
- Develop delete endpoint and service function in the backend for appointments and then connect with the frontend (also I have to add icons, handler and that kind of stuff)
- Develop endpoints and service functions in the backend for appointments and then connect with the frontend (also I have to add icons, handler and that kind of stuff)
- Before testing backend introduce all the seed data
1. Redis context structure
6. webhook payload validation
7. duplicate webhook/idempotency
- Investigar como crear rutas privadas para usuarios loggeados
- style 404 page
- Fix bug when business isnt introduced in the database
- Modify 'get_first_available_worker' so that it orders by the worker with less appointments assigned so it's fair for every worker.
- Fix bug when deleting or modifyinfg a service that has appointments linked to.
- Fix bug when toggling day failing and showing that added correctly
- Add functionality so business owner can modify his business information
- Configurations may be aligned to the center horizontally in small devices
- Appointments title should be inside a column with the button in small devices
- Long names doesn't appear in the appointment (do some research)
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



       
---

# ✅ WINS
- [x] Fix bug when toggling BusinessHours data inside it erases
- [x] Fix bug when toggling a day, that doesn't turns off. Although network says it's okey it doesn't update the database.
- [x] Create worker hours from the frontend (maybe I should change the toggle thing before, we would investigate it)
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
