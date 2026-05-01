from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# service/frontend/dist（相对于本文件：../../frontend/dist）
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="HuatingRiichiClub API",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS（开发时允许 Vite Dev Server，生产时可按需缩减）──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API 路由（必须在静态挂载之前注册）─────────────────────────────────
# from app.api.v1 import router as api_v1_router
# app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


# ── 生产态：挂载 Vue3 OP 构建产物 ──────────────────────────────────────
if FRONTEND_DIST.exists():
    # /assets/* → dist/assets/（JS/CSS/图片等哈希文件）
    _assets_dir = FRONTEND_DIST / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="frontend-assets")

    # /favicon.svg 等根级静态文件
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIST),
        name="frontend-root-static",
    )

    # SPA 回退：所有非 /api、非 /assets 路径均返回 index.html，
    # 由 Vue Router 接管客户端路由。
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # 避免误拦截已注册的 API 路径
        if full_path.startswith(("api/", "docs", "redoc", "openapi")):
            raise HTTPException(status_code=404, detail="Not found")
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=503, detail="Frontend not built")
