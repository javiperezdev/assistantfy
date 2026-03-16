from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    verification_token: str
    whatsapp_token: str
    phone_number_id: str
    deepseek_api_key: str
    # I have declared extra=ignore just for testing reasons, I should change this before the MVP
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()