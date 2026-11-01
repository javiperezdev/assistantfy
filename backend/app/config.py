from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tokens and private data
    verification_token: str
    whatsapp_token: str
    phone_number_id: str
    ai_api_key: str

    # database
    database_url: str
    postgres_user: str 
    postgres_password: str 
    postgres_db: str
    redis_url: str

    # testing
    test_database_url: str

    # front-end 
    front_end_url: str

    # session configuration
    session_cookie_name: str = "assistantfy_session"
    session_cookie_secure: bool = False
    session_ttl_seconds: int = 2592000        # 30 days, absolute Redis TTL
    session_max_age_seconds: int = 2592000    # 30 days, cookie max-age
    session_path: str = "/"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
