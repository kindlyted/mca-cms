"""
Project configuration for MCA-CMS JSON Generator.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from cms directory
load_dotenv(Path(__file__).parent.parent / ".env")


class Settings:
    # === Project paths ===
    CMS_DIR = Path(__file__).parent.parent
    PROJECT_ROOT = CMS_DIR.parent
    DATA_DIR = Path(os.getenv("CMS_DATA_DIR", str(PROJECT_ROOT / "data")))
    PROMPTS_DIR = CMS_DIR / "prompts"

    # === Output directories ===
    # mca-cms: blogs / services / partners / products are top-level peers.
    BLOG_OUTPUT_DIR = DATA_DIR / "blogs"
    SERVICE_OUTPUT_DIR = DATA_DIR / "services"
    # "provider" is the legacy internal name; it maps to the `partners` folder & `_type: partner`
    PROVIDER_OUTPUT_DIR = DATA_DIR / "partners"
    # products are organised by category: data/products/{category}/{lang}
    PRODUCT_OUTPUT_BASE = DATA_DIR / "products"

    # === Asset directories ===
    # Blog images stay in data/assets for sync.py to upload
    BLOG_ASSETS_DIR = DATA_DIR / "assets" / "blogs"
    SERVICE_ASSETS_DIR = DATA_DIR / "assets" / "services"
    PROVIDER_ASSETS_DIR = DATA_DIR / "assets" / "partners"
    # products assets: data/assets/products/{category}/{id}
    PRODUCT_ASSETS_BASE = DATA_DIR / "assets" / "products"

    # === Site config ===
    BASE_URL = os.getenv("BASE_URL", "https://www.yourdomain.com").rstrip("/")
    LANGUAGES = [x.strip() for x in os.getenv("LANGUAGES", "en,fr,de").split(",") if x.strip()]
    DEFAULT_LANGUAGE = "en"

    # === LLM defaults ===
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "deepseek")
    DEFAULT_TEMPERATURE = 0.7

    # === Unsplash ===
    UNSPLASH_ACCESS_KEY = os.getenv("UNP_AKEY", "")

    # === AI Image Generator ===
    IMAGE_GENERATOR = os.getenv("IMAGE_GENERATOR", "unsplash")  # "unsplash" | "ai"
    AI_IMAGE_MODEL = os.getenv("AI_IMAGE_MODEL", "qwen-image-2.0-pro")
    AI_IMAGE_PROVIDER = os.getenv("AI_IMAGE_PROVIDER", "qwen")  # "qwen" | "seedream"
    AI_IMAGE_STYLE = os.getenv("AI_IMAGE_STYLE", "photorealistic")  # photorealistic, cartoon, ink-wash, minimalist, nature-healing

    # === Image settings ===
    MAX_IMAGE_SIZE_BYTES = 1024 * 1024  # 1MB
    IMAGE_QUALITY_START = 85
    IMAGE_QUALITY_MIN = 40
    IMAGE_MAX_DIMENSION = 1920

    # === Remote sync settings ===
    # Remote sync pushes to the same site, so it reuses the single BASE_URL
    # from cms/.env (no separate REMOTE_API_URL).
    REMOTE_API_URL = BASE_URL
    REMOTE_API_KEY = os.getenv("REMOTE_API_KEY", "")


settings = Settings()
