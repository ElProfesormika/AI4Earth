from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://smartwaste:changeme@db:5432/smartwaste"
    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_topic_prefix: str = "smartwaste"
    cors_origins: str = "http://localhost:5173"
    models_dir: str = "/app/models"
    forecast_model: str = "/app/models/xgb_forecaster.json"


settings = Settings()
