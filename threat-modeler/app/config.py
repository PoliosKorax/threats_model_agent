import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения."""
    
    app_name: str = Field(default="Threat Modeler FSTEC", description="Имя приложения")
    app_port: int = Field(default=8000, description="Порт для запуска")
    env: str = Field(default="development", description="Окружение")
    
    # Database
    db_path: str = Field(default="./data/threats.db", description="Путь к SQLite БД")
    
    # Paths
    data_dir: str = Field(default="./data", description="Директория данных")
    reports_dir: str = Field(default="./reports", description="Директория отчётов")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
