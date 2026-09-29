"""
Product Generator — Generate product JSON with LLM.

Name mode: product name (+ optional details) -> LLM generates full product content
including commerce fields (price, compareAtPrice, colors, dimensions, thickness,
sizes, inStock) that match the mca-cms `products` entity schema.
"""

from generators.base import BaseGenerator, slugify, generate_image_with_ai
from llmcore import invoke_llm_json
from config import settings


class ProductGenerator(BaseGenerator):
    CONTENT_TYPE = "product"

    def generate(
        self,
        product_name: str = None,
        key_details: str = "",
        content_id: str = None,
        lang: str = "en",
        slug: str = None,
        style: str = "photorealistic",
        featured: bool = None,
    ) -> dict:
        """Generate a complete product JSON."""
        if not product_name:
            raise ValueError("product_name is required")

        if not content_id:
            content_id = slugify(product_name)
        if not slug:
            slug = content_id

        print(f"\n{'='*60}")
        print(f"Product Generator: {product_name}")
        print(f"Mode: Name Mode | ID: {content_id} | Lang: {lang}")
        print(f"{'='*60}\n")

        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        print("[Step 1/1] Generating product content & SEO...")
        content_data = invoke_llm_json(
            provider=self.provider,
            user_input=(
                f"Generate a complete product page JSON for a shop website:\n"
                f"Product: {product_name}\n"
                f"Details: {key_details or 'General product information'}\n"
                f"Language: {lang_name}\n"
            ),
            prompt_path=settings.PROMPTS_DIR / "product_content.prompt",
            temperature=0.7,
        )

        result = self._assemble(content_id, lang, slug, content_data)

        # Cover image (product: category-nested under data/assets/products/{category}/{id})
        category = result.get("meta", {}).get("category", "general")
        cover_path = settings.PRODUCT_ASSETS_BASE / category / content_id / "cover.webp"
        if not cover_path.exists():
            print("\n[Image] Generating product cover...")
            generate_image_with_ai(f"{product_name} product", cover_path, content_type="product", style=style)

        errors = self.validate_against_template(result)
        if errors:
            print(f"  ⚠️ Validation issues ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")
        else:
            print("  ✅ Validation passed")

        self.save(result, content_id, lang)
        return result

    def _assemble(self, content_id: str, lang: str, slug: str, content_data: dict) -> dict:
        result = self.get_template()

        # meta.category drives data/products/{category}/{lang}
        result["meta"]["category"] = content_data.get("category", "general")

        # SEO
        seo = content_data.get("seo", {})
        result["seo"]["title"] = seo.get("title", "")
        result["seo"]["description"] = seo.get("description", "")
        result["seo"]["keywords"] = seo.get("keywords", [])

        # Overview
        overview = content_data.get("overview", {})
        result["overview"]["title"] = overview.get("title", "")
        result["overview"]["excerpt"] = overview.get("excerpt", "")
        result["overview"]["subtitle"] = overview.get("subtitle", "")

        # Description
        result["description"] = content_data.get("description", "")

        # Commerce fields
        result["brand"] = content_data.get("brand", "")
        result["price"] = content_data.get("price", 0)
        result["compareAtPrice"] = content_data.get("compareAtPrice")
        result["currency"] = content_data.get("currency", "USD")
        result["colors"] = content_data.get("colors", [])
        result["dimensions"] = content_data.get("dimensions", "")
        result["thickness"] = content_data.get("thickness", "")
        result["sizes"] = content_data.get("sizes", [])
        result["inStock"] = content_data.get("inStock", True)

        # Highlights / specs / pricing / faq / references
        result["highlights"] = content_data.get("highlights", [])
        result["specs"] = content_data.get("specs", [])
        result["pricing"] = content_data.get("pricing", result["pricing"])
        result["faq"] = [
            {"q": item.get("q", item.get("question", "")),
             "a": item.get("a", item.get("answer", ""))}
            for item in content_data.get("faq", [])
        ]
        result["references"] = content_data.get("references", [])

        result = self.auto_fill_meta(result, content_id, lang, slug)
        return result
