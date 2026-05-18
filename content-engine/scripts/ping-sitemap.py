#!/usr/bin/env python3
"""
Pings Google and IndexNow after publishing new content.
Usage: python scripts/ping-sitemap.py
Reads SITE_URL, SITEMAP_URL, INDEXNOW_KEY from .env
"""

import os, sys, json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, quote_plus

try:
    import requests
except ImportError:
    sys.exit("ERROR: Install 'requests'.")

ROOT = Path(__file__).parent.parent
ENV_FILE = ROOT / ".env"
LOG_FILE = ROOT / "sitemap-ping-log.txt"

def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

SITE_URL    = os.environ.get("SITE_URL", "https://desigxner.com").rstrip("/")
SITEMAP_URL = os.environ.get("SITEMAP_URL", f"{SITE_URL}/sitemap.xml")
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "").strip()

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def ping_google():
    url = f"https://www.google.com/ping?sitemap={quote_plus(SITEMAP_URL)}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            log(f"Google ping OK — {SITEMAP_URL}")
            return True
        else:
            log(f"Google ping HTTP {r.status_code} — {SITEMAP_URL}")
    except Exception as e:
        log(f"Google ping FAILED: {e}")
    return False

def ping_indexnow(urls_to_submit=None):
    if not INDEXNOW_KEY:
        log("IndexNow skipped — no INDEXNOW_KEY in .env")
        return False

    host = SITE_URL.replace("https://", "").replace("http://", "")

    if urls_to_submit:
        payload = {
            "host": host,
            "key": INDEXNOW_KEY,
            "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt",
            "urlList": urls_to_submit
        }
        endpoint = "https://api.indexnow.org/IndexNow"
        try:
            r = requests.post(endpoint, json=payload, timeout=15)
            if r.status_code in (200, 202):
                log(f"IndexNow batch OK — {len(urls_to_submit)} URLs submitted")
                return True
            else:
                log(f"IndexNow HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            log(f"IndexNow FAILED: {e}")
    else:
        url = f"https://api.indexnow.org/indexnow?url={quote_plus(SITE_URL)}&key={INDEXNOW_KEY}"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code in (200, 202):
                log(f"IndexNow ping OK")
                return True
            else:
                log(f"IndexNow HTTP {r.status_code}")
        except Exception as e:
            log(f"IndexNow FAILED: {e}")
    return False

def ping_bing():
    bing_url = f"https://www.bing.com/ping?sitemap={quote_plus(SITEMAP_URL)}"
    try:
        r = requests.get(bing_url, timeout=15)
        if r.status_code == 200:
            log(f"Bing ping OK — {SITEMAP_URL}")
            return True
        else:
            log(f"Bing ping HTTP {r.status_code}")
    except Exception as e:
        log(f"Bing ping FAILED: {e}")
    return False

def main():
    log("=== Sitemap Submission ===")
    log(f"Site: {SITE_URL}")
    log(f"Sitemap: {SITEMAP_URL}")

    google_ok = ping_google()
    bing_ok = ping_bing()
    indexnow_ok = ping_indexnow()

    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sitemap_url": SITEMAP_URL,
        "google": "OK" if google_ok else "FAILED",
        "bing": "OK" if bing_ok else "FAILED",
        "indexnow": "OK" if indexnow_ok else "SKIPPED" if not INDEXNOW_KEY else "FAILED",
    }
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
