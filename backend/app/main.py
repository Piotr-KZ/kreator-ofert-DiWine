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
    """Startup: create tables + seed blocks + seed offer data."""
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

    # Seed offer data (products, packagings, colors, occasions, discounts)
    async with async_session_local() as db:
        from app.services.offer.seed_offer_data import seed_offer_data

        offer_counts = await seed_offer_data(db)
        logger.info(f"Seeded offer data: {offer_counts}")

    # Seed offer text templates
    async with async_session_local() as db:
        from app.services.offer.seed_offer_texts import seed_offer_texts
        text_count = await seed_offer_texts(db)
        logger.info(f"Seeded {text_count} offer text templates")

    # Seed offer block templates
    async with async_session_local() as db:
        from app.services.offer.seed_offer_blocks import seed_offer_blocks
        offer_block_counts = await seed_offer_blocks(db)
        logger.info(f"Seeded offer blocks: {offer_block_counts}")

    # Seed lifestyle photos from Unsplash (one-time download)
    async with async_session_local() as db:
        from app.services.offer.photo_library import seed_lifestyle_photos
        photo_stats = await seed_lifestyle_photos(db)
        logger.info(f"Photo library: {photo_stats}")

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
    allow_origins=["http://localhost:3002", "http://127.0.0.1:3002", "http://localhost:3005", "http://127.0.0.1:3005"],
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
