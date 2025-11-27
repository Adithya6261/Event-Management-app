from fastapi import FastAPI
import uvicorn

from app.api import auth_routes
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    openapi_url="/docs/openapi.json",
)

app.include_router(auth_routes.auth_router, prefix="/api/auth")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.uvicorn_host, port=settings.uvicorn_port, reload=False)
