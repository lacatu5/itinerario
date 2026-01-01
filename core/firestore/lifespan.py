import os
from contextlib import asynccontextmanager

import fireo
from firebase_admin import firestore

from core.auth.client import initialize_firebase
from core.config import config


@asynccontextmanager
async def firestore_lifespan(app):
    if config.is_local:
        os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        os.environ["FIRESTORE_EMULATOR_HOST"] = config.FIRESTORE_EMULATOR_HOST
    initialize_firebase()
    client = firestore.client()
    fireo.connection(client=client)
    yield
