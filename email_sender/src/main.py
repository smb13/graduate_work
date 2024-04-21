import uvicorn
from src.core.config import settings
from src.web.app import init_app

app = init_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True,
    )
