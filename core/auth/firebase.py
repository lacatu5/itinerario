from fastapi import Header, HTTPException
from loguru import logger
import json
import base64

from core.config import config

if not config.is_local:
    import firebase_admin
    from firebase_admin import auth as firebase_auth

    firebase_admin.initialize_app()


def decode_emulator_token(token: str) -> str:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token")
        payload = parts[1]
        payload += "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        return data.get("user_id") or data.get("uid", "")
    except Exception as e:
        logger.error(f"Failed to decode emulator token: {e}")
        raise


async def get_current_user_id(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")

    token = authorization[7:] if authorization.startswith("Bearer ") else authorization

    if config.is_local:
        return decode_emulator_token(token)

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
