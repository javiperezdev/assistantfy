from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tokens and private data
    verification_token: str
    whatsapp_token: str
    phone_number_id: str
    deepseek_api_key: str

    # database
    postgres_user: str 
    postgres_password: str 
    postgres_db: str

    # prompts

    # I have declared extra=ignore just for testing reasons, I should change this before the MVP
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
