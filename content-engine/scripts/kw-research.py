#!/usr/bin/env python3
"""
DataForSEO Keyword Research + Clustering for DesigXner
Fetches ~500 web-design keywords, clusters by topic with parent/child hierarchy,
outputs keyword-data.json enriched with volume/difficulty/intent.
Usage: python scripts/kw-research.py
"""

import os, sys, json, re, base64, time
from datetime import datetime
from collections import defaultdict
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: 'requests' not installed. Run: pip install requests")

# ── Config ────────────────────────────────────────────────────────────────────
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
OUTPUT   = ROOT / "keyword-data.json"

# US English
LOCATION_CODE = 2840
LANGUAGE_CODE = "en"

# ── Seed keywords (web design agency universe) ────────────────────────────────
SEEDS = [
    "small business website design",
    "web design agency",
    "website redesign",
    "website cost small business",
    "local business website",
    "ecommerce website design",
    "web design for dentists",
    "web design for law firms",
    "best website platform small business",
    "website speed optimization",
    "SEO for small business",
    "small business branding",
    "website conversion optimization",
    "website maintenance small business",
    "AI search optimization",
]

# ── Cluster definitions (topic → signal words) ───────────────────────────────
CLUSTER_MAP = {
    "cost": ["cost", "price", "pricing", "how much", "cheap", "affordable", "budget",
             "fee", "rate", "quote", "estimate", "charge", "invest", "roi", "value"],
    "industries": ["dentist", "dental", "lawyer", "law firm", "attorney", "legal",
                   "restaurant", "cafe", "food", "plumber", "electrician", "contractor",
                   "hvac", "landscaper", "real estate", "realtor", "agent", "fitness",
                   "gym", "trainer", "ecommerce", "shop", "store", "b2b", "saas",
                   "consultant", "coach", "medical", "clinic", "doctor", "accountant",
                   "cpa", "chiropractor", "nonprofit", "daycare", "vet", "veterinar"],
    "platforms": ["wordpress", "webflow", "wix", "squarespace", "shopify", "woocommerce",
                  "framer", "cms", "builder", "platform", "host", "freelancer", "diy",
                  "agency vs", "migrate", "switch from", "headless"],
    "redesign": ["redesign", "rebuild", "revamp", "refresh", "update site", "redo",
                 "new website", "overhaul", "rebrand", "facelift"],
    "conversion": ["conversion", "convert", "leads", "bookings", "cta", "call to action",
                   "trust signal", "testimonial", "social proof", "ux", "user experience",
                   "hero section", "pricing page", "about page", "contact page", "form"],
    "performance": ["speed", "fast", "slow", "performance", "core web vitals", "pagespeed",
                    "loading", "lcp", "cls", "fid", "cdn", "cache", "lazy load", "image optim"],
    "seo": ["seo", "search engine", "google ranking", "keyword research", "backlink",
            "local seo", "serp", "organic traffic", "on-page", "technical seo",
            "google business", "schema markup", "structured data", "sitemap"],
    "brand": ["brand", "logo", "color palette", "typography", "font", "design system",
              "visual identity", "photography", "stock photo", "illustration", "icon",
              "voice and tone", "style guide"],
    "operations": ["maintenance", "hosting", "security", "backup", "analytics",
                   "gdpr", "ccpa", "privacy", "ssl", "uptime", "plugin", "update",
                   "ga4", "google analytics"],
    "ai_search": ["chatgpt", "perplexity", "ai search", "llm", "generative engine",
                  "geo optimization", "gpt", "bard", "gemini", "ai visibility",
                  "cited by ai", "ai overview", "bing chat"],
    "process": ["how to hire", "questions to ask", "red flags", "checklist",
                "timeline", "process", "framework", "template", "guide", "steps",
                "brief", "rfp", "launch", "go live"],
}

# ── DataForSEO helpers ────────────────────────────────────────────────────────
def auth_header():
    if not LOGIN or not PASSWORD:
        sys.exit("ERROR: Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in .env")
    token = base64.b64encode(f"{LOGIN}:{PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def dfs_post(endpoint, payload, retries=2):
    url = f"https://api.dataforseo.com{endpoint}"
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers=auth_header(), json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            if data.get("status_code") == 20000:
                return data
            print(f"  DFS warning {data.get('status_code')}: {data.get('status_message')}")
            return data
        except requests.RequestException as e:
            if attempt < retries:
                print(f"  Retry {attempt+1}/{retries} after error: {e}")
                time.sleep(2 ** attempt)
            else:
                print(f"  FAILED after {retries+1} attempts: {e}")
                return None

# ── Fetch related keywords for a seed ────────────────────────────────────────
def fetch_related(seed, limit=100):
    print(f"  Fetching related for: {seed!r}")
    resp = dfs_post(
        "/v3/dataforseo_labs/google/related_keywords/live",
        [{"keyword": seed, "location_code": LOCATION_CODE,
          "language_code": LANGUAGE_CODE, "limit": limit, "depth": 2,
          "include_seed_keyword": True}]
    )
    if not resp:
        return []
    keywords = []
    for task in resp.get("tasks", []):
        for result in (task.get("result") or []):
            for item in (result.get("items") or []):
                kd = item.get("keyword_data", {})
                ki = kd.get("keyword_info", {})
                intent_obj = item.get("intent", {})
                kw = kd.get("keyword", "").strip()
                if not kw:
                    continue
                keywords.append({
                    "keyword": kw,
                    "search_volume": ki.get("search_volume") or 0,
                    "cpc": ki.get("cpc") or 0.0,
                    "competition": ki.get("competition") or 0.0,
                    "difficulty": 0,
                    "intent": intent_obj.get("main_intent", "informational"),
                })
    return keywords

# ── Fetch bulk difficulty ─────────────────────────────────────────────────────
def fetch_difficulty(keywords_list):
    if not keywords_list:
        return {}
    chunks = [keywords_list[i:i+1000] for i in range(0, len(keywords_list), 1000)]
    difficulty_map = {}
    for chunk in chunks:
        resp = dfs_post(
            "/v3/dataforseo_labs/google/bulk_keyword_difficulty/live",
            [{"keywords": chunk, "location_code": LOCATION_CODE,
              "language_code": LANGUAGE_CODE}]
        )
        if not resp:
            continue
        for task in resp.get("tasks", []):
            for result in (task.get("result") or []):
                for item in (result.get("items") or []):
                    kw = item.get("keyword", "")
                    diff = item.get("keyword_difficulty", 0)
                    difficulty_map[kw] = diff
    return difficulty_map

# ── Classify keyword into cluster ─────────────────────────────────────────────
def classify(keyword):
    kl = keyword.lower()
    scores = {}
    for cluster, signals in CLUSTER_MAP.items():
        score = sum(1 for s in signals if s in kl)
        if score:
            scores[cluster] = score
    if not scores:
        return "process"
    return max(scores, key=scores.get)

# ── Build parent/child hierarchy for a cluster ────────────────────────────────
def build_hierarchy(cluster_keywords):
    sorted_kws = sorted(cluster_keywords, key=lambda x: x.get("search_volume", 0), reverse=True)
    pillar = None
    children = []
    for kw in sorted_kws:
        word_count = len(kw["keyword"].split())
        if pillar is None and word_count <= 5 and kw.get("search_volume", 0) >= 100:
            pillar = {**kw, "is_pillar": True}
        else:
            children.append({**kw, "is_pillar": False})
    if pillar is None and sorted_kws:
        pillar = {**sorted_kws[0], "is_pillar": True}
        children = [{**k, "is_pillar": False} for k in sorted_kws[1:]]
    return pillar, children

# ── Generate slug from keyword ────────────────────────────────────────────────
def to_slug(keyword):
    s = keyword.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80]

# ── Compare against existing content-plan.yaml ───────────────────────────────
def load_existing_slugs():
    try:
        import yaml
        plan_path = ROOT / "content-plan.yaml"
        if plan_path.exists():
            data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
            return {a["slug"] for a in data.get("articles", []) if "slug" in a}
    except Exception:
        pass
    return set()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=== DesigXner Keyword Research ===")
    print(f"Target: US English (location {LOCATION_CODE})")
    print(f"Seeds: {len(SEEDS)}\n")

    # 1. Collect all keywords from all seeds
    all_keywords = {}
    for seed in SEEDS:
        for kw in fetch_related(seed, limit=100):
            kw_text = kw["keyword"]
            if kw_text not in all_keywords or all_keywords[kw_text]["search_volume"] < kw["search_volume"]:
                all_keywords[kw_text] = kw
        time.sleep(0.5)

    print(f"\nTotal unique keywords collected: {len(all_keywords)}")

    # 2. Fetch difficulty for all keywords
    print("Fetching keyword difficulty...")
    difficulty_map = fetch_difficulty(list(all_keywords.keys()))
    for kw_text, kw_data in all_keywords.items():
        kw_data["difficulty"] = difficulty_map.get(kw_text, 50)

    # 3. Filter: min 50 search volume, skip very long tail (>8 words)
    filtered = [
        kw for kw in all_keywords.values()
        if kw["search_volume"] >= 50 and len(kw["keyword"].split()) <= 8
    ]
    print(f"After filtering (vol≥50, words≤8): {len(filtered)} keywords")

    # 4. Classify into clusters
    clustered = defaultdict(list)
    for kw in filtered:
        cluster = classify(kw["keyword"])
        clustered[cluster].append(kw)

    # 5. Build hierarchy + output structure
    existing_slugs = load_existing_slugs()
    new_articles = []
    clusters_output = []

    for cluster_slug, kws in clustered.items():
        pillar, children = build_hierarchy(kws)
        if not pillar:
            continue

        cluster_obj = {
            "cluster_slug": cluster_slug,
            "total_keywords": len(kws),
            "total_search_volume": sum(k.get("search_volume", 0) for k in kws),
            "pillar": pillar,
            "children": children[:50],  # top 50 children per cluster
        }
        clusters_output.append(cluster_obj)

        # Identify new slugs not in existing content-plan.yaml
        all_kws_in_cluster = [pillar] + children
        for kw in all_kws_in_cluster[:20]:  # top 20 per cluster
            slug = to_slug(kw["keyword"])
            if slug not in existing_slugs and kw.get("search_volume", 0) >= 200:
                new_articles.append({
                    "slug": slug,
                    "cluster": cluster_slug,
                    "target_keyword": kw["keyword"],
                    "search_volume": kw["search_volume"],
                    "difficulty": kw["difficulty"],
                    "intent": kw["intent"],
                    "is_pillar": kw.get("is_pillar", False),
                })

    # 6. Sort clusters by total search volume
    clusters_output.sort(key=lambda x: x["total_search_volume"], reverse=True)

    # 7. Save output
    output_data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_keywords": len(filtered),
        "total_clusters": len(clusters_output),
        "clusters": clusters_output,
    }
    OUTPUT.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ Saved keyword-data.json ({len(filtered)} keywords, {len(clusters_output)} clusters)")

    # 8. Print newly discovered articles
    if new_articles:
        print(f"\nNEW ARTICLES: {len(new_articles)} keywords not in content-plan.yaml")
        for a in sorted(new_articles, key=lambda x: x["search_volume"], reverse=True)[:20]:
            print(f"  [{a['cluster']}] {a['slug']} (vol:{a['search_volume']}, diff:{a['difficulty']}, intent:{a['intent']})")
    else:
        print("\nNo new keywords beyond existing content plan.")

    print("\nDone.")

if __name__ == "__main__":
    main()
