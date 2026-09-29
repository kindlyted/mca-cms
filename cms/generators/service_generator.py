"""
Service Generator — Generate service JSON with LLM.

Two modes:
  1. Traditional mode: Input name + details → LLM generates full content
  2. MD mode: Input MD file path → LLM translates to target language + generates SEO
"""

from pathlib import Path
from typing import Dict, Optional
from generators.base import BaseGenerator, slugify, now_iso, today_str, download_service_cover
from llmcore import invoke_llm_json
from config import settings


class ServiceGenerator(BaseGenerator):
    CONTENT_TYPE = "service"

    def generate(
        self,
        service_name: str = None,
        key_details: str = "",
        md_path: str = None,
        content_id: str = None,
        lang: str = "en",
        slug: str = None,
        style: str = "photorealistic",
        featured: bool = None,
    ) -> dict:
        """
        Generate a complete service JSON.

        Two modes:
          1. Name mode: Input service name → LLM generates English markdown → saves to data/services/
          2. MD mode: Input md_path → LLM translates existing markdown to target language

        Args:
            service_name: Service name (e.g. "acupuncture") — required for name mode
            key_details: Additional details about the service
            md_path: Path to markdown file — for MD mode
            content_id: Optional ID, auto-generated from service_name or filename
            lang: Language code
            slug: Optional URL slug

        Returns:
            Complete service dict
        """
        from_name = bool(service_name and not md_path)

        # Phase 0: Name mode — generate English markdown first
        if from_name:
            slug_data = self._generate_slug_from_name(service_name)
            if not content_id:
                content_id = slug_data["content_id"]
            if not slug:
                slug = slug_data["slug"]
            md_path = str(settings.SERVICE_OUTPUT_DIR / f"{content_id}.md")
            if not Path(md_path).exists():
                self._generate_and_save_md(service_name, key_details, content_id)

        # Phase 1: MD mode — always
        if not content_id:
            content_id = slugify(Path(md_path).stem)
        if not slug:
            slug = content_id + "-in-china"

        source_label = service_name or Path(md_path).name
        print(f"\n{'='*60}")
        print(f"Service Generator: {source_label}")
        print(f"Mode: {'Name → ' if from_name else ''}MD Mode | ID: {content_id} | Lang: {lang}")
        print(f"{'='*60}\n")

        print("[Step 1/2] Loading Markdown file...")
        md_content = self._load_markdown_file(md_path)

        print("\n[Step 2/2] Translating & SEO...")
        content_data = self._translate_content(md_content, lang)

        analysis = {
            "category": "",
            "priceRange": "Varies",
            "duration": "Varies",
            "difficulty": "easy",
            "region": "",
            "country": "",
            "featured": False,
            "priority": 3
        }

        result = self._assemble(content_id, lang, slug, analysis, content_data, is_md_mode=True)

        # Cover image (always, with exists check)
        print("\n[Image] Downloading service cover...")
        download_service_cover(
            service_id=content_id,
            query=f"{service_name or content_id} medical service China",
            style=style,
        )

        errors = self.validate_against_template(result)
        if errors:
            print(f"  ⚠️ Validation issues ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")
        else:
            print("  ✅ Validation passed")

        self.save(result, content_id, lang)

        return result

    def _generate_slug_from_name(self, service_name: str) -> dict:
        """Step 0: Distil long service name into short semantic content_id and slug."""
        result = invoke_llm_json(
            provider=self.provider,
            user_input=f"Generate a content_id and slug for this topic: {service_name}",
            prompt_path=settings.PROMPTS_DIR / "slug_generator.prompt",
            temperature=0.3,
        )

        content_id = result.get("content_id", slugify(service_name))
        slug = result.get("slug", slugify(service_name) + "-in-china")
        print(f"  [Slug] ID: {content_id} | Slug: {slug}")
        return {"content_id": content_id, "slug": slug}

    def _generate_and_save_md(self, service_name: str, key_details: str, content_id: str):
        """Generate English markdown from service name and save."""
        print(f"\nGenerating English markdown for: {service_name}")
        print(f"{'='*60}")

        print("\n[MD Gen 1/2] Service Analysis...")
        analysis = self._analyze_service(service_name, key_details, "en")

        print("\n[MD Gen 2/2] Content Generation...")
        content_data = self._generate_content(service_name, analysis, key_details, "en")

        body = content_data.get("body", "")
        overview = content_data.get("overview", {})
        title = overview.get("title", service_name)

        md = f"# {title}\n\n{body}\n\n"

        faq = content_data.get("faq", [])
        if faq:
            md += "## FAQ\n\n"
            for item in faq:
                q = item.get("q", item.get("question", ""))
                a = item.get("a", item.get("answer", ""))
                md += f"**{q}**\n\n{a}\n\n"

        refs = content_data.get("references", [])
        if refs:
            md += "## References\n\n"
            for ref in refs:
                md += f"- [{ref.get('title', '')}]({ref.get('url', '')})\n"

        md_path = settings.SERVICE_OUTPUT_DIR / f"{content_id}.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md, encoding="utf-8")
        print(f"  ✅ Saved: {md_path}")

    def _analyze_service(self, service_name: str, key_details: str, lang: str) -> dict:
        """Traditional mode Step 1: Analyze the service for categorization and metadata."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Analyze this medical service for a medical tourism website in China:\n"
            f"Service: {service_name}\n"
            f"Details: {key_details or 'General overview'}\n"
            f"Language: {lang_name}"
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "service_analysis.prompt",
            temperature=0.5,
        )

        print(f"  Category: {result.get('category', 'N/A')}")
        print(f"  Type: {result.get('type', 'N/A')}")
        print(f"  Price range: {result.get('priceRange', 'N/A')}")

        return result

    def _generate_content(
        self,
        service_name: str,
        analysis: dict,
        key_details: str,
        lang: str,
    ) -> dict:
        """Traditional mode Step 2: Generate service content, FAQ, highlights, conditions, process."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Generate comprehensive content for a medical service page:\n"
            f"Service: {service_name}\n"
            f"Category: {analysis.get('category', 'therapy')}\n"
            f"Price range: {analysis.get('priceRange', 'Varies')}\n"
            f"Duration: {analysis.get('duration', 'Varies')}\n"
            f"Difficulty: {analysis.get('difficulty', 'easy')}\n"
            f"Details: {key_details or 'Comprehensive guide'}\n"
            f"Language: {lang_name}\n"
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "service_content.prompt",
            temperature=0.7,
        )

        print(f"  Title: {result.get('overview', {}).get('title', 'N/A')}")
        print(f"  Body length: {len(result.get('body', ''))} chars")
        print(f"  FAQ items: {len(result.get('faq', []))}")
        print(f"  Highlights: {len(result.get('highlights', []))}")

        return result

    def _translate_content(self, md_content: str, lang: str) -> dict:
        """MD mode: Translate markdown content to target language and generate SEO."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Translate and generate SEO for this service page content:\n\n"
            f"Target language: {lang_name}\n\n"
            f"=== START OF MARKDOWN CONTENT ===\n"
            f"{md_content}\n"
            f"=== END OF MARKDOWN CONTENT ==="
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "service_translate.prompt",
            temperature=0.5,
        )

        print(f"  Title: {result.get('overview', {}).get('title', 'N/A')}")
        print(f"  Body length: {len(result.get('body', ''))} chars")
        print(f"  FAQ items: {len(result.get('faq', []))}")
        print(f"  Highlights: {len(result.get('highlights', []))}")

        return result

    def _assemble(
        self,
        content_id: str,
        lang: str,
        slug: str,
        analysis: dict,
        content_data: dict,
        is_md_mode: bool,
    ) -> dict:
        """Assemble the final service JSON."""
        template = self.get_template()
        result = template

        # Meta
        result["meta"]["region"] = analysis.get("region", "")
        result["meta"]["country"] = analysis.get("country", "")
        result["meta"]["difficulty"] = analysis.get("difficulty", "easy")
        result["meta"]["duration"] = analysis.get("duration", "")
        result["meta"]["priceRange"] = analysis.get("priceRange", "")
        result["meta"]["featured"] = analysis.get("featured", False)
        result["meta"]["priority"] = analysis.get("priority", 3)

        # SEO - just title, description, keywords
        seo = content_data.get("seo", {})
        result["seo"]["title"] = seo.get("title", "")
        result["seo"]["description"] = seo.get("description", "")
        result["seo"]["keywords"] = seo.get("keywords", "")

        # Cover
        result["cover"]["url"] = f"/api/assets/services/{content_id}/cover.webp"
        result["cover"]["alt"] = content_data.get("overview", {}).get("title", "")

        # Overview
        overview = content_data.get("overview", {})
        result["overview"]["title"] = overview.get("title", "")
        result["overview"]["excerpt"] = overview.get("excerpt", "")
        result["overview"]["subtitle"] = overview.get("subtitle", "")

        # Description (short narrative, no markdown headings)
        result["description"] = content_data.get("description", content_data.get("body", ""))

        # mca-cms structured sections (intro / procedure / comparison / outcome)
        result["introduction"] = content_data.get("introduction", "")
        result["procedure"] = content_data.get("procedure", content_data.get("treatmentProcedure", ""))
        result["comparison"] = content_data.get("comparison", content_data.get("costComparison", ""))
        result["outcome"] = content_data.get("outcome", content_data.get("aftercare", ""))

        # Pricing (tiers now have per-tier inclusions)
        pricing = content_data.get("pricing", {
            "currency": "USD", "tiers": [], "exclusions": [], "exampleTotal": {}
        })
        # Backward compat: if LLM still outputs pricing-level inclusions, distribute to each tier
        old_incl = pricing.pop("inclusions", None)
        if old_incl and pricing.get("tiers"):
            for tier in pricing["tiers"]:
                if "inclusions" not in tier:
                    tier["inclusions"] = list(old_incl)
        result["pricing"] = pricing

        # Testimonials
        result["testimonials"] = content_data.get("testimonials", [])

        # FAQ - convert to short format {q, a}
        raw_faq = content_data.get("faq", [])
        result["faq"] = [
            {"q": item.get("q", item.get("question", "")),
             "a": item.get("a", item.get("answer", ""))}
            for item in raw_faq
        ]

        # Highlights
        result["highlights"] = content_data.get("highlights", [])

        # Conditions
        result["conditions"] = content_data.get("conditions", {"title": "", "items": []})

        # Process
        result["process"] = content_data.get("process", {"title": "", "steps": []})

        # References
        result["references"] = content_data.get("references", [])

        # Auto-fill (sets _type, meta.id/language/status/dates/slug, default author)
        result = self.auto_fill_meta(result, content_id, lang, slug)

        # Override default author if LLM provided a name
        llm_author = content_data.get("author")
        if llm_author and llm_author.get("name"):
            result["meta"]["author"] = {
                "id": "yourbrand-team",
                "name": llm_author["name"],
                "role": llm_author.get("role", "Editorial Team"),
                "url": "https://www.yourdomain.com/about"
            }

        return result
