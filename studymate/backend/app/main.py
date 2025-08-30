from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ingestion, search, chat, auth, crud


def create_app() -> FastAPI:
    app = FastAPI(title="StudyMate API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(ingestion.router)
    app.include_router(search.router)
    app.include_router(chat.router)
    app.include_router(auth.router)
    app.include_router(crud.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "studymate", "version": "0.1.0"}

    return app


app = create_app()


