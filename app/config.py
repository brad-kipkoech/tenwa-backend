from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Tenwa Logistics API"
    APP_ENV: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    FRONTEND_URL: str = "http://localhost:5173"

    RESEND_API_KEY: str | None = None
    EMAIL_FROM: str = "Tenwa Logistics <onboarding@resend.dev>"
    EMAIL_TO: str | None = None

    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    ADMIN_ALLOWED_EMAILS: str = ""

    class Config:
        env_file = ".env"


settings = Settings()