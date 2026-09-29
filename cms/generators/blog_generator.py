"""
Blog Generator — Generate blog post JSON with LLM.

Flow:
  1. Topic Analysis → extract primary_tag, audience, outline
  2. Content Generation → title, body, faq, overview
  3. SEO & Metadata → seo, tags, geo
  4. Assemble → auto-fill meta, validate, download images, save
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

from generators.base import (
    BaseGenerator,
    slugify,
    calculate_read_time,
    now_iso,
    today_str,
    strip_body_sections,
    download_blog_images,
    generate_image_with_ai,
    create_placeholder_image,
)
from llmcore import invoke_llm_json
from config import settings

# Load tag_groups from config/tags.json for group lookup
_TAGS_DICT = json.loads((Path(__file__).resolve().parent.parent.parent / "config" / "tags.json").read_text(encoding="utf-8"))
TAG_GROUPS = _TAGS_DICT.get("tag_groups", {})


class BlogGenerator(BaseGenerator):
    CONTENT_TYPE = "blog"

    @staticmethod
    def _find_tag_group(tag_id: str) -> str:
        """Find which group a tag belongs to in tag_groups."""
        for group_key, group in TAG_GROUPS.items():
            if tag_id in group:
                return group_key
        return "general"

    def generate(
        self,
        topic: str = None,
        content_id: str = None,
        lang: str = "en",
        slug: str = None,
        md_path: str = None,
        style: str = "photorealistic",
        featured: bool = None,
    ) -> dict:
        """
        Generate a complete blog post JSON.

        Two modes:
          1. Topic mode: Input topic → LLM generates English markdown → saves to docs/articles/
          2. MD mode: Input md_path → LLM translates existing markdown to target language

        Both modes converge on the same MD→translate pipeline.

        Args:
            topic: The blog topic (e.g. "dental implants in Shanghai") — required for topic mode
            content_id: Optional ID, auto-generated from topic or filename if not provided
            lang: Language code (en, es, fr)
            slug: Optional URL slug, auto-generated if not provided
            md_path: Path to markdown file — for MD mode

        Returns:
            Complete blog post dict
        """
        from_topic = bool(topic and not md_path)

        # Phase 0: Topic mode — generate English markdown file first
        if from_topic:
            slug_data = self._generate_slug_from_topic(topic)
            if not content_id:
                content_id = slug_data["content_id"]
            if not slug:
                slug = slug_data["slug"]
            md_path = str(settings.BLOG_MD_DIR / f"{content_id}.md")
            if not Path(md_path).exists():
                self._generate_and_save_md(topic, content_id)

        # Phase 1: MD mode — always, since topic mode generates MD
        if not content_id:
            content_id = slugify(Path(md_path).stem)
        if not slug:
            slug = content_id

        source_label = topic or Path(md_path).name
        print(f"\n{'='*60}")
        print(f"Blog Generator: {source_label}")
        print(f"Mode: {'Topic → ' if from_topic else ''}MD Mode | ID: {content_id} | Lang: {lang}")
        print(f"{'='*60}\n")

        print("[Step 1/2] Loading Markdown file...")
        md_content = self._load_markdown_file(md_path)

        print("\n[Step 2/2] Translating & Generating SEO...")
        content_data = self._translate_content(md_content, lang)

        analysis = {
            "primary_tag": "",
            "content_type_tag": "guide",
            "secondary_tags": [],
            "region": "",
            "country": "",
            "featured": False,
            "priority": 5,
        }

        topic_for_seo = content_data.get("title", topic or Path(md_path).stem)
        seo_data = self._generate_seo_metadata(topic_for_seo, content_data, analysis, lang)

        # Replace PLACEHOLDER_ID with actual content_id in body
        body_key = "body"
        body_val = content_data.get(body_key, "")
        if isinstance(body_val, str):
            body_val = body_val.replace("PLACEHOLDER_ID", content_id)
            content_data[body_key] = body_val
        elif isinstance(body_val, dict) and "content" in body_val:
            body_val["content"] = body_val["content"].replace("PLACEHOLDER_ID", content_id)
            content_data[body_key] = body_val

        # Step: Assemble (shared)
        print("\n[Assemble] Assembling final JSON...")
        result = self._assemble(content_id, lang, slug, analysis, content_data, seo_data, featured)

        # Validate
        errors = self.validate_against_template(result)
        if errors:
            print(f"  ⚠️ Validation issues ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")
        else:
            print("  ✅ Validation passed")

        # Download images
        body_for_images = content_data.get("body", "")
        if isinstance(body_for_images, str):
            image_queries = self._extract_image_queries(body_for_images, content_id)
            if image_queries:
                print(f"\n[Images] Downloading {len(image_queries)} images...")
                download_blog_images(content_id, image_queries, style=style)

        # Download cover image
        print("\n[Image] Downloading blog cover...")
        cover_topic = topic or content_data.get("title", content_id)
        self._download_blog_cover(content_id, cover_topic, style=style)

        # Save
        self.save(result, content_id, lang)

        return result

    def _generate_and_save_md(self, topic: str, content_id: str):
        """Generate English markdown from topic and save to docs/articles/."""
        print(f"\nGenerating English markdown for: {topic}")
        print(f"{'='*60}")

        print("\n[MD Gen 1/2] Topic Analysis...")
        analysis = self._analyze_topic(topic, "en")

        print("\n[MD Gen 2/2] Content Generation...")
        content_data = self._generate_content(topic, analysis, "en")

        body = content_data.get("body", "").replace("PLACEHOLDER_ID", content_id)
        title = content_data.get("title", topic)

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

        md_path = settings.BLOG_MD_DIR / f"{content_id}.md"
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md, encoding="utf-8")
        print(f"  ✅ Saved: {md_path}")

    def _generate_slug_from_topic(self, topic: str) -> dict:
        """Step 0: Distil long topic into short semantic content_id and slug."""
        prompt = self._load_prompt("slug_generator.prompt")
        prompt = prompt.replace("%%TOPIC%%", topic)

        result = invoke_llm_json(
            provider=self.provider,
            user_input=f"Generate a content_id and slug for this topic: {topic}",
            prompt_path=settings.PROMPTS_DIR / "slug_generator.prompt",
            temperature=0.3,
        )

        content_id = result.get("content_id", slugify(topic))
        slug = result.get("slug", slugify(topic) + "-guide")
        print(f"  [Slug] ID: {content_id} | Slug: {slug}")
        return {"content_id": content_id, "slug": slug}

    def _download_blog_cover(self, content_id: str, topic: str = None, style: str = "photorealistic"):
        """Download/generate cover image for a blog post."""
        save_path = settings.BLOG_ASSETS_DIR / content_id / "cover.webp"
        if save_path.exists():
            print(f"  [Image] Already exists: cover.webp")
            return

        query = topic or content_id.replace("-", " ")
        result = generate_image_with_ai(
            query, save_path, aspect_ratio="landscape", content_type="blog", style=style
        )
        if not result:
            print(f"  [Image] AI generation failed, creating placeholder")
            create_placeholder_image(save_path, text=f"Blog: {content_id}")

    def _analyze_topic(self, topic: str, lang: str) -> dict:
        """Step 1: Analyze the topic for primary_tag, audience, outline."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        prompt = self._load_prompt("blog_analysis.prompt")
        prompt = prompt.replace("%%TOPIC%%", topic)
        prompt = prompt.replace("%%LANGUAGE%%", lang_name)

        user_input = f"Analyze this blog topic for a professional services website: {topic}"

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "blog_analysis.prompt",
            temperature=0.5,
        )

        print(f"  Primary Tag: {result.get('primary_tag', 'N/A')}")
        print(f"  Content Type: {result.get('content_type_tag', 'N/A')}")
        print(f"  Audience: {result.get('target_audience', 'N/A')}")
        print(f"  Region: {result.get('region', 'N/A')}")

        return result

    def _generate_content(self, topic: str, analysis: dict, lang: str) -> dict:
        """Step 2: Generate the actual blog content."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Write a comprehensive blog post about: {topic}\n\n"
            f"Primary topic: {analysis.get('primary_tag', '')}\n"
            f"Content type: {analysis.get('content_type_tag', 'guide')}\n"
            f"Target audience: {analysis.get('target_audience', 'general audience')}\n"
            f"Writing approach: {analysis.get('writing_approach', 'informative')}\n"
            f"Region/Country: {analysis.get('region', '')}, {analysis.get('country', '')}\n"
            f"Language: {lang_name}\n"
        )

        # Tavily: fetch authoritative sources (optional; no-op without API_KEY_TAVILY)
        try:
            from tavily_search import build_sources_context
            sources_context = build_sources_context(
                topic,
                extra_keywords=[analysis.get("primary_tag", "")] if analysis.get("primary_tag") else None,
            )
            if sources_context:
                user_input += f"\n\n{sources_context}\n"
        except Exception as e:
            print(f"  [Tavily] skip: {e}")

        if analysis.get("outline"):
            user_input += f"\nSuggested outline:\n{analysis['outline']}"

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "blog_content.prompt",
            temperature=0.7,
        )

        title = result.get("title", topic)
        body = result.get("body", "")
        print(f"  Title: {title[:60]}...")
        print(f"  Body length: {len(body)} chars")

        return result

    def _generate_seo_metadata(self, topic: str, content_data: dict, analysis: dict, lang: str) -> dict:
        """Step 3: Generate SEO metadata, tags, and geo."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Generate SEO metadata for a blog post about: {topic}\n\n"
            f"Title: {content_data.get('title', '')}\n"
            f"Body preview: {content_data.get('body', '')[:2000]}\n"
            f"Primary specialty: {analysis.get('primary_tag', '')}\n"
            f"Language: {lang_name}\n"
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "blog_seo.prompt",
            temperature=0.5,
        )

        print(f"  SEO title: {result.get('seo', {}).get('title', 'N/A')[:60]}...")
        print(f"  Tags: {len(result.get('tags', {}).get('secondary', []))} secondary")

        return result

    def _translate_content(self, md_content: str, lang: str) -> dict:
        """MD mode: Translate markdown content to target language and generate overview + faq."""
        lang_name = {"en": "English", "fr": "French", "de": "German"}.get(lang, "English")

        user_input = (
            f"Translate and generate SEO for this blog post:\n\n"
            f"Target language: {lang_name}\n\n"
            f"=== START OF MARKDOWN CONTENT ===\n"
            f"{md_content}\n"
            f"=== END OF MARKDOWN CONTENT ==="
        )

        result = invoke_llm_json(
            provider=self.provider,
            user_input=user_input,
            prompt_path=settings.PROMPTS_DIR / "blog_translate.prompt",
            temperature=0.5,
        )

        print(f"  Title: {result.get('title', 'N/A')[:60]}...")
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
        seo_data: dict,
        featured: bool = None,
    ) -> dict:
        """Assemble the final blog post from all generated parts."""
        template = self.get_template()
        body_content = content_data.get("body", "")

        result = template

        # Meta
        result["meta"]["region"] = analysis.get("region", "")
        result["meta"]["country"] = analysis.get("country", "")
        result["meta"]["readTime"] = calculate_read_time(
            body_content if isinstance(body_content, str) else str(body_content)
        )
        result["meta"]["featured"] = analysis.get("featured", False)
        if featured is not None:
            result["meta"]["featured"] = bool(featured)
        result["meta"]["priority"] = analysis.get("priority", 5)

        # SEO
        seo = seo_data.get("seo", {})
        result["seo"]["title"] = seo.get("title", "")
        result["seo"]["description"] = seo.get("description", "")
        result["seo"]["keywords"] = seo.get("keywords", "")

        # Overview
        overview = content_data.get("overview", {})
        result["overview"]["title"] = overview.get("title", content_data.get("title", ""))
        result["overview"]["subtitle"] = overview.get("subtitle", "")
        result["overview"]["excerpt"] = overview.get("excerpt", "")

        # Body (keeps {format, content} or {format, sections})
        if isinstance(body_content, str):
            result["body"]["content"] = strip_body_sections(body_content)
        else:
            result["body"] = body_content

        # Tags — build from analysis + seo_data
        tags = seo_data.get("tags", {})
        primary_tag_id = analysis.get("primary_tag", "medical-tourism")
        content_type_tag_id = analysis.get("content_type_tag", "treatment-guide")
        secondary_tag_ids = analysis.get("secondary_tags", [])

        result["tags"]["primary"] = [{
            "id": primary_tag_id,
            "name": primary_tag_id.replace("-", " ").title(),
            "slug": primary_tag_id,
            "group": "specialty"
        }]

        secondary = []
        secondary.append({
            "id": content_type_tag_id,
            "name": content_type_tag_id.replace("-", " ").title(),
            "slug": content_type_tag_id,
            "group": "content-type"
        })
        for tag_id in secondary_tag_ids[:3]:
            tag_group = self._find_tag_group(tag_id)
            secondary.append({
                "id": tag_id,
                "name": tag_id.replace("-", " ").title(),
                "slug": tag_id,
                "group": tag_group
            })
        for tag in tags.get("secondary", []):
            if isinstance(tag, dict) and tag.get("id") not in [t["id"] for t in secondary]:
                if "group" not in tag:
                    tag["group"] = self._find_tag_group(tag.get("id", ""))
                secondary.append(tag)

        result["tags"]["secondary"] = secondary

        # FAQ — convert to short format {q, a}
        raw_faq = content_data.get("faq", [])
        result["faq"] = [
            {"q": item.get("q", item.get("question", "")),
             "a": item.get("a", item.get("answer", ""))}
            for item in raw_faq
        ]

        # Meta/content fields
        result["references"] = content_data.get("references", [])
        result["source"] = content_data.get("source", "YourBrand Research")
        result["sourceUrl"] = content_data.get("sourceUrl", "")

        # Auto-fill (id, language, dates, slug, default author)
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

    def _extract_image_queries(self, body_content: str, content_id: str) -> List[Dict]:
        """Extract image queries from markdown content."""
        # Find all image references: ![description](/path/to/image.webp)
        pattern = r'!\[(.*?)\]\((.*?)\)'
        matches = re.findall(pattern, body_content)

        queries = []
        for idx, (alt_text, url) in enumerate(matches, 1):
            # Use alt text as search query
            query = alt_text.strip()
            if query:
                queries.append({"index": idx, "query": query})

        return queries
