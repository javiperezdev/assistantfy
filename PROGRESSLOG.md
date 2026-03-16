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
Thanks to the hard work I put in yesterday and how quickly I grasped the concepts, implementing the AI was actually quite easy. There’s still a long way to go. I need to refine the parameters like temperature but I’ve officially finished the integration. I’m really excited about how fast I’m learning and making progress!