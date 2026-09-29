"""Tavily 搜索服务 — 为内容生成获取权威参考资料。

可选依赖：需要 `pip install tavily-python` 并在 cms/.env 配置 API_KEY_TAVILY。
未配置时所有函数安全返回空（不影响生成流程）。
"""

import os
import re
from typing import List, Dict, Optional

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


def _get_client() -> Optional["TavilyClient"]:
    """初始化 Tavily 客户端。"""
    api_key = os.getenv("API_KEY_TAVILY")
    if not api_key or not TavilyClient:
        return None
    return TavilyClient(api_key)


# ============ 权威来源类型识别 ============

AUTHORITY_PATTERNS = [
    (r"\.gov\b|\.gov\.|\.mil\b", "government"),
    (r"\.edu\b|university|college|\.ac\.", "education"),
    (r"who\.int|un\.org|worldbank|oecd|imf|unicef", "official"),
    (r"reuters|bloomberg|bbc\.|wsj\.|ft\.com|economist|apnews", "media"),
    (r"\.org\b", "organization"),
]


def check_authority_type(url: str) -> str:
    """判断 URL 的权威来源类型。"""
    url_lower = url.lower()
    for pattern, atype in AUTHORITY_PATTERNS:
        if re.search(pattern, url_lower):
            return atype
    return "general"


# ============ 搜索主函数 ============


def search_sources(
    query: str,
    max_results: int = 5,
    search_depth: str = "advanced",
) -> List[Dict]:
    """对单一查询词执行 Tavily 搜索。

    Returns:
        搜索结果列表，每条含 title, url, content, score, authority_type
    """
    client = _get_client()
    if not client:
        return []

    try:
        response = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
        )
        results = []
        for r in response.get("results", []):
            url = r.get("url", "")
            results.append({
                "title": r.get("title", ""),
                "url": url,
                "content": r.get("content", ""),
                "score": r.get("score", 0),
                "authority_type": check_authority_type(url),
            })
        return results
    except Exception as e:
        print(f"  [Tavily] Search failed for '{query}': {e}")
        return []


def search_sources_multi(
    queries: List[str],
    max_results_per_query: int = 5,
    min_score: float = 0.3,
    max_total: int = 8,
) -> List[Dict]:
    """多路 Tavily 搜索，合并、去重、排序、过滤。"""
    all_results = []
    for query in queries[:4]:  # 最多 4 路
        results = search_sources(query, max_results_per_query)
        all_results.extend(results)

    # 去重 (by URL)
    seen_urls = set()
    unique = []
    for r in sorted(all_results, key=lambda x: x.get("score", 0), reverse=True):
        url = r.get("url", "")
        if url and url not in seen_urls and r.get("score", 0) >= min_score:
            seen_urls.add(url)
            unique.append(r)

    return unique[:max_total]


def build_sources_context(
    topic: str,
    extra_keywords: List[str] = None,
    max_total: int = 6,
) -> str:
    """构建 sources context 文本，插入到 prompt 中供 LLM 使用。

    Returns:
        格式化的来源上下文文本；未配置/无结果时返回空字符串。
    """
    queries = [topic]
    if extra_keywords:
        queries.extend(extra_keywords)

    sources = search_sources_multi(queries, max_total=max_total)

    if not sources:
        return ""

    # 按权威类型分组排序
    priority = {"government": 0, "education": 1, "official": 2, "media": 3,
                 "organization": 4, "general": 5}
    sources.sort(key=lambda x: (priority.get(x.get("authority_type", "general"), 5),
                                -x.get("score", 0)))

    lines = ["## Reference Sources from Web Search", ""]
    for i, src in enumerate(sources, 1):
        lines.append(f"Source {i}: {src['title']}")
        lines.append(f"  URL: {src['url']}")
        lines.append(f"  Type: {src['authority_type']}")
        if src.get("content"):
            content_preview = src["content"][:500]
            lines.append(f"  Summary: {content_preview}")
        lines.append("")

    return "\n".join(lines)
