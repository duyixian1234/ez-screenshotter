import functools
import logging
from typing import Optional

from pydantic import BaseSettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


class Settings(BaseSettings):
    watermark: Optional[str] = None


@functools.cache
def get_settings() -> Settings:
    settings = Settings()
    logging.info("Load Settings: %s", settings)
    return settings
