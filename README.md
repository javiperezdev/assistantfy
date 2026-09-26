# Assistantfy

AI agent capable of managing all client bookings, cancelling appointments, and answering questions about schedules and services while keeping the data reliable.

## 📦 Technologies

* Python
* FastAPI
* PostgreSQL
* Redis
* Vite
* React.js
* TypeScript
* Docker

## 🦄 Features

Here's what you can do with Assistantfy:

* As a client, you can chat via WhatsApp in order to book and cancel an appointment, as well as get your questions answered (schedules, services...).

* As a business owner, you can configure your business (workers, services, worker-service assignments, and business hours).

* And we are on the way to implementing a functionality to view all your appointments.

## 📚 What I Learned

Maybe it's difficult to put into words everything I have learned while developing this project:

* Learned how to use new technologies such as FastAPI, PostgreSQL, React, TypeScript, Docker, Redis and Git.

* How to consume AI through APIs, how to keep the context of the model through the conversation, prompting and how to create an agent loop so AI could have access to tools.

* Consume the WhatsApp API and send messages with background tasks (from FastAPI).

It's a little bit of a vague and short description because this project changed the way I think about the quality of the software I am building. I have had my ups and downs with the project, but I have consistently kept pushing and learning, which was the objective.

## 🚦 Running the Project

To run the project in your local environment, follow these steps:

1. Clone the repository to your local machine.

2. Create a `.env` file with all the required API keys.

3. Register with Meta for Developers (get the keys).

4. Install the required dependencies.

5. Execute `docker compose up -d` in the terminal.

6. Open WhatsApp if you want to use the client side, or http://localhost:5173 if you want to test the business owner side.

## 🍿 Video

Coming soon...
