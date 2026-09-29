"""
Provider Generator — Generate provider (hospital) JSON with LLM.

Two modes:
  1. Traditional mode: Input name + details → LLM generates full content
  2. MD mode: Input MD file path → LLM translates to target language + generates SEO
"""

import re
from pathlib import Path
from typing import Dict, Optional
from generators.base import (
    BaseGenerator,
    slugify,
    calculate_read_time,
    now_iso,
    today_str,
    strip_body_sections,
    download_provider_cover,
)
from llmcore import invoke_llm_json
from config import settings


# =============================================================================
# City → Chinese Geographic Region Mapping (deterministic, LLM-agnostic)
# =============================================================================
CITY_TO_REGION = {
    # North China (华北)
    "beijing": "North China", "tianjin": "North China",
    "shijiazhuang": "North China", "tangshan": "North China", "baoding": "North China",
    "taiyuan": "North China", "datong": "North China",
    "hohhot": "North China", "baotou": "North China",
    # Northeast China (东北)
    "shenyang": "Northeast China", "dalian": "Northeast China",
    "changchun": "Northeast China", "jilin": "Northeast China",
    "harbin": "Northeast China", "daqing": "Northeast China",
    # East China (华东)
    "shanghai": "East China",
    "nanjing": "East China", "suzhou": "East China", "wuxi": "East China",
    "hangzhou": "East China", "ningbo": "East China",
    "hefei": "East China", "fuzhou": "East China", "xiamen": "East China",
    "nanchang": "East China",
    "jinan": "East China", "qingdao": "East China", "yantai": "East China", "weihai": "East China",
    # South China (华南)
    "guangzhou": "South China", "shenzhen": "South China",
    "zhuhai": "South China", "dongguan": "South China", "foshan": "South China",
    "nanning": "South China", "guilin": "South China",
    "haikou": "South China", "sanya": "South China",
    # Central China (华中)
    "wuhan": "Central China", "changsha": "Central China",
    "zhengzhou": "Central China", "luoyang": "Central China",
    # Southwest China (西南)
    "chengdu": "Southwest China", "chongqing": "Southwest China",
    "kunming": "Southwest China", "guiyang": "Southwest China",
    "lhasa": "Southwest China",
    # Northwest China (西北)
    "xian": "Northwest China", "xi'an": "Northwest China",
    "lanzhou": "Northwest China", "xining": "Northwest China",
    "yinchuan": "Northwest China", "urumqi": "Northwest China",
}


def resolve_region(city: str) -> str:
    """Map a Chinese city name to its geographic region, case-insensitive.

    Returns the region string, or None if the city is not recognised.
    """
    key = city.strip().lower()
    return CITY_TO_REGION.get(key)


class ProviderGenerator(BaseGenerator):
    CONTENT_TYPE = "provider"

    def generate(
        self,
        hospital_name: str = None,
        key_info: str = "",
        md_path: str = None,
        content_id: str = None,
        lang: str = "en",
        slug: str = None,
        style: str = "photorealistic",
        featured: bool = None,
    ) -> dict:
        """
        Generate a complete provider JSON.

        Two modes:
          1. Name mode: Input hospital name → LLM generates English markdown → saves to data/partners/
          2. MD mode: Input md_path → LLM translates existing markdown to target language

        Args:
            hospital_name: Hospital name (e.g. "Beijing Tongren Eye Hospital") — required for name mode
            key_info: Additional key information about the hospital
            md_path: Path to markdown file — for MD mode
            content_id: Optional ID, auto-generated from hospital_name or filename
            lang: Language code
            slug: Optional URL slug

        Returns:
            Complete provider dict
        """
        from_name = bool(hospital_name and not md_path)

        # Phase 0: Name mode — generate English markdown first
        if from_name:
            if not content_id:
                content_id = slugify(hospital_name)
            if not slug:
                slug = content_id
            md_path = str(settings.PROVIDER_OUTPUT_DIR / f"{content_id}.md")
            if not Path(md_path).exists():
                self._generate_and_save_md(hospital_name, key_info, content_id)

        # Phase 1: MD mode — always
        if not content_id:
            content_id = slugify(Path(md_path).stem)
        if not slug:
            slug = content_id

        source_label = hospital_name or Path(md_path).name
        print(f"\n{'='*60}")
        print(f"Provider Generator: {source_label}")
        print(f"Mode: {'Name → ' if from_name else ''}MD Mode | ID: {content_id} | Lang: {lang}")
        print(f"{'='*60}\n")

        print("[Step 1/2] Loading Markdown file...")
        md_content = self._load_markdown_file(md_path)

        print("\n[Step 2/2] Translating & SEO...")
        content_data = self._translate_content(md_content, lang)

        inst_from_llm = content_data.get("institution", {})
        llm_city = inst_from_llm.get("address", {}).get("city", "")
        analysis = {
            "type": inst_from_llm.get("type", ""),
            "region": resolve_region(llm_city) or inst_from_llm.get("region", ""),
            "country": inst_from_llm.get("country", ""),
            "featured": False,
            "priority": 5,
            "institution": inst_from_llm if inst_from_llm else {},
            "doctors": [],
            "serviceTypes": []
        }

        result = self._assemble(content_id, lang, slug, analysis, content_data, is_md_mode=True, featured=featured)

        # Cover image (always, with exists check)
        print(f"\n[Images] Downloading provider cover image...")
        download_provider_cover(content_id, f"{hospital_name or content_id} China hospital building", style=style)

        errors = self.validate_against_template(result)
        if errors:
            print(f"  ⚠️ Validation issues ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")
        else:
            print("  ✅ Validation passed")

        self.save(result, content_id, lang)

        return result

    def _generate_and_save_md(self, hospital_name: str, key_info: str, content_id: str):
        """Generate English markdown from hospital name and save."""
        print(f"\nGenerating English markdown for: {hospital_name}")
        print(f"{'='*60}")

        print("\n[MD Gen 1/2] Provider Analysis...")
        analysis = self._analyze_provider(hospital_name, key_info, "en")

        print("\n[MD Gen 2/2] Content Generation...")
        content_data = self._generate_content(hospital_name, analysis, key_info, "en")

        desc = content_data.get("description", content_data.get("body", ""))
        overview = content_data.get("overview", {})
        title = overview.get("title", hospital_name)

        md = f"# {title}\n\n{desc}\n\n"

        services = content_data.get("services", [])
        if services:
            md += "### Services Offered\n\n"
            for s in services:
                md += f"- {s}\n"
            md += "\n"

        doctors = content_data.get("doctors", [])
        if doctors:
            md += "### Our Medical Team\n\n"
            for doc in doctors:
                md += f"#### {doc.get('name', '')}\n"
                if doc.get("title"):
                    md += f"{doc['title']}\n"
                if doc.get("qualifications"):
                    md += f"*{doc['qualifications']}*\n"
                if doc.get("specialties"):
                    md += f"**Specialties:** {', '.join(doc['specialties'])}\n"
                if doc.get("languages"):
                    md += f"**Languages:** {', '.join(doc['languages'])}\n"
                md += "\n"

        highlights = content_data.get("highlights", [])
        if highlights:
            md += "### Why Choose Us\n\n"
            for h in highlights:
                md += f"- {h}\n"
            md += "\n"

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

        md_path = settings.PROVIDER_OUTPUT_DIR / f"{content_id}.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md, encoding="utf-8")
        print(f"  ✅ Saved: {md_path}")

    def _analyze_provider(self, hospital_name: str, key_info: str, lang: str) -> dict:
        """Traditional mode Step 1: Analyze the provider for institution data, doctors, specialties."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Analyze this hospital for a medical tourism website:\n"
            f"Hospital: {hospital_name}\n"
            f"Key info: {key_info or 'General hospital information'}\n"
            f"Language: {lang_name}"
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "provider_analysis.prompt",
            temperature=0.5,
        )

        print(f"  City: {result.get('institution', {}).get('address', {}).get('city', 'N/A')}")
        print(f"  Specialty: {result.get('type', 'N/A')}")
        print(f"  Doctors: {len(result.get('doctors', []))}")

        return result

    def _generate_content(
        self,
        hospital_name: str,
        analysis: dict,
        key_info: str,
        lang: str,
    ) -> dict:
        """Traditional mode Step 2: Generate provider content, FAQ, overview."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Generate comprehensive content for a hospital profile page:\n"
            f"Hospital: {hospital_name}\n"
            f"Type: {analysis.get('type', 'hospital')}\n"
            f"City: {analysis.get('institution', {}).get('address', {}).get('city', 'Beijing')}\n"
            f"Specialties: {analysis.get('serviceTypes', [])}\n"
            f"Key info: {key_info or 'General hospital information'}\n"
            f"Language: {lang_name}\n"
            f"Institution data: {analysis.get('institution', {})}\n"
            f"Doctors data: {analysis.get('doctors', [])}\n"
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "provider_content.prompt",
            temperature=0.7,
        )

        print(f"  Title: {result.get('overview', {}).get('title', 'N/A')}")
        print(f"  Body length: {len(result.get('body', ''))} chars")
        print(f"  FAQ items: {len(result.get('faq', []))}")

        return result

    def _deep_merge(self, base: dict, overlay: dict) -> dict:
        """Deep-merge overlay into base, preserving base keys for missing overlay keys."""
        result = {}
        for key in base:
            if key in overlay:
                if isinstance(base[key], dict) and isinstance(overlay[key], dict):
                    result[key] = self._deep_merge(base[key], overlay[key])
                else:
                    result[key] = overlay[key]
            else:
                result[key] = base[key]
        for key in overlay:
            if key not in base:
                result[key] = overlay[key]
        return result

    def _translate_content(self, md_content: str, lang: str) -> dict:
        """MD mode: Translate markdown content to target language and generate SEO."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Translate and generate SEO for this provider (hospital) page content:\n\n"
            f"Target language: {lang_name}\n\n"
            f"=== START OF MARKDOWN CONTENT ===\n"
            f"{md_content}\n"
            f"=== END OF MARKDOWN CONTENT ==="
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "provider_translate.prompt",
            temperature=0.5,
        )

        print(f"  Title: {result.get('overview', {}).get('title', 'N/A')}")
        print(f"  Body length: {len(result.get('body', ''))} chars")
        print(f"  FAQ items: {len(result.get('faq', []))}")

        return result

    def _assemble(
        self,
        content_id: str,
        lang: str,
        slug: str,
        analysis: dict,
        content_data: dict,
        is_md_mode: bool,
        featured: bool = None,
    ) -> dict:
        """Assemble the final provider JSON (new minimal schema)."""
        template = self.get_template()
        result = template

        # Meta
        result["meta"]["type"] = analysis.get("type", "")
        city = analysis.get("institution", {}).get("address", {}).get("city", "")
        result["meta"]["city"] = city
        result["meta"]["region"] = resolve_region(city) or analysis.get("region", "")
        result["meta"]["country"] = analysis.get("country", "")
        result["meta"]["featured"] = analysis.get("featured", False)
        if featured is not None:
            result["meta"]["featured"] = bool(featured)
        result["meta"]["priority"] = analysis.get("priority", 5)

        # SEO (no og/twitter/schema/canonical/hreflang — generated at SSR)
        seo = content_data.get("seo", {})
        result["seo"]["title"] = seo.get("title", "")
        result["seo"]["description"] = seo.get("description", "")
        result["seo"]["keywords"] = seo.get("keywords", "")

        # Cover (partners asset namespace)
        result["cover"]["url"] = f"/api/assets/partners/{content_id}/cover.webp"
        result["cover"]["alt"] = content_data.get("overview", {}).get("title", "")

        # Overview (no summary/description — use seo.description)
        overview = content_data.get("overview", {})
        result["overview"]["title"] = overview.get("title", "")
        result["overview"]["excerpt"] = overview.get("excerpt", "")
        result["overview"]["subtitle"] = overview.get("subtitle", "")

        # Institution (deep-merge with template defaults so MD mode doesn't lose fields)
        institution = analysis.get("institution", {})
        if "rating" in institution and "reviewCount" in institution["rating"]:
            institution["rating"]["count"] = institution["rating"].pop("reviewCount")
        result["institution"] = self._deep_merge(result["institution"], institution)

        # Team (mca-cms partner schema uses `team`; provider 'doctors' is mapped here)
        result["team"] = analysis.get("doctors", [])

        # Description (narrative, no sections — fallback to stripped legacy body)
        raw_body = content_data.get("body", "")
        result["description"] = content_data.get("description", strip_body_sections(raw_body) if raw_body else "")

        # Services
        result["services"] = content_data.get("services", [])

        # Highlights
        result["highlights"] = content_data.get("highlights", analysis.get("highlights", []))

        # FAQ (use short keys q/a)
        raw_faq = content_data.get("faq", [])
        result["faq"] = [
            {"q": item.get("question", item.get("q", "")),
             "a": item.get("answer", item.get("a", ""))}
            for item in raw_faq
        ]

        # References
        raw_refs = content_data.get("references", [])
        result["references"] = [
            {"title": item.get("title", ""), "url": item.get("url", "")}
            for item in raw_refs
        ]

        # Auto-fill (id, slug, language, dates, etc.)
        result = self.auto_fill_meta(result, content_id, lang, slug)

        # Remove fields that are hardcoded in layout or generated at SSR
        result.pop("cta", None)
        result.pop("content", None)

        return result
