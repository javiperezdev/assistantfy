 # Assistantfy

![Logo](assets/logo.png)

*An enterprise-grade B2B SaaS backend designed to transform LLMs into autonomous agents for real-time business operations and booking management.*

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-FF4438?style=for-the-badge&logo=redis&logoColor=white)

---

## 🌟 Highlights

*   **🚀 24/7 Autonomous Operations:** Automates end-to-end appointment scheduling and FAQ handling.
*   **🧠 LLM-Powered:** Moves beyond simple chatbot scripts for natural, dynamic conversation.
*   **⚡ Extensible Architecture:** Modular tool-calling engine for easy feature additions.
*   **🔒 Multi-tenant:** Robust database schema ensuring strict data isolation.
*   **🧠 Stateful Loops:** Uses Redis to maintain context across long-term conversations.

---

## ℹ️ Overview

Assistantfy empowers local businesses (clinics, salons, etc.) by acting as an affordable, 24/7 autonomous virtual assistant. It moves beyond simple chatbot scripts by utilizing LLMs to manage end-to-end appointment scheduling, FAQ handling, and dynamic conversation management—enabling business owners to focus on operations while the agent handles customer interaction.

---

## 🚀 Usage

Assistantfy is designed to integrate into your business messaging flows.

### Examples of Interaction Flow

#### Checking for availability and booking
![Example of booking](assets/DELETE.png)

#### Cancel an appointment
![Example of booking](assets/GetAVandBookAPP.png)

---

## 🏗 DB Architecture

```mermaid
erDiagram
    %% CORE TENANT & AUTHENTICATION
    BUSINESS {
        int id PK
        string phone_number
        string name
        string timezone
    }

    ADMIN_USER {
        int id PK
        int business_id FK
        string email UK "Unique"
        string hashed_password
        boolean is_active
    }

    BUSINESS_HOURS {
        int id PK
        int business_id FK
        int day_of_week "1=Mon, 7=Sun"
        time start_time
        time end_time
    }

    %% RESOURCES & SKILLS
    WORKER {
        int id PK
        int business_id FK
        string name
    }

    WORKER_HOURS {
        int id PK
        int worker_id FK
        int day_of_week
        time start_time
        time end_time
    }

    SERVICE {
        int id PK
        int business_id FK
        string name 
        float price 
        int duration_minutes 
    }

    WORKER_SERVICE {
        int worker_id PK,FK "Points to Worker.id"
        int service_id PK,FK "Points to Service.id"
    }

    %% CUSTOMERS
    CLIENT {
        int id PK
        int business_id FK
        string phone_number UK "Unique per Business"
        string name
    }
    
    %% TRANSACTIONS 
    APPOINTMENT {
        int id PK
        int business_id FK
        int client_id FK
        int worker_id FK
        int service_id FK
        datetime start_time 
        datetime end_time
    }

    %% RELATIONSHIPS
    BUSINESS ||--o{ ADMIN_USER : "has accounts (login)"
    BUSINESS ||--o{ BUSINESS_HOURS : "operates during"
    BUSINESS ||--o{ WORKER : "employs"
    BUSINESS ||--o{ SERVICE : "offers"
    BUSINESS ||--o{ CLIENT : "registers"
    BUSINESS ||--o{ APPOINTMENT : "manages"
    
    %% MANY-TO-MANY RESOLUTION
    WORKER ||--o{ WORKER_SERVICE : "can perform"
    SERVICE ||--o{ WORKER_SERVICE : "is performed by"

    %% APPOINTMENT RELATIONSHIPS
    CLIENT ||--o{ APPOINTMENT : "books"
    WORKER ||--o{ APPOINTMENT : "attends"
    SERVICE ||--o{ APPOINTMENT : "includes"

    WORKER ||--o{ WORKER_HOURS : "works"
```

---

## ⬇️ Installation


### Prerequisites
*   Python 3.12+
*   PostgreSQL
*   Redis
*   Docker & Docker Compose (optional, for infrastructure)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/assistantfy.git
   cd assistantfy
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and configure the following required environment variables:
   ```env
   # API & Integration
   VERIFICATION_TOKEN=your_verification_token
   WHATSAPP_TOKEN=your_whatsapp_token
   PHONE_NUMBER_ID=your_phone_number_id
   DEEPSEEK_API_KEY=your_deepseek_api_key

   # Database & Infrastructure
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=dbname
   REDIS_URL=redis://localhost:6379/0
   ```

### Execution
If you have Docker installed, you can start the infrastructure (Postgres/Redis) with:
```bash
docker-compose up -d
```

Then, start the FastAPI application:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.


---

## 💬 Community & Contributing

We welcome contributions! If you have suggestions, found a bug, or would like to propose a new feature, please open an issue or start a Discussion in the GitHub repository.
