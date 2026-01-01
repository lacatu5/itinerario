from contextlib import asynccontextmanager

from core.config import centrifugo_settings
from core.messaging.client import CentrifugoClient


@asynccontextmanager
async def messaging_lifespan(app):
    app.state.centrifugo_client = CentrifugoClient(
        centrifugo_settings.CENTRIFUGO_API_URL,
        centrifugo_settings.CENTRIFUGO_API_KEY,
    )
    yield
    await app.state.centrifugo_client.close()
