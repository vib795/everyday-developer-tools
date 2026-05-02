from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import settings
from .logging import configure_logging
from .rate_limit import limiter
from .routers import (
    document,
    encoding,
    fake_data,
    json_tools,
    regex_tools,
    string_tools,
    time_tools,
)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, docs_url="/docs", redoc_url=None)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(json_tools.router)
    app.include_router(regex_tools.router)
    app.include_router(string_tools.router)
    app.include_router(encoding.router)
    app.include_router(time_tools.router)
    app.include_router(document.router)
    app.include_router(fake_data.router)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    _mount_spa(app)
    return app


def _mount_spa(app: FastAPI) -> None:
    dist = Path(settings.spa_dist)
    if not dist.exists():
        @app.get("/")
        def missing_spa() -> JSONResponse:
            return JSONResponse(
                {
                    "message": "SPA build not found. Run `npm run build` in frontend/ "
                    "or set SPA_DIST.",
                    "expected_path": str(dist),
                },
                status_code=503,
            )
        return

    assets_dir = dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    index_path = dist / "index.html"

    @app.get("/{full_path:path}", response_model=None, include_in_schema=False)
    def spa_catchall(full_path: str, request: Request) -> FileResponse | JSONResponse:
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        candidate = dist / full_path
        if full_path and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(index_path))


app = create_app()
