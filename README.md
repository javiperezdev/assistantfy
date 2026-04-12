# ASSISTANTFY

An enterprise-grade B2B SaaS backend that transforms LLMs into autonomous agents for real-time business operations and booking management.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![DeepSeek API](https://img.shields.io/badge/AI-DeepSeek_API-4D4D4E?style=for-the-badge)

## 📌 The Product Vision
Assistantfy acts as an affordable, 24/7 virtual assistant for local businesses (clinics, salons, etc.). It eliminates manual call handling by leveraging Natural Language Processing (NLP) to answer FAQs and manage end-to-end appointment scheduling, allowing owners to focus on their core services.

---

### The Multi-Tenant Database Schema
To handle multiple businesses securely within the same database, I designed a multi-tenant schema where a `Business` acts as the root entity, ensuring strict data isolation.

``` mermaid
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
## ROADMAP

### Phase 1: Infrastructure & Performance 
[x] Stateful Session Management via Redis: Implement a high-performance caching layer to maintain conversation persistence across stateless WhatsApp webhooks.

[ ] Develop a Sliding Window Context Buffer to optimize token consumption and reduce LLM inference costs by managing the message history sent to the model.

[ ] Security & Anti-Abuse Layer: Integrate Rate Limiting per client ID using Redis to prevent DoS attacks and safeguard API budget from malicious exploitation.

### Phase 2: Business Control 
[ ] Dashboard: Build a centralized interface for business owners to manage service catalogs, staff availability, and real-time appointment calendars.

[ ] Business Intelligence & Conversion Analytics: Develop an analytics engine to track key metrics: Message-to-Booking conversion rates, peak inquiry times, and popular services.

















