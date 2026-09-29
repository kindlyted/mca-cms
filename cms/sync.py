#!/usr/bin/env python3
"""
MCA-CMS Content Sync — Bulk push generated JSON + images to remote server.

Usage:
  # Sync all content (blog, service, provider)
  python sync.py

  # Sync specific content type
  python sync.py --type blog
  python sync.py --type service
  python sync.py --type provider

  # Sync specific language
  python sync.py --lang en

  # Dry run (show what would be synced without uploading)
  python sync.py --dry-run
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add cms directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

import requests
from config import settings
from sync_client import SyncClient, push_to_remote


# =============================================================================
# Content Scanner
# =============================================================================

def scan_content(content_type: str, lang: str = None) -> list[dict]:
    """
    Scan local data directory for generated content.

    Returns list of { content_id, lang, json_path, data }
    """
    data_dir = settings.DATA_DIR

    if content_type == "blog":
        base_dir = settings.BLOG_OUTPUT_DIR
    elif content_type == "service":
        base_dir = settings.SERVICE_OUTPUT_DIR
    elif content_type == "provider":
        base_dir = settings.PROVIDER_OUTPUT_DIR
    else:
        raise ValueError(f"Unknown content type: {content_type}")

    if not base_dir.exists():
        print(f"  [Scan] Directory not found: {base_dir}")
        return []

    results = []

    for json_file in sorted(base_dir.rglob("*.json")):
        relative = json_file.relative_to(base_dir)
        parts = relative.parts

        if len(parts) == 2:
            file_lang = parts[0]
            file_id = parts[1].replace(".json", "")
        elif len(parts) == 1:
            file_lang = "en"
            file_id = parts[0].replace(".json", "")
        else:
            continue

        if lang and file_lang != lang:
            continue

        if file_lang not in settings.LANGUAGES:
            continue

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            content_id = data.get("meta", {}).get("id", file_id)
            content_lang = data.get("meta", {}).get("language", file_lang)

            results.append({
                "content_id": content_id,
                "lang": content_lang,
                "json_path": json_file,
                "data": data,
            })
        except Exception as e:
            print(f"  [Scan] Error reading {json_file}: {e}")

    return results


def find_local_images(content_type: str, content_id: str) -> list[Path]:
    """Find all local image files for a content item."""
    if content_type == "blog":
        img_dir = settings.BLOG_ASSETS_DIR / content_id
    elif content_type == "service":
        img_dir = settings.SERVICE_ASSETS_DIR / content_id
    elif content_type == "provider":
        img_dir = settings.PROVIDER_ASSETS_DIR / content_id
    else:
        return []

    if not img_dir.exists():
        return []

    images = []
    for ext in ["*.webp", "*.jpg", "*.jpeg", "*.png", "*.gif"]:
        images.extend(sorted(img_dir.glob(ext)))

    return images


# =============================================================================
# Sync Logic
# =============================================================================

def sync_content(
    content_type: str,
    lang: str = None,
    dry_run: bool = False,
) -> dict:
    """Sync all content of a given type to the remote server."""
    stats = {"total": 0, "synced": 0, "failed": 0, "images_synced": 0}

    items = scan_content(content_type, lang)
    if not items:
        print(f"  [{content_type.upper()}] No content found to sync")
        return stats

    print(f"\n{'='*60}")
    print(f"  Syncing {content_type.upper()}: {len(items)} item(s)")
    print(f"{'='*60}")

    for item in items:
        stats["total"] += 1
        content_id = item["content_id"]
        content_lang = item["lang"]

        print(f"\n  [{content_type.upper()}] {content_id} ({content_lang})")

        local_images = find_local_images(content_type, content_id)

        if dry_run:
            print(f"    [DRY RUN] Would sync JSON: {item['json_path'].name}")
            if local_images:
                print(f"    [DRY RUN] Would upload {len(local_images)} image(s)")
                for img in local_images:
                    print(f"      - {img.name}")
            stats["synced"] += 1
            continue

        result = push_to_remote(content_type, item["data"], local_images)

        if result.get("success"):
            print(f"    ✅ Synced successfully")
            image_errors = result.get("image_errors", [])
            for err in image_errors:
                print(f"    ⚠️  {err}")
            stats["synced"] += 1
        else:
            msg = result.get("message", "Unknown error")
            print(f"    ❌ Failed: {msg}")
            stats["failed"] += 1

    return stats


# =============================================================================
# Delete Content
# =============================================================================

def delete_content(content_type: str, content_id: str) -> bool:
    """
    Delete a content item from the remote server.

    Args:
        content_type: "blog", "service", or "provider"
        content_id: The content ID to delete

    Returns:
        True if successful, False otherwise
    """
    client = SyncClient.get_instance()
    if not client:
        print("❌ SyncClient not initialized")
        return False

    print(f"Deleting {content_type} '{content_id}'...")
    try:
        result = client.delete_content(content_type, content_id)
        if result.get("success"):
            print(f"✅ {content_type.capitalize()} '{content_id}' deleted successfully")
            return True
        else:
            msg = result.get("message", "Unknown error")
            print(f"❌ Delete failed: {msg}")
            return False
    except requests.exceptions.HTTPError as e:
        resp = e.response
        try:
            detail = resp.json().get("statusMessage", resp.text[:200])
        except Exception:
            detail = resp.text[:200]
        print(f"❌ HTTP {resp.status_code}: {detail}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="MCA-CMS Content Sync — Push generated content to remote server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync.py                        # Sync all content
  python sync.py --type blog            # Sync blog posts only
  python sync.py --type service --lang en  # Sync English services
  python sync.py --dry-run              # Preview without uploading
  python sync.py --delete service abc123  # Delete a service
        """,
    )

    parser.add_argument(
        "--type", "-t",
        choices=["blog", "service", "provider"],
        help="Content type to sync (default: all)",
    )
    parser.add_argument(
        "--lang", "-l",
        help="Language code to sync (e.g. en, es, fr)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview what would be synced without uploading",
    )
    parser.add_argument(
        "--delete", "-d",
        nargs=2,
        metavar=("TYPE", "ID"),
        help="Delete a content item (e.g. 'service svc123')",
    )

    args = parser.parse_args()

    # Handle delete command
    if args.delete:
        content_type, content_id = args.delete
        # Validate configuration
        if not settings.REMOTE_API_URL:
            print("❌ REMOTE_API_URL is not set in .env")
            print("   Add: REMOTE_API_URL=https://www.yourdomain.com")
            sys.exit(1)

        if not settings.REMOTE_API_KEY:
            print("❌ REMOTE_API_KEY is not set in .env")
            print("   Add: REMOTE_API_KEY=your-api-key")
            sys.exit(1)

        print(f"Remote server: {settings.REMOTE_API_URL}")
        client = SyncClient.get_instance()
        if not client:
            print("❌ Failed to initialize SyncClient")
            sys.exit(1)
        success = delete_content(content_type, content_id)
        sys.exit(0 if success else 1)

    # Validate configuration
    if not settings.REMOTE_API_URL:
        print("❌ REMOTE_API_URL is not set in .env")
        print("   Add: REMOTE_API_URL=https://www.yourdomain.com")
        sys.exit(1)

    if not settings.REMOTE_API_KEY:
        print("❌ REMOTE_API_KEY is not set in .env")
        print("   Add: REMOTE_API_KEY=your-api-key")
        sys.exit(1)

    print(f"Remote server: {settings.REMOTE_API_URL}")
    print(f"Data directory: {settings.DATA_DIR}")

    # Initialize client and health check
    client = SyncClient.get_instance()
    if not client:
        print("❌ Failed to initialize SyncClient")
        sys.exit(1)

    print("\nChecking server connectivity...")
    if not client.check_health():
        print("❌ Cannot reach remote server")
        print(f"   URL: {settings.REMOTE_API_URL}")
        sys.exit(1)
    print("✅ Server is reachable")

    # Determine content types to sync
    content_types = [args.type] if args.type else ["blog", "service", "provider"]

    # Sync each content type
    total_stats = {"total": 0, "synced": 0, "failed": 0, "images_synced": 0}

    for ct in content_types:
        stats = sync_content(ct, args.lang, args.dry_run)
        for key in total_stats:
            total_stats[key] += stats.get(key, 0)

    # Summary
    print(f"\n{'='*60}")
    print(f"  SYNC SUMMARY")
    print(f"{'='*60}")
    print(f"  Total items:   {total_stats['total']}")
    print(f"  Synced:        {total_stats['synced']}")
    print(f"  Failed:        {total_stats['failed']}")

    if args.dry_run:
        print(f"\n  (Dry run — no data was uploaded)")

    if total_stats["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
