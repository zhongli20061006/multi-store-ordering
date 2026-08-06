from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core import uploads
from app.core.config import settings
from app.core.response import ok, register_exception_handlers
from app.api.v1 import admin_banners, admin_dashboard, admin_menus, admin_orders, admin_stores, auth, orders, stores


app = FastAPI(title=settings.app_name, version="0.1.0")

uploads.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads.UPLOAD_DIR)), name="uploads")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/api/v1/health")
def health():
    return ok({"status": "ok"})


api = APIRouter(prefix="/api/v1")
api.include_router(auth.router)
api.include_router(stores.router)
api.include_router(orders.router)
api.include_router(admin_stores.router)
api.include_router(admin_dashboard.router)
api.include_router(admin_banners.router)
api.include_router(admin_menus.router)
api.include_router(admin_orders.router)
app.include_router(api)
