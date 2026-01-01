from cent import AsyncClient, CentError, PublishRequest
from loguru import logger


class CentrifugoClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = 5
        self.client = AsyncClient(api_url, api_key, timeout=self.timeout)

    async def publish(self, channel: str, data: dict) -> bool:
        try:
            request = PublishRequest(channel=channel, data=data)
            await self.client.publish(request)
            logger.debug(f"Published to channel {channel}")
            return True
        except CentError as e:
            logger.error(f"Centrifugo publish failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error publishing to Centrifugo: {e}")
            return False

    async def broadcast(self, channel: str, data: dict) -> bool:
        return await self.publish(channel, data)

    async def close(self):
        await self.client.close()
