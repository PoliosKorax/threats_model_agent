"""Главный файл приложения FastAPI."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import secrets

from app.config import settings
from app.db.engine import init_db
from app.api.endpoints.wizard import router as wizard_router


# Директории
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan контекст для инициализации приложения."""
    # Startup
    print(f"🚀 Starting {settings.app_name}...")
    
    # Инициализация БД
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Создание приложения
app = FastAPI(
    title=settings.app_name,
    description="Генератор моделей угроз ФСТЭК",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS (для локальной разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Секретный ключ для сессий
app.secret_key = secrets.token_hex(32)

# Статические файлы
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Шаблоны Jinja2
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.templates = templates  # Добавляем для доступа из endpoints


# Middleware для добавления db session в request
@app.middleware("http")
async def add_db_session(request: Request, call_next):
    """Добавить сессию БД в request.state."""
    from app.db.engine import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        request.state.db = session
        response = await call_next(request)
        await session.commit()
    return response


# Роуты
app.include_router(wizard_router, prefix="/api/wizard")


@app.get("/")
async def root(request: Request):
    """Главная страница - перенаправление на wizard."""
    return templates.TemplateResponse(
        "wizard/step1_system.html",
        {"request": request, "step": 1}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.env == "development"
    )
