from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import get_catalog, get_vector_store
from app.routers import chat, documents, laws, library, system


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    settings.ensure_storage()
    get_catalog()
    get_vector_store().ensure_collection()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_title,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(documents.router)
app.include_router(library.router)
app.include_router(laws.router)
app.include_router(chat.router)
