from app.router import api_router
from core.app import create_app, run

app = create_app(
    title="Chat Service",
    description="Real-time chat microservice for Itinerario",
    version="1.0.0",
    routers=[api_router],
    use_firestore=True,
    use_messaging=True,
)

if __name__ == "__main__":
    run(app)
