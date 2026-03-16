# ASSISTANTFY
An AI-powered assistant designed to automate business workflows. It eliminates the need for manual call handling by leveraging NLP to answer FAQs and manage end-to-end appointment scheduling, significantly increasing operational efficiency.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Work_In_Progress-FF8C00?style=for-the-badge)

## 🎯 Objectives
The goal of this project is to build a highly scalable, asynchronous backend that can:
1. Receive messages in real-time via WhatsApp Webhooks. [x]
2. Process natural language using an LLM (currently DeepSeek) to understand the user's intent. [x]
3. Manage a calendar/database to schedule, modify, or cancel appointments automatically. [ ]

📖 **Track my daily progress and technical decisions here:** [PROGRESSLOG.md](./PROGRESSLOG.md)

**1. Clone the repository** 
 ```bash
   git clone [https://github.com/javiperezdev/assistantfy.git](https://github.com/javiperezdev/assistantfy.git)  
   cd assistantfy 
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv venv  source venv/bin/activate  # On Windows use `venv\Scripts\activate`  
pip install -r requirements.txt   
```

**3. Environment Variables**Create a .env file in the root directory:

```shell 
WHATSAPP_TOKEN=your_meta_system_user_token  
VERIFY_TOKEN=your_custom_verify_token  
PHONE_NUMBER_ID=your_meta_phone_number_id   
```

**4. Run the development server**

```bash 
uvicorn app.main:app --reload  
```

(Note: To test webhooks locally, you will need a tool like [Ngrok](https://ngrok.com/) to expose your localhost to the internet).

Developed with curiosity by **javiperezdev**