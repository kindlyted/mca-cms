#!/usr/bin/env python3
"""
MCA-CMS JSON Generator — CLI Entry Point

Usage:
  python main.py blog --topic "dental implants in Shanghai" --lang en
  python main.py service --name "acupuncture" --lang en
  python main.py provider --name "Beijing Tongren Eye Hospital" --lang en
  python main.py blog --topic "..." --lang all
  python main.py validate --file path/to/file.json
"""

import sys
import argparse
import json
from pathlib import Path

# Add cms directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from generators.blog_generator import BlogGenerator
from generators.service_generator import ServiceGenerator
from generators.provider_generator import ProviderGenerator
from generators.product_generator import ProductGenerator
from validators.schema_validator import validate_file
from config import settings


def generate_blog(args):
    """Generate blog post(s)."""
    if not args.md and not args.topic:
        print("Error: Either --topic (traditional mode) or --md (MD mode) is required")
        return
    if args.md and args.topic:
        print("Warning: Both --topic and --md provided. Using MD mode.")

    generator = BlogGenerator(provider=args.provider, sync=args.sync)
    languages = settings.LANGUAGES if args.lang == "all" else [args.lang]

    for lang in languages:
        result = generator.generate(
            topic=args.topic,
            md_path=args.md,
            content_id=args.id,
            lang=lang,
            slug=args.slug,
            style=args.style,
            featured=args.featured,
        )
        print(f"\n✅ Blog generated: {result['meta']['id']} ({lang})")


def generate_service(args):
    """Generate service page(s)."""
    # Validate mode requirements
    if not args.md and not args.name:
        print("Error: Either --name (traditional mode) or --md (MD mode) is required")
        return
    if args.md and args.name:
        print("Warning: Both --name and --md provided. Using MD mode.")

    generator = ServiceGenerator(provider=args.provider, sync=args.sync)
    languages = settings.LANGUAGES if args.lang == "all" else [args.lang]

    for lang in languages:
        result = generator.generate(
            service_name=args.name,
            key_details=args.details or "",
            md_path=args.md,
            content_id=args.id,
            lang=lang,
            slug=args.slug,
            style=args.style,
            featured=args.featured,
        )
        print(f"\n✅ Service generated: {result['meta']['id']} ({lang})")


def generate_provider(args):
    """Generate provider page(s)."""
    # Validate mode requirements
    if not args.md and not args.name:
        print("Error: Either --name (traditional mode) or --md (MD mode) is required")
        return
    if args.md and args.name:
        print("Warning: Both --name and --md provided. Using MD mode.")

    generator = ProviderGenerator(provider=args.provider, sync=args.sync)
    languages = settings.LANGUAGES if args.lang == "all" else [args.lang]

    for lang in languages:
        result = generator.generate(
            hospital_name=args.name,
            key_info=args.details or "",
            md_path=args.md,
            content_id=args.id,
            lang=lang,
            slug=args.slug,
            style=args.style,
            featured=args.featured,
        )
        print(f"\n✅ Provider generated: {result['meta']['id']} ({lang})")


def generate_product(args):
    """Generate product page(s)."""
    if not args.name:
        print("Error: --name is required")
        return

    generator = ProductGenerator(provider=args.provider, sync=args.sync)
    languages = settings.LANGUAGES if args.lang == "all" else [args.lang]

    for lang in languages:
        result = generator.generate(
            product_name=args.name,
            key_details=args.details or "",
            content_id=args.id,
            lang=lang,
            slug=args.slug,
            style=args.style,
            featured=args.featured,
        )
        print(f"\n✅ Product generated: {result['meta']['id']} ({lang})")


def validate_json(args):
    """Validate JSON file(s) against template schema."""
    for file_path in args.files:
        is_valid, errors = validate_file(file_path)
        if is_valid:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} ({len(errors)} issues):")
            for e in errors:
                print(f"   - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="MCA-CMS JSON Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py blog --topic "dental implants in Shanghai" --lang en        # Topic → MD → JSON
  python main.py blog --topic "dental implants in Shanghai" --lang all       # All languages
  python main.py blog --topic "dental implants in Shanghai" --lang all --sync  # + push to remote
  python main.py blog --md docs/articles/ivf-cost-china-2026.md --lang fr   # Translate existing MD
  python main.py service --name "acupuncture" --lang all
  python main.py provider --name "Beijing Tongren Eye Hospital" --lang en
  python main.py validate --files data/blogs/en/test.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Blog ---
    blog_parser = subparsers.add_parser("blog", help="Generate a blog post")
    blog_parser.add_argument("--topic", "-t", help="Blog topic: generates English markdown then translates (e.g. 'dental implants in Shanghai')")
    blog_parser.add_argument("--md", help="Path to existing markdown file for translation (e.g. docs/articles/my-post.md)")
    blog_parser.add_argument("--lang", "-l", default="en", help="Language code (en, es, fr, all)")
    blog_parser.add_argument("--id", help="Custom content ID (auto-generated if omitted)")
    blog_parser.add_argument("--slug", help="Custom URL slug (auto-generated if omitted)")
    blog_parser.add_argument("--provider", "-p", default="dmx", help="LLM provider")
    blog_parser.add_argument("--sync", "-s", action="store_true", help="Push to remote server after generation")
    blog_parser.add_argument("--style", default="photorealistic", help="Image style: photorealistic, cartoon, ink-wash, minimalist, nature-healing")
    blog_parser.add_argument("--featured", type=int, choices=[0, 1], default=None, help="Override featured status (1=featured, 0=not, default=LLM decides)")

    # --- Service ---
    service_parser = subparsers.add_parser("service", help="Generate a service page")
    service_parser.add_argument("--name", "-n", help="Service name (required for traditional mode)")
    service_parser.add_argument("--details", "-d", help="Key details about the service")
    service_parser.add_argument("--md", help="Path to markdown file (for MD mode)")
    service_parser.add_argument("--lang", "-l", default="en", help="Language code")
    service_parser.add_argument("--id", help="Custom content ID")
    service_parser.add_argument("--slug", help="Custom URL slug")
    service_parser.add_argument("--provider", "-p", default="dmx", help="LLM provider")
    service_parser.add_argument("--sync", "-s", action="store_true", help="Push to remote server after generation")
    service_parser.add_argument("--style", default="photorealistic", help="Image style: photorealistic, cartoon, ink-wash, minimalist, nature-healing")
    service_parser.add_argument("--featured", type=int, choices=[0, 1], default=None, help="Override featured status (1=featured, 0=not, default=LLM decides)")

    # --- Provider ---
    provider_parser = subparsers.add_parser("provider", help="Generate a provider page")
    provider_parser.add_argument("--name", "-n", help="Hospital name (required for traditional mode)")
    provider_parser.add_argument("--details", "-d", help="Key info about the hospital")
    provider_parser.add_argument("--md", help="Path to markdown file (for MD mode)")
    provider_parser.add_argument("--lang", "-l", default="en", help="Language code")
    provider_parser.add_argument("--id", help="Custom content ID")
    provider_parser.add_argument("--slug", help="Custom URL slug")
    provider_parser.add_argument("--provider", "-p", default="dmx", help="LLM provider")
    provider_parser.add_argument("--sync", "-s", action="store_true", help="Push to remote server after generation")
    provider_parser.add_argument("--style", default="photorealistic", help="Image style: photorealistic, cartoon, ink-wash, minimalist, nature-healing")
    provider_parser.add_argument("--featured", type=int, choices=[0, 1], default=None, help="Override featured status (1=featured, 0=not, default=LLM decides)")

    # --- Product ---
    product_parser = subparsers.add_parser("product", help="Generate a product page")
    product_parser.add_argument("--name", "-n", help="Product name (required)")
    product_parser.add_argument("--details", "-d", help="Key details about the product")
    product_parser.add_argument("--lang", "-l", default="en", help="Language code (en, fr, de, all)")
    product_parser.add_argument("--id", help="Custom content ID")
    product_parser.add_argument("--slug", help="Custom URL slug")
    product_parser.add_argument("--provider", "-p", default="dmx", help="LLM provider")
    product_parser.add_argument("--sync", "-s", action="store_true", help="Push to remote server after generation")
    product_parser.add_argument("--style", default="photorealistic", help="Image style: photorealistic, cartoon, ink-wash, minimalist, nature-healing")
    product_parser.add_argument("--featured", type=int, choices=[0, 1], default=None, help="Override featured status (1=featured, 0=not, default=LLM decides)")

    # --- Validate ---
    validate_parser = subparsers.add_parser("validate", help="Validate JSON files")
    validate_parser.add_argument("--files", "-f", nargs="+", required=True, help="JSON file paths")

    args = parser.parse_args()

    if args.command == "blog":
        generate_blog(args)
    elif args.command == "service":
        generate_service(args)
    elif args.command == "provider":
        generate_provider(args)
    elif args.command == "product":
        generate_product(args)
    elif args.command == "validate":
        validate_json(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
