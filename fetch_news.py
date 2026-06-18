#!/usr/bin/env python3
"""Pull real, dated, attributed headlines per stock from Google News RSS (free).

We store only headline + source + date + link (never article bodies) and the app
links out — the license-safe pattern. Writes data/news.json:
  { "RELIANCE": [{"t":"...","src":"...","date":"YYYY-MM-DD","url":"..."}], ... }

Run:  python3 fetch_news.py
"""
import urllib.request, urllib.parse, json, os, re
import xml.etree.ElementTree as ET
from datetime import datetime

NAMES = {
    "RELIANCE":"Reliance Industries", "TCS":"Tata Consultancy Services",
    "INFY":"Infosys", "HDFCBANK":"HDFC Bank", "ITC":"ITC Ltd",
    "SUNPHARMA":"Sun Pharma", "BAJFINANCE":"Bajaj Finance",
    "ADANIGREEN":"Adani Green Energy", "TATAPOWER":"Tata Power",
    "ONGC":"ONGC", "HINDUNILVR":"Hindustan Unilever",
    "MARUTI":"Maruti Suzuki", "DMART":"Avenue Supermarts DMart",
    "COALINDIA":"Coal India",
}
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def rss_url(name):
    q = urllib.parse.quote(f'"{name}" stock')
    return f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"

def fetch(sym, name, limit=4):
    try:
        req = urllib.request.Request(rss_url(name), headers=UA)
        xml = urllib.request.urlopen(req, timeout=20).read()
        root = ET.fromstring(xml)
        items = []
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            pub = (it.findtext("pubDate") or "").strip()
            src_el = it.find("source")
            src = (src_el.text.strip() if src_el is not None and src_el.text else "")
            # Google News titles are "Headline - Source" — strip the trailing source
            if src and title.endswith(" - " + src):
                title = title[: -(len(src) + 3)]
            date = ""
            try:
                date = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
            except ValueError:
                date = pub[:16]
            if title:
                items.append({"t": title, "src": src, "date": date, "url": link})
            if len(items) >= limit:
                break
        return items
    except Exception as e:
        print(f"  ! {sym}: {type(e).__name__}")
        return []

def main():
    out = {}
    for sym, name in NAMES.items():
        out[sym] = fetch(sym, name)
        print(f"  {sym:12s} {len(out[sym])} headlines")
    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w") as f:
        json.dump({"fetched": datetime.now().strftime("%Y-%m-%d"), "news": out}, f, indent=1)
    print(f"Wrote data/news.json.")

if __name__ == "__main__":
    main()
