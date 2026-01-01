import os
from contextlib import asynccontextmanager

from core.auth.client import initialize_firebase
from core.config import config


@asynccontextmanager
async def firebase_lifespan(app):
    if config.is_local:
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        os.environ["FIRESTORE_EMULATOR_HOST"] = config.FIRESTORE_EMULATOR_HOST
    initialize_firebase()
    yield
