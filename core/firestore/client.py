import os

from google.cloud import firestore
from loguru import logger

from core.config import config


def get_firestore_client() -> firestore.Client:
    if config.is_local:
        os.environ["FIRESTORE_EMULATOR_HOST"] = config.FIRESTORE_EMULATOR_HOST
        client = firestore.Client(project=config.GOOGLE_CLOUD_PROJECT, credentials=None)
        logger.debug("Using Firestore emulator")
        return client

    client = firestore.Client(project=config.GOOGLE_CLOUD_PROJECT)
    logger.debug(f"Using Firestore for project {config.GOOGLE_CLOUD_PROJECT}")
    return client
