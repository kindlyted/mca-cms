"""
SyncClient — HTTP client for pushing content to the remote Nuxt server.

Used by both sync.py (bulk) and base.py (per-item after generation).
"""

import requests
from pathlib import Path

from config import settings

# content_type (internal) -> mca-cms API route path (index.post endpoint)
_API_PATH = {"blog": "blog", "service": "services", "provider": "partners", "product": "products"}
# content_type -> multipart id field for the upload endpoint
_ID_FIELD = {"blog": "articleId", "service": "serviceId", "provider": "partnerId", "product": "productId"}


def _api_path(content_type: str) -> str:
    return _API_PATH.get(content_type, f"{content_type}s")


def _id_field(content_type: str) -> str:
    return _ID_FIELD.get(content_type, f"{content_type}Id")


class SyncClient:
    """HTTP client for pushing content to the remote Nuxt server."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "SyncClient | None":
        """
        Get or create a singleton SyncClient.
        Returns None if REMOTE_API_URL is not configured.
        """
        if cls._instance is None:
            if not settings.REMOTE_API_URL or not settings.REMOTE_API_KEY:
                return None
            cls._instance = cls(settings.REMOTE_API_URL, settings.REMOTE_API_KEY)
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton (useful after config changes)."""
        cls._instance = None

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
        })

    def push_content(self, content_type: str, data: dict) -> dict:
        """
        Push a single content item to the remote server.

        Args:
            content_type: "blog", "service", or "provider"
            data: The full JSON data object

        Returns:
            API response dict
        """
        # mca-cms create endpoint is POST /api/{api_path} (index.post)
        api_path = _api_path(content_type)
        url = f"{self.base_url}/api/{api_path}"
        resp = self.session.post(url, json=data, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def upload_image(self, content_type: str, content_id: str, image_path: Path, filename: str = None) -> dict:
        """
        Upload an image file for a content item.

        Args:
            content_type: "blog", "service", or "provider"
            content_id: The content ID
            image_path: Local path to the image file
            filename: Optional custom filename

        Returns:
            API response dict
        """
        api_path = _api_path(content_type)
        url = f"{self.base_url}/api/{api_path}/upload"

        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/webp")}
            data = {_id_field(content_type): content_id}
            if content_type == "product":
                # derive category from local path: .../assets/products/{category}/{id}/file.webp
                parts = list(Path(image_path).parts)
                if "products" in parts:
                    idx = parts.index("products")
                    if idx + 1 < len(parts):
                        data["category"] = parts[idx + 1]
            if filename:
                data["filename"] = filename

            max_attempts = 3
            last_error = None
            for attempt in range(max_attempts):
                try:
                    resp = self.session.post(url, files=files, data=data, timeout=120)
                    resp.raise_for_status()
                    return resp.json()
                except requests.exceptions.HTTPError as e:
                    detail = ""
                    try:
                        detail = e.response.json().get("statusMessage", e.response.text[:300])
                    except Exception:
                        detail = e.response.text[:300]
                    raise Exception(f"HTTP {e.response.status_code}: {detail}")
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        import time
                        wait = (attempt + 1) * 2
                        print(f"  [Sync] Upload retry {attempt + 1}/{max_attempts} after {wait}s ({e})")
                        time.sleep(wait)
                        # Re-open the file for the retry
                        f.seek(0)
                    else:
                        raise
            raise last_error

    def check_health(self) -> bool:
        """Check if the remote server is reachable."""
        try:
            resp = self.session.get(f"{self.base_url}/api/blog", timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def delete_content(self, content_type: str, content_id: str) -> dict:
        """
        Delete a content item from the remote server.

        Args:
            content_type: "blog", "service", or "provider"
            content_id: The content ID to delete

        Returns:
            API response dict
        """
        api_path = _api_path(content_type)
        url = f"{self.base_url}/api/{api_path}/{content_id}"
        resp = self.session.delete(url, timeout=60)
        resp.raise_for_status()
        return resp.json()


def push_to_remote(content_type: str, data: dict, local_images: list[Path] = None) -> dict:
    """
    Convenience function: push content + upload local images.

    Args:
        content_type: "blog", "service", or "provider"
        data: The full JSON data object
        local_images: Optional list of local image Paths to upload

    Returns:
        Result dict with success, message, image_errors
    """
    client = SyncClient.get_instance()
    if not client:
        return {"success": False, "message": "REMOTE_API_URL or REMOTE_API_KEY not configured"}

    content_id = data.get("meta", {}).get("id", "unknown")
    image_errors = []

    try:
        # Step 1: Upload images first
        if local_images:
            for img_path in local_images:
                try:
                    img_result = client.upload_image(content_type, content_id, img_path, img_path.name)
                    if not img_result.get("success"):
                        image_errors.append(f"Upload failed: {img_path.name}")
                except Exception as e:
                    image_errors.append(f"Upload error ({img_path.name}): {e}")

        # Step 2: Push JSON after images
        result = client.push_content(content_type, data)

        if not result.get("success"):
            return {"success": False, "message": f"API returned failure: {result}"}

        return {
            "success": True,
            "content_id": content_id,
            "api_result": result.get("data", {}),
            "image_errors": image_errors,
        }

    except requests.exceptions.HTTPError as e:
        resp = e.response
        try:
            detail = resp.json().get("statusMessage", resp.text[:200])
        except Exception:
            detail = resp.text[:200]
        return {"success": False, "message": f"HTTP {resp.status_code}: {detail}"}

    except Exception as e:
        return {"success": False, "message": str(e)}
