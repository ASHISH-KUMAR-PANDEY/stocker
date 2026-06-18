#!/usr/bin/env python3
"""Fetch NSE end-of-day Bhavcopy and write data/quotes.json for the app.

Discover runs on this delayed/EOD feed (the "shared engine"). NSE publishes the
Bhavcopy free each trading day; this pulls the latest available, extracts our
universe's close + previous close (-> day %), and writes a small JSON the app
overlays onto the curated stock cards.

Run:  python3 fetch_bhavcopy.py
Output: data/quotes.json  { "date": "...", "quotes": { "RELIANCE": {price, chg, vol}, ... } }
"""
import urllib.request, io, zipfile, csv, json, os
from datetime import date, timedelta

UNIVERSE = ["RELIANCE","TCS","INFY","HDFCBANK","ITC","SUNPHARMA","BAJFINANCE",
            "ADANIGREEN","TATAPOWER","ONGC","HINDUNILVR","MARUTI","DMART","COALINDIA"]

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "*/*", "Referer": "https://www.nseindia.com/"}

def url_for(d):
    return ("https://nsearchives.nseindia.com/content/cm/"
            f"BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip")

def fetch_latest(max_back=8):
    d = date.today()
    for _ in range(max_back):
        try:
            req = urllib.request.Request(url_for(d), headers=UA)
            data = urllib.request.urlopen(req, timeout=25).read()
            z = zipfile.ZipFile(io.BytesIO(data))
            rows = list(csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), "utf-8")))
            return d, rows
        except Exception:
            d -= timedelta(days=1)
    raise SystemExit("Could not fetch a Bhavcopy in the last %d days." % max_back)

def main():
    d, rows = fetch_latest()
    want = set(UNIVERSE)
    quotes = {}
    for r in rows:
        if r.get("SctySrs") == "EQ" and r.get("TckrSymb") in want:
            try:
                close = float(r["ClsPric"]); prev = float(r["PrvsClsgPric"])
                chg = round((close - prev) / prev * 100, 2) if prev else 0.0
                quotes[r["TckrSymb"]] = {"price": round(close, 2), "chg": chg,
                                         "vol": int(float(r.get("TtlTradgVol") or 0))}
            except (ValueError, KeyError):
                pass
    out = {"date": d.isoformat(), "source": "NSE Bhavcopy (EOD)", "quotes": quotes}
    os.makedirs("data", exist_ok=True)
    with open("data/quotes.json", "w") as f:
        json.dump(out, f, indent=2)
    missing = want - set(quotes)
    print(f"Wrote data/quotes.json — {len(quotes)} symbols, EOD {d.isoformat()}.")
    if missing:
        print("  (not found in bhavcopy:", ", ".join(sorted(missing)), ")")

if __name__ == "__main__":
    main()
