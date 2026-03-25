from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tokens and private data
    verification_token: str
    whatsapp_token: str
    phone_number_id: str
    deepseek_api_key: str

    # prompts
    availability_prompt: str

    # I have declared extra=ignore just for testing reasons, I should change this before the MVP
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

BUSINESS_HOURS = {
    1: ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"],
    2: ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"],
    3: ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"],
    4: ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"],
    5: ["09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"],
    6: ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"],
    7: [] 
}