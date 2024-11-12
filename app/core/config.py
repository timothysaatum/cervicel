# import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "cervicel"
    debug: bool = True

settings = Settings()
