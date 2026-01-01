from app.router import api_router
from core.app import create_app, run

app = create_app(
    title="User Service",
    description="User management microservice for Itinerario",
    version="1.0.0",
    routers=[api_router],
)

if __name__ == "__main__":
    run(app)
