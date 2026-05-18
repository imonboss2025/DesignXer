#!/usr/bin/env python3
"""
Fetches top 10 organic competitor URLs from DataForSEO for a keyword.
Usage: python scripts/serp.py "keyword to research"
Output: JSON to stdout with competitor_urls, serp_features, related_questions.
"""

import sys, os, json, base64, time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: Install 'requests'.")

ROOT = Path(__file__).parent.parent
ENV_FILE = ROOT / ".env"

def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

LOGIN    = os.environ.get("DATAFORSEO_LOGIN", "").strip()
PASSWORD = os.environ.get("DATAFORSEO_PASSWORD", "").strip()

# Domains to skip in competitor analysis
SKIP_DOMAINS = {
    "wikipedia.org", "reddit.com", "quora.com", "amazon.com", "youtube.com",
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
    "pinterest.com", "yelp.com", "bbb.org", "indeed.com", "glassdoor.com",
    "gov", "edu",
}

def auth_header():
    if not LOGIN or not PASSWORD:
        sys.exit("ERROR: Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in .env")
    token = base64.b64encode(f"{LOGIN}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def should_skip(url):
    for domain in SKIP_DOMAINS:
        if domain in url:
            return True
    return False

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: serp.py \"keyword\""}))
        sys.exit(1)

    keyword = " ".join(sys.argv[1:])
    print(f"SERP research for: {keyword!r}", file=sys.stderr)

    payload = [{
        "keyword": keyword,
        "location_code": 2840,
        "language_code": "en",
        "device": "desktop",
        "depth": 10,
    }]

    try:
        r = requests.post(
            "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
            headers=auth_header(),
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if data.get("status_code") != 20000:
        print(json.dumps({"error": f"DataForSEO error {data.get('status_code')}: {data.get('status_message')}"}))
        sys.exit(1)

    competitor_urls = []
    related_questions = []
    serp_features = []

    for task in data.get("tasks", []):
        for result in (task.get("result") or []):
            items = result.get("items") or []
            for item in items:
                item_type = item.get("type", "")

                if item_type == "organic":
                    url = item.get("url", "")
                    domain = item.get("domain", "")
                    if url and not should_skip(url) and len(competitor_urls) < 10:
                        competitor_urls.append({
                            "url": url,
                            "domain": domain,
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "rank_group": item.get("rank_group", 0),
                        })

                elif item_type == "people_also_ask":
                    for qa in (item.get("items") or []):
                        q = qa.get("title", "")
                        if q:
                            related_questions.append(q)

                elif item_type in ("featured_snippet", "knowledge_graph",
                                   "local_pack", "top_stories", "image_pack"):
                    serp_features.append(item_type)

    result_out = {
        "keyword": keyword,
        "competitor_urls": competitor_urls,
        "related_questions": related_questions[:8],
        "serp_features": list(set(serp_features)),
        "total_organic_found": len(competitor_urls),
    }

    print(json.dumps(result_out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
