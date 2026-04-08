# ASSISTANTFY
Assistantfy is a personal project designed as a software solution for service-based businesses to have an affordable, 24/7 assistant. This gives owners more time to focus on their core services instead of administrative tasks like scheduling appointments. It also allows businesses to reach clients who contact them after hours, as Assistantfy never sleeps.

### 2026-03-06
Today, I configured the virtual environment, deployed the server, and created the .gitignore. I developed a POST endpoint to send messages and a GET endpoint to retrieve all sent messages. I also established a Pydantic BaseModel for the Message entity. I’m happy with the progress made today. Over the next few hours (or tomorrow), I plan to connect the system to the WhatsApp API. 

At midnight, I implemented and learned about raising exceptions, changed the list to view all the messages, for a dictionarie which has much less time complexity, tomorrow I would focus in learning how to connect with whatsapp.

### 2026-03-07
Today, I learned who to configue the .env, how to access to the variables, how to use BaseSettings and I am understandig how whatsapp API works, so later I would at least get the verification from the API with the webhook

to conclude the day, I learned what ngrok is and how to use it, I got the verification whatsapp API which means that I integrated the API successfully and I learned concepts such as query params and why do you need to use 'Alias'. Overrall I am really happy on how I am developing and learning from this project, keeping this progress log is making things easier and more fulfilling.

### 2026-03-08
Today I only implemented, the post for the webhook, from there I would receive the messages from the future, currenty it just prints the raw JSON, just for testing reasons.

### 2026-03-09
I am really excited, to tell that I have implemented the functionality to receive whatsapp messages, the nested json was a hard concept to grasp and I was working in the send_messages() method, by tomorrow this would be finished.

### 2026-03-10
I learned about the Requests library how it works and how to debug responses (using 'response.text' and 'response.status_code'). I also implemented the method to send messages (without AI responses for now, obviously). Apart from these successes, I still need to resolve the events for reading messages, which are currently returning a 422 Unprocessable Entity error.

### 2026-03-11
I fixed the bug with message status updates ('read', 'sent', 'delivered'). The fix was just allowing the message list to be None. I also added a statuses attribute to the Value class to print events to the terminal for easier debugging

### 2026-03-12
Today, I learned about APIRouters. I ran into some routing issues, but I resolved them by consulting the FastAPI documentation and using AI to troubleshoot the logic. I'm excited to have a clean foundation and a great starting point for AI implementation. Additionally, I wrote the project's README, a necessary step as I intend to make the repository public.


### 2026-03-14
This morning was tough, I struggled a lot with new concepts like the State object and lifespan. However, it was all to make my app more efficient and powerful, which I believe is necessary. I didn't make huge strides in terms of raw lines of code, but I’ve greatly improved my understanding of how FastAPI and this app work. I now have a solid foundation to implement AI tomorrow.

In terms of productivity, I replaced the requests library with httpx for asynchronous support. I initialized httpx.AsyncClient in the main app state, which is much more efficient than initializing it for every message. The cost of keeping it open is minimal. Additionally, I managed to use @asynccontextmanager to initialize the client and tear it down properly when the server shuts down.

### 2026-03-15
I’ve refactored how I’m sharing the httpx_client to follow better practices and avoid future headaches. In doing so, I realized I had a misunderstanding of "lifespan." I previously treated it as a single global entity (server startup/shutdown), but I’ve now correctly implemented it at the request level. This specifically solved an issue that was driving me crazy in routers/whatsapp when calling send_message.

I also integrated the AI implementation into the request lifespan, alongside the httpx client. I’m currently weighing an architectural decision regarding which service should be responsible for sending messages: 'ai_service' or 'whatsapp_service'. I have valid arguments for both, but this is something tomorow would be solved

### 2026-03-16
Thanks to the hard work I put in yesterday and how quickly I grasp concepts, implementing the AI was actually quite easy. There’s still a long way to go. I need to refine the parameters like temperature but I’ve officially finished the integration. I’m really excited about how fast I’m learning and making progress!

### 2026-03-17 
Today I haven't coded anything, but I learned about dependency injection. I’ve decided to implement a database to manage clients, appointments, and services. Since I've already designed the E/R, I just need to learn how to implement it in the FastAPI ecosystem using its libraries and tools

### 2026-03-18
Today I was in a rush. I hope I can continue working over the next few hours. So far, I have learned SQLModel, its syntax, and the logic, and I've implemented the classes that I designed yesterday.

Luckily, I got some time for the project and just configured database.py. I’ve decided to use SQLite for the development stage because it is the easiest to implement, which I think is crucial right now.

I learned how to create the database and the engine, even it was mostly boilerplate code, but I learned what was happening under the hood, which helped me make better decisions. One curious thing I found was that if you don’t import the models in main, the database won't actually create the tables. That’s why I imported all the classes from models, even though the editor is marking them as unused.

### 2026-03-19
This morning felt really productive; I’ve grasped the core concepts and made some key architectural decisions. For now, the workflow I’m planning to ensure the best UI/UX chatting experience is as follows:
    The client sends a message.
    My server receives it and calls search_clients_by_phone_number.
    It delivers that information (either None or the Client info) to the AI.

Another crucial step is crafting a robust system prompt to minimize hallucinations.

I learned a lot while building the client router. Before implementing the 'add user' functionality, I had the session dependency injected directly into services/client_service. However, I realized this was inefficient; doing the same in my method would have resulted in two separate database hits.

To fix this, I removed the Depends from client_service and search_client_by_phone_number. Now, they simply accept a session parameter passed from the client router, which handles the get_session dependency injection.

Additionally, I learned that raising HTTP status codes directly to LLMs isn't ideal. It’s much more effective to apply defensive programming techniques instead.

### 2026-03-25
Luckily, I got some time to work on my project. I was anxious because the development is becoming difficult; designing a system for AI is a paradigm shift for me. AI requires a specific way of programming that is as mind-blowing as it is beautiful. The only thing I’m not liking is that it is based on probabilities, but that is simply what AI is.

On the productivity side, I developed the logic behind getting empty slots and developed the router and schema for AI tools, for now I just built the one for this functionality (a really impressive thing I learned today). By the way, I am securing my prompts, as they are my business logic.

Later on the day, I had refactor a lot of methods to made code cleaner and implemented the functionality of adding appointments which was hard. Appart from that I had been reading that for call tooling is better to use 'post', which is something I have to research

### 2026-03-26
Today is the day that things change wildly:
- We are changing from a single tenant to a multiple tenant, this means:
    - Migrate database to postgreSQL
    - Modify services to work for this architecture

Number one priority is creating the postgreSQL database in docker, then all the models to support the new multi-tenant schema and after that refactor the complete app, fix bugs and code that is not working due to the migration from sqlite to postgre. The good news are that for the frontend we will use a low-code open source tool called appSmith, which will lead us finishing the mvp before than expected.

### 2026-03-27
I am happy because today we advanced a lot, I migrated from sqlite to postgre, database is functional, also I have my software broken because I didn't know what branches were, but I would use them when I solve this problems. By the way I am using the asynchronous driver of postgre, which was a little bit mind blowing at the begining.

Later I solved a problem I had with the main not recognizing appointment_service module

### 2026-03-29
Today I inserted a business to test how the database works, and to develop the get_available_slots method

### 2026-03-30 
Developing get_available_slots is getting really hard, but I will finish it soon, I just want to make sure I am doing it right and learning on the way. Today's struggle was dealing with the objects that returns the ORM, which obviously aren't the same as when you use raw sql.

### 2026-04-01
This morning, I built the logic for the get_available_slots, even though the method is robust I realized that what happens if workers have different work hours, or even if they have the same, my method isn't able to handle more than one worker, so I would change the schema to include worker hours and after that I would change the get_available_slots to make possible to include various workers.

During the night, I got some things done such as defining what I really want to do with this method, which is a thing of genious, now time complexity would be O1, it would be fastest and easy to test. I decided to do bulk querys instead of a lot, just as much as workers has a business, and make all the calculations with ram using python and making it easy with sets and dictionaries

### 2026-04-03
This morning I finished the get_available_slots method and I had been testing it, with data from postgres, It is working really nice even with multiple workers which was my biggest headache durind development, in the future I need to create tests for this method because it's crucial.

The method to add appointments is also working as expected, but I have to add the functionalitie of checking if that appointment exists.

### 2026-04-04
All routers and functionalities are working as expected, I am really happy about this, I have a lot of ideas to make the system more ai-friendly, which also make it more robust. I haven't done nothing new in this days, I just focused on making everything work well (next time I would use github branches), and making it much more professional. 

One of the functionalities I have developed, is a method that gets the closer dates for a requested date and conects it with the get_availability router so it gives new dates, until it gets to 7 day, if in 7 days it doesn't have any slot. A dict is given to ai, with instructions of what to do