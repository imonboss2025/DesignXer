#!/usr/bin/env python3
"""
TF-IDF analysis + entity extraction from competitor pages.
Usage:
  python scripts/tfidf.py URL1 URL2 URL3 ...
  python scripts/tfidf.py --file urls.txt
Output: JSON to stdout with top_terms, entities, competitor_stats.
"""

import sys, re, json, math, string
from collections import Counter, defaultdict
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("ERROR: Install 'requests' and 'beautifulsoup4'.")

# ── Stop words ────────────────────────────────────────────────────────────────
STOP_WORDS = set("""
a about above after again against all also am an and any are aren't as at be
because been before being below between both but by can't cannot could couldn't
did didn't do does doesn't doing don't down during each few for from further get
got had hadn't has hasn't have haven't having he he'd he'll he's her here here's
hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't
it it's its itself just let's me more most mustn't my myself no nor not of off on
once only or other ought our ours ourselves out over own same shan't she she'd
she'll she's should shouldn't so some such than that that's the their theirs them
themselves then there there's these they they'd they'll they're they've this those
through to too under until up very was wasn't we we'd we'll we're we've were
weren't what what's when when's where where's which while who who's whom why
why's will won't would wouldn't you you'd you'll you're you've your yours yourself
yourselves one two three four five six seven eight nine ten also like many much
even well just can make use good great want need know take help based also
""".split())

# Extra web-content noise to strip
NOISE = {"click", "here", "read", "more", "learn", "share", "post", "home",
         "page", "menu", "nav", "footer", "header", "comment", "reply",
         "back", "next", "prev", "skip", "close", "open", "toggle", "show",
         "hide", "menu", "search", "follow", "subscribe", "sign", "log",
         "view", "check", "get", "start", "free", "today", "new", "best"}

# ── HTML → clean text ────────────────────────────────────────────────────────
def extract_text(html, url=""):
    soup = BeautifulSoup(html, "lxml")
    # Remove boilerplate
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Extract headings separately for entity detection
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1","h2","h3","h4"])]

    # Main content: prefer <article>, <main>, then body
    content_el = soup.find("article") or soup.find("main") or soup.find("body")
    if not content_el:
        content_el = soup

    text = content_el.get_text(" ", strip=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    word_count = len(text.split())

    return {"text": text, "headings": headings, "word_count": word_count, "url": url}

# ── Tokenize ─────────────────────────────────────────────────────────────────
def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s'-]", " ", text)
    tokens = text.split()
    return [t.strip("'-") for t in tokens
            if len(t) >= 3 and t not in STOP_WORDS and t not in NOISE
            and not t.isdigit()]

# ── TF-IDF across a corpus ────────────────────────────────────────────────────
def compute_tfidf(docs_text):
    N = len(docs_text)
    if N == 0:
        return []

    tokenized = [tokenize(doc) for doc in docs_text]

    # TF per doc
    tf_docs = [Counter(tokens) for tokens in tokenized]

    # IDF: log(N / (1 + df))
    df = Counter()
    for tokens_set in (set(t) for t in tokenized):
        df.update(tokens_set)

    # Also compute bigrams
    bigrams = []
    for tokens in tokenized:
        bigrams.append([f"{tokens[i]}_{tokens[i+1]}"
                        for i in range(len(tokens)-1)
                        if tokens[i] not in STOP_WORDS and tokens[i+1] not in STOP_WORDS])
    bigram_tf = [Counter(bg) for bg in bigrams]
    bigram_df = Counter()
    for bg_set in (set(bg) for bg in bigrams):
        bigram_df.update(bg_set)

    # Aggregate TF-IDF score across all docs
    term_scores = defaultdict(float)

    for doc_tf in tf_docs:
        total_terms = sum(doc_tf.values()) or 1
        for term, count in doc_tf.items():
            tf = count / total_terms
            idf = math.log(N / (1 + df[term]))
            term_scores[term] += tf * idf

    # Bigrams
    for doc_bg_tf in bigram_tf:
        total = sum(doc_bg_tf.values()) or 1
        for term, count in doc_bg_tf.items():
            tf = count / total
            idf = math.log(N / (1 + bigram_df[term]))
            term_scores[term] += tf * idf * 1.5  # boost bigrams

    # Total frequency across all docs
    total_freq = Counter()
    for doc_tf in tf_docs:
        total_freq.update(doc_tf)

    # Sort by score
    results = []
    for term, score in sorted(term_scores.items(), key=lambda x: -x[1]):
        if score > 0.001 and total_freq[term] >= 2:
            display_term = term.replace("_", " ")
            results.append({
                "term": display_term,
                "score": round(score, 4),
                "frequency": total_freq[term],
            })
    return results

# ── Entity extraction ─────────────────────────────────────────────────────────
def extract_entities(docs_text, headings_list):
    """
    Heuristic entity extraction:
    - Capitalized phrases from body text (proper nouns)
    - Recurring technical brand names
    - Frequently cited tools, platforms, companies
    """
    combined_text = " ".join(docs_text)
    combined_headings = " ".join(h for hs in headings_list for h in hs)

    # Find capitalized phrases (2-3 words starting with capitals)
    cap_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b', combined_text)
    phrase_counter = Counter(cap_phrases)

    # Remove single common words that got capitalized (sentence starts)
    common_caps = {"The", "A", "An", "In", "If", "When", "How", "What",
                   "Why", "For", "You", "We", "Your", "Our", "This", "That",
                   "These", "Those", "It", "There", "Here", "As", "But",
                   "And", "Or", "To", "From", "With", "By", "At", "On",
                   "Of", "So", "Do", "Be", "Is", "Are", "Was", "Were",
                   "Has", "Have", "Had", "Can", "Will", "Would", "Should"}
    phrase_counter = Counter({p: c for p, c in phrase_counter.items()
                              if p not in common_caps and c >= 2})

    # Known tech entities to look for (web design industry)
    KNOWN_ENTITIES = [
        "WordPress", "Webflow", "Wix", "Squarespace", "Shopify", "WooCommerce",
        "Framer", "Elementor", "Divi", "Gutenberg", "HubSpot", "Salesforce",
        "Google Analytics", "Google Search Console", "Core Web Vitals",
        "PageSpeed Insights", "GTmetrix", "Lighthouse", "Cloudflare",
        "Schema.org", "JSON-LD", "Open Graph", "Google Business Profile",
        "Google Tag Manager", "Hotjar", "Crazy Egg", "Semrush", "Ahrefs",
        "Moz", "Search Console", "Google Ads", "Facebook Ads",
        "ChatGPT", "Perplexity", "Claude", "Bard", "Gemini", "Bing",
        "IndexNow", "Vercel", "Netlify", "AWS", "WP Engine",
        "Yoast SEO", "RankMath", "All in One SEO",
    ]
    entity_hits = {}
    for entity in KNOWN_ENTITIES:
        count = combined_text.count(entity) + combined_headings.count(entity)
        if count >= 1:
            entity_hits[entity] = count

    # Merge phrase_counter + entity_hits
    all_entities = {}
    for entity, count in entity_hits.items():
        all_entities[entity] = count
    for phrase, count in phrase_counter.most_common(40):
        if phrase not in all_entities and len(phrase.split()) >= 2:
            all_entities[phrase] = count

    # Sort by frequency
    sorted_entities = sorted(all_entities.items(), key=lambda x: -x[1])
    return [{"entity": e, "frequency": c} for e, c in sorted_entities[:25]]

# ── Content gap analysis from headings ───────────────────────────────────────
def content_gap(headings_list):
    N = len(headings_list)
    heading_freq = Counter()
    for headings in headings_list:
        seen = set()
        for h in headings:
            normalized = h.lower().strip()
            if normalized not in seen:
                heading_freq[normalized] += 1
                seen.add(normalized)

    table_stakes = []
    partial_gaps = []
    full_gaps = []

    for heading, count in heading_freq.most_common(60):
        entry = {"heading": heading, "competitor_count": count, "of_total": N}
        ratio = count / N if N else 0
        if ratio >= 0.6:
            table_stakes.append(entry)
        elif ratio >= 0.2:
            partial_gaps.append(entry)
        else:
            full_gaps.append(entry)

    return {
        "table_stakes": table_stakes[:15],
        "partial_gaps": partial_gaps[:15],
        "full_gaps": full_gaps[:10],
    }

# ── Fetch a single URL ────────────────────────────────────────────────────────
def fetch_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; DesigXnerBot/1.0; research)",
            "Accept": "text/html,application/xhtml+xml",
        }
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if r.status_code == 200:
            return extract_text(r.text, url)
    except Exception as e:
        print(f"  SKIP {url}: {e}", file=sys.stderr)
    return None

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    urls = []

    if "--file" in args:
        idx = args.index("--file")
        file_path = args[idx + 1] if idx + 1 < len(args) else None
        if file_path:
            with open(file_path) as f:
                urls = [line.strip() for line in f if line.strip()]
    else:
        urls = [a for a in args if a.startswith("http")]

    if not urls:
        print(json.dumps({"error": "No URLs provided. Usage: tfidf.py URL1 URL2 ..."}))
        sys.exit(1)

    print(f"Fetching {len(urls)} URLs...", file=sys.stderr)
    docs = []
    for url in urls:
        doc = fetch_url(url)
        if doc:
            docs.append(doc)
            print(f"  OK {doc['word_count']}w — {url}", file=sys.stderr)

    if not docs:
        print(json.dumps({"error": "All URLs failed to fetch"}))
        sys.exit(1)

    print(f"Computing TF-IDF on {len(docs)} documents...", file=sys.stderr)
    texts = [d["text"] for d in docs]
    headings_list = [d["headings"] for d in docs]

    top_terms = compute_tfidf(texts)[:30]
    entities = extract_entities(texts, headings_list)
    gaps = content_gap(headings_list)

    result = {
        "documents_analyzed": len(docs),
        "competitor_urls": [d["url"] for d in docs],
        "competitor_word_counts": {d["url"]: d["word_count"] for d in docs},
        "avg_competitor_word_count": int(sum(d["word_count"] for d in docs) / len(docs)),
        "top_terms": top_terms,
        "entities": entities,
        "content_gaps": gaps,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
