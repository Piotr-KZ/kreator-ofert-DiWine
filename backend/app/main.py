"""
Lab Creator — internal tool for testing page generation quality.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401 — ensure all models are loaded for SQLAlchemy
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import init_db, async_session_local

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables + seed blocks."""
    logger.info("Starting Lab Creator...")

    # Create tables
    await init_db()
    logger.info("Database tables created")

    # Seed categories + blocks
    async with async_session_local() as db:
        from app.services.creator.block_service import seed_block_categories
        from app.services.creator.seed_blocks import seed_block_templates

        cats = await seed_block_categories(db)
        blocks = await seed_block_templates(db)
        logger.info(f"Seeded {cats} categories, {blocks} blocks")

    yield
    logger.info("Shutting down Lab Creator")


app = FastAPI(
    title="Lab Creator",
    version="1.0.0",
    description="Wewnetrzne narzedzie testowe do generowania stron www",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api/v1")

# Static files for uploads
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health():
    return {"status": "ok", "app": "Lab Creator"}
