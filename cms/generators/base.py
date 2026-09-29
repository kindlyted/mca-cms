"""
Base Generator — Common logic for all content types.

Template structures are HARDCODED here (no external JSON template files needed).
This ensures the schema is immutable regardless of what happens to data/templates/.
"""

import re
import io
import json
import copy
import time
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw

from config import settings
from llmcore import invoke_llm, invoke_llm_json


# =============================================================================
# HARDCODED TEMPLATE SCHEMAS (source of truth, never modify data/templates/)
# =============================================================================

DEFAULT_AUTHOR = {
    "id": "yourbrand-team",
    "name": "YourBrand Editorial Team",
    "role": "Editorial Team",
    "url": "https://www.yourdomain.com/about"
}

BLOG_TEMPLATE = {
    "_type": "blog",
    "meta": {
        "id": "", "region": "", "country": "", "language": "", "status": "published",
        "readTime": 0, "featured": False, "priority": 0,
        "createdAt": "", "updatedAt": "", "slug": "",
        "author": {"id": "", "name": "", "role": "", "url": ""},
    },
    "seo": {
        "title": "", "description": "", "keywords": "",
    },
    "cover": {
        "url": "", "alt": "", "caption": "",
    },
    "overview": {"title": "", "subtitle": "", "excerpt": ""},
    "body": {"format": "markdown", "content": ""},
    "tags": {"primary": [], "secondary": []},
    "faq": [],
    "references": [],
    "source": "",
    "sourceUrl": "",
}

SERVICE_TEMPLATE = {
    "_type": "service",
    "meta": {
        "id": "", "region": "", "country": "",
        "language": "", "status": "published",
        "featured": False, "priority": 0,
        "createdAt": "", "updatedAt": "", "slug": "",
        "difficulty": "", "duration": "", "priceRange": "",
        "author": {"id": "", "name": "", "role": "", "url": ""},
    },
    "seo": {
        "title": "", "description": "", "keywords": "",
    },
    "cover": {
        "url": "", "alt": "",
    },
    "overview": {"title": "", "excerpt": "", "subtitle": ""},
    "description": "",
    "pricing": {
        "currency": "USD",
        "tiers": [],
        "exclusions": [],
        "exampleTotal": {}
    },
    "testimonials": [],
    "highlights": [],
    "conditions": {"title": "", "items": []},
    "process": {"title": "", "steps": []},
    "faq": [],
    "references": [],
}

PROVIDER_TEMPLATE = {
    "_type": "provider",
    "meta": {
        "id": "", "type": "hospital",
        "city": "", "region": "", "country": "", "language": "",
        "status": "published",
        "featured": False, "priority": 0,
        "createdAt": "", "updatedAt": "", "slug": "",
    },
    "seo": {
        "title": "", "description": "", "keywords": "",
    },
    "cover": {
        "url": "", "alt": "",
    },
    "overview": {"title": "", "excerpt": "", "subtitle": ""},
    "institution": {
        "name": "", "established": 0, "beds": 0,
        "annualPatients": "", "internationalPatients": "",
        "accreditation": [], "ranking": "",
        "languages": [], "address": {
            "street": "", "city": "", "province": "",
            "postalCode": "",
        },
        "geo": {"latitude": "", "longitude": ""},
        "contact": {
            "phone": "", "email": "", "website": "", "workingHours": "",
        },
        "rating": {"value": 0, "count": 0},
    },
    "doctors": [],
    "services": [],
    "description": "",
    "faq": [],
    "references": [],
}

PRODUCT_TEMPLATE = {
    "_type": "product",
    "meta": {
        "id": "", "language": "", "status": "published",
        "featured": False, "priority": 0,
        "createdAt": "", "updatedAt": "", "slug": "",
        "category": "", "region": "", "country": "",
    },
    "seo": {
        "title": "", "description": "", "keywords": [],
    },
    "cover": {
        "url": "", "alt": "",
    },
    "overview": {"title": "", "excerpt": "", "subtitle": ""},
    "description": "",
    "brand": "",
    "price": 0,
    "compareAtPrice": None,
    "currency": "USD",
    "colors": [],
    "dimensions": "",
    "thickness": "",
    "sizes": [],
    "inStock": True,
    "highlights": [],
    "specs": [],
    "pricing": {
        "currency": "USD",
        "tiers": [],
        "inclusions": [],
        "exclusions": [],
    },
    "faq": [],
    "references": [],
}

TEMPLATES = {
    "blog": BLOG_TEMPLATE,
    "service": SERVICE_TEMPLATE,
    "provider": PROVIDER_TEMPLATE,
    "product": PRODUCT_TEMPLATE,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def calculate_read_time(content: str) -> int:
    """Calculate reading time in minutes (English ~250 wpm)."""
    words = len(content.split())
    return max(1, round(words / 250))


def now_iso() -> str:
    """Current datetime in ISO format with +08:00."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def today_str() -> str:
    """Current date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


# entity type -> URL route prefix (matches mca-cms Nuxt routes)
_ROUTE_MAP = {"blog": "blogs", "service": "services", "provider": "partners", "product": "products"}


def _entity_route(content_type: str) -> str:
    return _ROUTE_MAP.get(content_type, content_type)


def build_hreflang(slug: str, content_type: str, lang: str) -> List[Dict]:
    """Build hreflang entries for all languages."""
    base = settings.BASE_URL
    route = _entity_route(content_type)
    hreflang = []
    for l in settings.LANGUAGES:
        prefix = f"/{l}" if l != "en" else ""
        url = f"{base}{prefix}/{route}/{slug}"
        hreflang.append({"lang": l, "url": url})
    return hreflang


def build_canonical(slug: str, content_type: str, lang: str) -> str:
    """Build canonical URL."""
    base = settings.BASE_URL
    prefix = f"/{lang}" if lang != "en" else ""
    return f"{base}{prefix}/{_entity_route(content_type)}/{slug}"


# =============================================================================
# BODY STRIPPING — remove sections handled separately by the frontend layout
# =============================================================================

# Common CTA closing patterns at end of body text (e.g. "Ready to book? Contact us.")
_CTA_PATTERNS = re.compile(
    r'(?:\n\n)(?:Ready to|Start your|Book your|Contact us|Get in touch|Schedule your|Take the first step)'
    r'.*?(?:today!?|now!?|us!?|journey!?)\.?\s*$',
    re.DOTALL | re.IGNORECASE
)


def strip_body_sections(body: str) -> str:
    """Remove structural sections from body that are rendered separately in the layout.

    Strips:
      - ## FAQ / ### FAQ / ## Frequently Asked Questions sections
      - ## References / ### References sections
      - ## Highlights sections (service)
      - ## Eligibility & Requirements / Conditions sections (service)
      - ## Your * Journey / Process / Step sections (service)
      - CTA closing paragraph at end of body
    """
    if not body:
        return body

    # Combined pattern to strip all structural section headings (both ## and ###)
    # and everything after them. Order matters: generic first, then specific.
    _STRIP_SECTIONS = re.compile(
        r'\n#{2,3}\s*(?:'
        r'FAQ|Frequently Asked Questions|'
        r'References|'
        r'Highlights?|'
        r'Eligibili.*|Requirements|Conditions?|'
        r'Your\s+\w+\s+Journey|Process|Step\b'
        r')\s*\n',
        re.IGNORECASE
    )
    body = _STRIP_SECTIONS.split(body)[0].strip()

    # Strip trailing CTA paragraph
    body = _CTA_PATTERNS.sub('', body).strip()

    return body
    body = _CTA_PATTERNS.sub('', body).strip()

    return body


# =============================================================================
# IMAGE GENERATION (AI) - 文生图
# =============================================================================

def generate_image_with_ai(
    query: str,
    save_path: Path,
    aspect_ratio: str = "landscape",
    content_type: str = "blog",
    style: str = "photorealistic",
) -> Optional[str]:
    """
    使用 AI 文生图生成图片（替代 Unsplash 下载）

    Args:
        query: Search keyword
        save_path: Full output path (e.g. .../01.webp)
        aspect_ratio: 'landscape', 'portrait', or 'squarish'
        content_type: 'blog', 'service', or 'provider'
        style: Image style (photorealistic, cartoon, ink-wash, minimalist, nature-healing)

    Returns:
        Saved file path string, or None on failure
    """
    from .image_generator import (
        generate_blog_image,
        generate_service_image,
        generate_provider_image,
        generate_product_image,
    )

    # 根据内容类型选择生成函数
    if content_type == "blog":
        result = generate_blog_image(query, save_path, aspect_ratio, provider=settings.AI_IMAGE_PROVIDER, model=settings.AI_IMAGE_MODEL, style=style)
    elif content_type == "service":
        result = generate_service_image(query, save_path, provider=settings.AI_IMAGE_PROVIDER, model=settings.AI_IMAGE_MODEL, style=style)
    elif content_type == "provider":
        result = generate_provider_image(query, save_path, provider=settings.AI_IMAGE_PROVIDER, model=settings.AI_IMAGE_MODEL, style=style)
    elif content_type == "product":
        result = generate_product_image(query, save_path, provider=settings.AI_IMAGE_PROVIDER, model=settings.AI_IMAGE_MODEL, style=style)
    else:
        result = None

    return result


# =============================================================================
# IMAGE DOWNLOAD (Unsplash) - 保留作为备选
# =============================================================================

def download_image_from_unsplash(
    query: str,
    save_path: Path,
    aspect_ratio: str = "landscape",
) -> Optional[str]:
    """
    Download an image from Unsplash and save as WebP.

    Args:
        query: Search keyword
        save_path: Full output path (e.g. .../01.webp)
        aspect_ratio: 'landscape', 'portrait', or 'squarish'

    Returns:
        Saved file path string, or None on failure
    """
    access_key = settings.UNSPLASH_ACCESS_KEY
    if not access_key:
        print("  [Image] Skipping: UNSPLASH_ACCESS_KEY not set")
        return None

    if not query:
        query = "medical china"

    orientation_map = {
        "landscape": "landscape",
        "portrait": "portrait",
        "squarish": "squarish",
    }
    orientation = orientation_map.get(aspect_ratio, "landscape")

    try:
        url = (
            f"https://api.unsplash.com/search/photos"
            f"?client_id={access_key}"
            f"&query={requests.utils.quote(query)}"
            f"&orientation={orientation}"
            f"&per_page=5"
        )
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            print(f"  [Image] No results for: {query}")
            return None

        save_path.parent.mkdir(parents=True, exist_ok=True)

        for photo in data["results"]:
            photo_url = photo["urls"]["raw"] + "&w=1920&q=80"
            try:
                img_response = requests.get(photo_url, timeout=60)
                img_response.raise_for_status()

                img = Image.open(io.BytesIO(img_response.content))
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")

                # Check aspect ratio
                w, h = img.size
                ratio = w / h
                if aspect_ratio == "landscape" and ratio < 1.2:
                    continue
                elif aspect_ratio == "portrait" and ratio > 0.8:
                    continue

                # Resize if too large
                if max(img.size) > settings.IMAGE_MAX_DIMENSION:
                    scale = settings.IMAGE_MAX_DIMENSION / max(img.size)
                    new_size = (int(w * scale), int(h * scale))
                    img = img.resize(new_size, Image.LANCZOS)

                # Save as WebP with quality optimization
                quality = settings.IMAGE_QUALITY_START
                while quality >= settings.IMAGE_QUALITY_MIN:
                    buffer = io.BytesIO()
                    img.save(buffer, format="WEBP", quality=quality, method=6)
                    if buffer.getbuffer().nbytes <= settings.MAX_IMAGE_SIZE_BYTES:
                        with open(save_path, "wb") as f:
                            f.write(buffer.getvalue())
                        size_kb = buffer.getbuffer().nbytes / 1024
                        print(f"  [Image] Saved: {save_path.name} ({size_kb:.1f}KB, q={quality})")
                        return str(save_path)
                    quality -= 10

                # Fallback: save with minimum quality
                buffer = io.BytesIO()
                img.save(buffer, format="WEBP", quality=30, method=6)
                with open(save_path, "wb") as f:
                    f.write(buffer.getvalue())
                print(f"  [Image] Saved (low quality): {save_path.name}")
                return str(save_path)

            except Exception as e:
                print(f"  [Image] Failed to process photo: {e}")
                continue

        print(f"  [Image] No suitable image found for: {query}")
        return None

    except Exception as e:
        print(f"  [Image] Unsplash API error: {e}")
        return None


def download_blog_images(
    content_id: str,
    image_queries: List[Dict[str, str]],
    style: str = "photorealistic",
) -> int:
    """
    Download/generate blog images and return count of successful attempts.
    Uses AI generator if IMAGE_GENERATOR=ai, otherwise Unsplash.

    Args:
        content_id: Blog post ID (e.g. 'dental-implants-shanghai')
        image_queries: List of {"index": 1, "query": "dental clinic modern"}
        style: Image style (photorealistic, cartoon, ink-wash, minimalist, nature-healing)

    Returns:
        Number of successfully created images
    """
    save_dir = settings.BLOG_ASSETS_DIR / content_id
    success = 0

    for item in image_queries:
        idx = item["index"]
        query = item["query"]
        filename = f"{idx:02d}.webp"
        save_path = save_dir / filename

        if save_path.exists():
            print(f"  [Image] Already exists: {filename}")
            success += 1
            continue

        # 使用 AI 生成或 Unsplash 下载
        if settings.IMAGE_GENERATOR == "ai":
            result = generate_image_with_ai(
                query, save_path, aspect_ratio="landscape", content_type="blog", style=style
            )
        else:
            # 第一层：尝试原始查询
            result = download_image_from_unsplash(query, save_path, aspect_ratio="landscape")
            if not result:
                # 第二层：简化关键词（取前3个词）
                simplified = " ".join(query.split()[:3])
                if simplified != query:
                    print(f"  [Image] Retry 1: Simplified query: {simplified}")
                    result = download_image_from_unsplash(simplified, save_path, aspect_ratio="landscape")
                if not result:
                    # 第三层：通用医疗关键词
                    generic_keywords = [
                        "medical clinic modern",
                        "hospital building exterior",
                        "doctor patient consultation",
                        "medical technology",
                        "healthcare facility"
                    ]
                    for keyword in generic_keywords:
                        print(f"  [Image] Retry 2: Generic keyword: {keyword}")
                        result = download_image_from_unsplash(keyword, save_path, aspect_ratio="landscape")
                        if result:
                            break

        if result:
            success += 1

        print(f"\n[Wait] Cooling down 30s to avoid rate limit...")
        time.sleep(30)

    print(f"  [Image] Created {success}/{len(image_queries)} images")
    return success


def create_placeholder_image(
    save_path: Path,
    text: str = "No Image",
    width: int = 1920,
    height: int = 1080,
) -> Optional[str]:
    """
    Create a colored placeholder image when download fails.

    Args:
        save_path: Output file path
        text: Text to display on image
        width: Image width
        height: Image height

    Returns:
        Saved file path string, or None on failure
    """
    try:
        from PIL import ImageDraw, ImageFont
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a gradient background
        img = Image.new("RGB", (width, height), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)

        # Draw a subtle gradient
        for y in range(height):
            progress = y / height
            r = int(240 + progress * 15)
            g = int(240 + progress * 10)
            b = int(245 + progress * 20)
            for x in range(width):
                img.putpixel((x, y), (r, g, b))

        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        draw.text((x, y), text, fill=(150, 150, 160), font=font)

        # Save as WebP
        img.save(save_path, format="WEBP", quality=80)
        print(f"  [Image] Created placeholder: {save_path.name}")
        return str(save_path)

    except Exception as e:
        print(f"  [Image] Failed to create placeholder: {e}")
        return None


def download_service_cover(
    service_id: str,
    query: str,
    style: str = "photorealistic",
) -> Optional[str]:
    """Download/generate a cover image for a service with fallback strategies."""
    save_path = settings.SERVICE_ASSETS_DIR / service_id / "cover.webp"

    if save_path.exists():
        print(f"  [Image] Already exists: {service_id}/cover.webp")
        return str(save_path)

    # 使用 AI 生成或 Unsplash 下载
    if settings.IMAGE_GENERATOR == "ai":
        result = generate_image_with_ai(
            query, save_path, aspect_ratio="landscape", content_type="service", style=style
        )
        if result:
            return result
        # AI 失败时创建占位图
        print(f"  [Image] AI generation failed, creating placeholder")
        return create_placeholder_image(save_path, text=f"Service: {service_id}")

    # Unsplash 流程
    # 第一层：尝试原始查询
    result = download_image_from_unsplash(query, save_path, aspect_ratio="landscape")
    if result:
        return result

    # 第二层：简化关键词
    simplified = " ".join(query.split()[:3])
    if simplified != query:
        print(f"  [Image] Retry 1: Simplified query: {simplified}")
        result = download_image_from_unsplash(simplified, save_path, aspect_ratio="landscape")
        if result:
            return result

    # 第三层：通用医疗关键词
    generic_keywords = [
        "medical service clinic",
        "healthcare treatment facility",
        "doctor consultation room",
        "medical equipment modern"
    ]
    for keyword in generic_keywords:
        print(f"  [Image] Retry 2: Generic keyword: {keyword}")
        result = download_image_from_unsplash(keyword, save_path, aspect_ratio="landscape")
        if result:
            return result

    # 第四层：创建占位图片
    print(f"  [Image] All download attempts failed, creating placeholder")
    return create_placeholder_image(save_path, text=f"Service: {service_id}")


def download_provider_cover(
    provider_id: str,
    query: str,
    style: str = "photorealistic",
) -> Optional[str]:
    """Download/generate a cover image for a provider with fallback strategies."""
    save_path = settings.PROVIDER_ASSETS_DIR / provider_id / "cover.webp"

    if save_path.exists():
        print(f"  [Image] Already exists: {provider_id}/cover.webp")
        return str(save_path)

    # 使用 AI 生成或 Unsplash 下载
    if settings.IMAGE_GENERATOR == "ai":
        result = generate_image_with_ai(
            query, save_path, aspect_ratio="landscape", content_type="provider", style=style
        )
        if result:
            return result
        # AI 失败时创建占位图
        print(f"  [Image] AI generation failed, creating placeholder")
        return create_placeholder_image(save_path, text=f"Provider: {provider_id}")

    # Unsplash 流程
    # 第一层：尝试原始查询
    result = download_image_from_unsplash(query, save_path, aspect_ratio="landscape")
    if result:
        return result

    # 第二层：简化关键词
    simplified = " ".join(query.split()[:3])
    if simplified != query:
        print(f"  [Image] Retry 1: Simplified query: {simplified}")
        result = download_image_from_unsplash(simplified, save_path, aspect_ratio="landscape")
        if result:
            return result

    # 第三层：通用医院关键词
    generic_keywords = [
        "hospital building exterior modern",
        "medical center architecture",
        "clinic interior modern",
        "healthcare facility exterior"
    ]
    for keyword in generic_keywords:
        print(f"  [Image] Retry 2: Generic keyword: {keyword}")
        result = download_image_from_unsplash(keyword, save_path, aspect_ratio="landscape")
        if result:
            return result

    # 第四层：创建占位图片
    print(f"  [Image] All download attempts failed, creating placeholder")
    return create_placeholder_image(save_path, text=f"Provider: {provider_id}")


# =============================================================================
# BASE GENERATOR CLASS
# =============================================================================

class BaseGenerator(ABC):
    """Abstract base class for all content generators."""

    CONTENT_TYPE: str = ""  # "blog", "service", "provider"

    def __init__(self, provider: str = "zhipu", sync: bool = False):
        self.provider = provider
        self.sync = sync
        self.prompts_dir = settings.PROMPTS_DIR

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt file."""
        path = self.prompts_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_markdown_file(self, md_path: str) -> str:
        """Load content from a Markdown file."""
        path = Path(md_path)
        if not path.exists():
            raise FileNotFoundError(f"Markdown file not found: {path}")
        return path.read_text(encoding="utf-8")

    def get_template(self) -> dict:
        """Get a deep copy of the hardcoded template."""
        return copy.deepcopy(TEMPLATES[self.CONTENT_TYPE])

    @abstractmethod
    def generate(self, **kwargs) -> dict:
        """Generate content. Must be implemented by subclasses."""
        pass

    def auto_fill_meta(
        self,
        data: dict,
        content_id: str,
        lang: str,
        slug: str = None,
    ) -> dict:
        """
        Auto-fill fields that don't need LLM generation.

        Fills: _type, meta.id, meta.language, meta.status, meta.createdAt/updatedAt,
               meta.slug, meta.author, seo.canonical, seo.hreflang,
               seo.schema.mainEntityOfPage, content.publishedAt/updatedAt,
               visuals paths, etc.
        """
        now = now_iso()
        today = today_str()

        if not slug:
            slug = slugify(content_id)

        canonical = build_canonical(slug, self.CONTENT_TYPE, lang)
        hreflang = build_hreflang(slug, self.CONTENT_TYPE, lang)

        # Fill meta
        # mca-cms: the provider entity is emitted as `_type: partner`
        _TYPE_OUTPUT = {"provider": "partner"}
        data["_type"] = _TYPE_OUTPUT.get(self.CONTENT_TYPE, self.CONTENT_TYPE)
        data.setdefault("meta", {})
        data["meta"]["id"] = content_id
        data["meta"]["language"] = lang
        data["meta"]["status"] = "published"
        data["meta"]["createdAt"] = now
        data["meta"]["updatedAt"] = now
        data["meta"]["slug"] = slug
        data["meta"]["author"] = copy.deepcopy(DEFAULT_AUTHOR)

        # Fill seo auto fields (canonical + hreflang for blog only)
        if self.CONTENT_TYPE == "blog":
            data.setdefault("seo", {})
            data["seo"]["canonical"] = canonical
            data["seo"]["hreflang"] = hreflang

            # Schema mainEntityOfPage (for blog only)
            schema = data.get("seo", {}).get("schema", {})
            schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": canonical}
            data["seo"]["schema"] = schema

            # Fill content dates (blog only)
            data.setdefault("content", {})
            data["content"]["publishedAt"] = now
            data["content"]["updatedAt"] = now

        # Fill visuals based on content type
        if self.CONTENT_TYPE == "blog":
            cover_url = f"/api/assets/blogs/{content_id}/cover.webp"
            alt_text = data.get("overview", {}).get("title", "")
            # New format: flat cover field
            data.setdefault("cover", {})
            data["cover"]["url"] = cover_url
            data["cover"]["alt"] = alt_text
            # Legacy format: visuals.cover (for backward compat)
            data.setdefault("visuals", {})
            data["visuals"]["cover"] = {
                "url": cover_url,
                "alt": alt_text,
                "caption": alt_text,
            }
            data["visuals"]["thumbnail"] = {
                "url": cover_url,
                "alt": alt_text,
            }
        elif self.CONTENT_TYPE == "provider":
            cover_url = f"/api/assets/partners/{content_id}/cover.webp"
            data["cover"]["url"] = cover_url
            data["cover"]["alt"] = data.get("overview", {}).get("title", "")
        elif self.CONTENT_TYPE == "product":
            category = data.get("meta", {}).get("category", "")
            cover_url = f"/api/assets/products/{category}/{content_id}/cover.webp"
            data["cover"]["url"] = cover_url
            data["cover"]["alt"] = data.get("overview", {}).get("title", "")

        return data

    def validate_against_template(self, data: dict) -> List[str]:
        """
        Validate generated data against the hardcoded template.
        Returns a list of missing field paths.
        """
        template = TEMPLATES[self.CONTENT_TYPE]
        errors = []
        self._check_keys(template, data, "", errors)
        return errors

    def _check_keys(self, template: dict, data: dict, prefix: str, errors: List[str]):
        """Recursively check that all template keys exist in data."""
        for key, value in template.items():
            path = f"{prefix}.{key}" if prefix else key
            if key not in data:
                errors.append(f"Missing: {path}")
            elif isinstance(value, dict) and isinstance(data.get(key), dict):
                self._check_keys(value, data[key], path, errors)

    def save(self, data: dict, content_id: str, lang: str) -> Path:
        """Save generated JSON to the correct directory, and optionally push to remote."""
        if self.CONTENT_TYPE == "blog":
            output_dir = settings.BLOG_OUTPUT_DIR / lang
        elif self.CONTENT_TYPE == "service":
            output_dir = settings.SERVICE_OUTPUT_DIR / lang
        elif self.CONTENT_TYPE == "provider":
            output_dir = settings.PROVIDER_OUTPUT_DIR / lang
        elif self.CONTENT_TYPE == "product":
            category = data.get("meta", {}).get("category") or "general"
            output_dir = settings.PRODUCT_OUTPUT_BASE / category / lang
        else:
            raise ValueError(f"Unknown content type: {self.CONTENT_TYPE}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{content_id}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[Save] {output_path}")

        # Push to remote server if --sync flag is set
        if self.sync:
            self._sync_to_remote(data, content_id)

        return output_path

    def _find_local_images(self, content_id: str) -> list:
        """Find local image files for this content item."""
        if self.CONTENT_TYPE == "blog":
            img_dir = settings.BLOG_ASSETS_DIR / content_id
        elif self.CONTENT_TYPE == "service":
            img_dir = settings.SERVICE_ASSETS_DIR / content_id
        elif self.CONTENT_TYPE == "provider":
            img_dir = settings.PROVIDER_ASSETS_DIR / content_id
        elif self.CONTENT_TYPE == "product":
            # products assets are category-nested: data/assets/products/{category}/{id}
            base = settings.PRODUCT_ASSETS_BASE
            img_dir = None
            if base.exists():
                for cat in base.iterdir():
                    if cat.is_dir() and (cat / content_id).exists():
                        img_dir = cat / content_id
                        break
            if img_dir is None:
                return []
        else:
            return []

        if not img_dir.exists():
            return []

        images = []
        for ext in ["*.webp", "*.jpg", "*.jpeg", "*.png", "*.gif"]:
            images.extend(sorted(img_dir.glob(ext)))
        return images

    def _sync_to_remote(self, data: dict, content_id: str):
        """Push content JSON and local images to the remote server."""
        from sync_client import push_to_remote

        print(f"[Sync] Pushing {self.CONTENT_TYPE}/{content_id} to remote...")

        # Find local images to upload
        local_images = self._find_local_images(content_id)

        result = push_to_remote(self.CONTENT_TYPE, data, local_images)

        if result.get("success"):
            print(f"[Sync] ✅ {content_id} synced successfully")
            if result.get("api_result"):
                api_data = result["api_result"]
                if api_data.get("slug"):
                    print(f"[Sync]    URL: {api_data['url']}")
            image_errors = result.get("image_errors", [])
            for err in image_errors:
                print(f"[Sync]    ⚠️  {err}")
        else:
            msg = result.get("message", "Unknown error")
            print(f"[Sync] ❌ Failed: {msg}")
