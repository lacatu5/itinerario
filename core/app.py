import time
from contextlib import AsyncExitStack, asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from loguru import logger

from .config import service_settings
from .exceptions import register_exception_handlers


def register_http_logging_middleware(app):
    @app.middleware("http")
    async def http_logging_middleware(request: Request, call_next):
        start_time = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", "N/A")

        response = await call_next(request)

        process_time_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"method={request.method} path={request.url.path} "
            f"status={response.status_code} time={process_time_ms:.2f}ms "
            f"request_id={request_id}"
        )

        return response


def create_app(
    title: str,
    description: str = "",
    version: str = "1.0.0",
    routers: list | None = None,
    lifespan=None,
    use_firestore: bool = False,
    use_messaging: bool = False,
    allowed_origins: list[str] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def combined_lifespan(app):
        async with AsyncExitStack() as stack:
            if use_firestore:
                from .firestore.lifespan import firestore_lifespan

                await stack.enter_async_context(firestore_lifespan(app))
            if use_messaging:
                from .messaging.lifespan import messaging_lifespan

                await stack.enter_async_context(messaging_lifespan(app))
            if lifespan:
                await stack.enter_async_context(lifespan(app))
            yield

    app = FastAPI(title=title, description=description, version=version, lifespan=combined_lifespan)

    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://www.itinerario.app",
            "https://itinerario.app",
            "https://staging.itinerario.app",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    register_http_logging_middleware(app)
    register_exception_handlers(app)
    add_pagination(app)

    if routers:
        for router in routers:
            app.include_router(router)

    @app.get("/")
    def root():
        return {"message": f"{title} is running"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    return app


def run(app: FastAPI, host: str = None, port: int = None):
    host = host or service_settings.HOST
    port = port or service_settings.PORT
    uvicorn.run(app, host=host, port=port)
