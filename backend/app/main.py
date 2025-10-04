from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .config import get_settings, logger
from .database import get_db_manager
from .routes import get_api_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_title)

    app.include_router(get_api_router())

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=settings.cors_origins or ['*'],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        try:
            get_db_manager()
        except Exception as exc:
            logger.exception("Application startup failed during database initialization")
            raise exc

    @app.on_event("shutdown")
    async def shutdown_event():
        db_manager = get_db_manager()
        await db_manager.close()

    return app
