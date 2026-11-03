from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    github_client_id: str
    github_client_secret: str
    jwt_secret_key: str
    openai_api_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
