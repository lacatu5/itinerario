import time

import jwt


def generate_centrifugo_token(user_id: str, api_key: str, exp_hours: int = 24) -> str:
    exp = int(time.time()) + (exp_hours * 3600)

    payload = {"sub": user_id, "exp": exp}

    token = jwt.encode(payload, api_key, algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token
