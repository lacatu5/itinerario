import os

import firebase_admin
from firebase_admin import credentials
from loguru import logger

from core.config import config


def initialize_firebase():
    if firebase_admin._apps:
        return

    try:
        project_id = config.FIREBASE_PROJECT_ID
        if config.is_local:
            auth_emulator_host = config.FIREBASE_AUTH_EMULATOR_HOST
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = auth_emulator_host

            firebase_admin.initialize_app(options={"projectId": project_id})
            logger.info(
                f"Firebase initialized for local environment with auth emulator at {auth_emulator_host}"
            )
        else:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {"projectId": project_id})
            env_name = "dev" if config.is_dev else "production"
            logger.info(f"Firebase initialized for {env_name} environment")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise
