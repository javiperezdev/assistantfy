from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tokens and private data
    verification_token: str
    whatsapp_token: str
    phone_number_id: str
    deepseek_api_key: str

    # database
    database_url: str
    postgres_user: str 
    postgres_password: str 
    postgres_db: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
