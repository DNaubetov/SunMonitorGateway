from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JSC_TPP: Optional[str] = None
    TASHKENT_TTC: Optional[str] = None
    SIRDARYA_TPP: Optional[str] = None
    MUBAREK_TPP: Optional[str] = None

    class Config:
        env_file = ".env"
