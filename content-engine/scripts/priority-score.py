#!/usr/bin/env python3
"""
Scores unwritten articles by SEO opportunity and prints a ranked list.
Usage: python scripts/priority-score.py [--count N]
Output: JSON list of top N unwritten articles by priority score, sorted best-first.
"""

import sys, json, os, math
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: Install 'pyyaml'.")

ROOT = Path(__file__).parent.parent
PLAN_FILE   = ROOT / "content-plan.yaml"
KW_FILE     = ROOT / "keyword-data.json"
CONTENT_DIR = ROOT / "src" / "content"

PRIORITY_WEIGHT = {"P0": 1.0, "P1": 0.85, "P2": 0.70, "P3": 0.55}

def load_keyword_data():
    if not KW_FILE.exists():
        return {}
    data = json.loads(KW_FILE.read_text(encoding="utf-8"))
    kw_map = {}
    for cluster in data.get("clusters", []):
        for kw_list_key in ("children",):
            for kw in cluster.get(kw_list_key, []):
                kw_map[kw["keyword"].lower()] = kw
        pillar = cluster.get("pillar")
        if pillar:
            kw_map[pillar["keyword"].lower()] = pillar
    return kw_map

def article_exists(cluster, slug):
    path = CONTENT_DIR / cluster / f"{slug}.md"
    return path.exists()

def score_article(article, kw_map):
    target_kw = article.get("target_keyword", "").lower()
    kw_data = kw_map.get(target_kw, {})

    search_volume = kw_data.get("search_volume", article.get("word_count", 500))
    difficulty    = kw_data.get("difficulty",    50)
    cpc           = kw_data.get("cpc",           0.5)
    priority      = article.get("priority", "P2")

    # Opportunity score: high volume + low difficulty = high score
    opportunity = search_volume * (1 - difficulty / 100)

    # CPC bonus: commercial keywords get a boost
    cpc_bonus = 1 + min(cpc / 10, 0.5)

    # Pillar bonus: pillars help the whole cluster
    pillar_bonus = 1.2 if article.get("pillar") else 1.0

    score = opportunity * cpc_bonus * pillar_bonus * PRIORITY_WEIGHT.get(priority, 0.5)
    return round(score, 1)

def main():
    args = sys.argv[1:]
    count = 10
    if "--count" in args:
        idx = args.index("--count")
        if idx + 1 < len(args):
            count = int(args[idx + 1])

    if not PLAN_FILE.exists():
        print(json.dumps({"error": "content-plan.yaml not found"}))
        sys.exit(1)

    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    articles = plan.get("articles", [])
    kw_map = load_keyword_data()

    results = []
    for article in articles:
        slug    = article.get("slug", "")
        cluster = article.get("cluster", "")
        if not slug or not cluster:
            continue

        exists = article_exists(cluster, slug)
        if exists:
            continue  # Already written

        sc = score_article(article, kw_map)
        kw_data = kw_map.get(article.get("target_keyword", "").lower(), {})

        results.append({
            "slug": slug,
            "title": article.get("title", ""),
            "cluster": cluster,
            "parent_pillar": article.get("parent_pillar", ""),
            "target_keyword": article.get("target_keyword", ""),
            "priority": article.get("priority", "P2"),
            "word_count": article.get("word_count", 2000),
            "search_volume": kw_data.get("search_volume", "?"),
            "difficulty": kw_data.get("difficulty", "?"),
            "score": sc,
            "file_path": f"src/content/{cluster}/{slug}.md",
        })

    results.sort(key=lambda x: -x["score"])
    top = results[:count]

    print(json.dumps(top, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
