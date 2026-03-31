from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    APP_NAME: str = "License Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/license.db"

    # 管理员 Token
    ADMIN_TOKEN: str = "change-me-in-production"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
