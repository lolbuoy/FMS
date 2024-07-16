import os
from dotenv import dotenv_values

config = dotenv_values(".env")

class Config:
    # SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    # REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    # REDIS_POLL_INTERVAL = os.environ.get("REDIS_POLL_INTERVAL", 5)
    SECRET_KEY = config.get("SECRET_KEY", "default_secret_key")
    REDIS_URL = config.get("REDIS_URL", "redis://localhost:6379/0")
    REDIS_POLL_INTERVAL = int(config.get("REDIS_POLL_INTERVAL", 5))