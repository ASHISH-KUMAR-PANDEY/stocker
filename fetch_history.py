#!/usr/bin/env python3
"""Stitch ~90 trading days of NSE Bhavcopy into a real price history + metrics.

Free, license-safe (same public EOD file as fetch_bhavcopy.py). Produces:
  data/history.json = {
     "from","to","days",
     "series":  { "RELIANCE": [c1..cN], ... },   # chronological closes
     "metrics": { "RELIANCE": {"vol":"low|medium|high","mom":"hot|steady|soft",
                               "ret":<90d % >}, ... }
  }
The app draws the real chart from `series` and the score reads real `vol`/`mom`
from `metrics` (volatility = stdev of daily returns; momentum = 90-day return),
banded into terciles across the universe so the bands are relative & stable.

Run:  python3 fetch_history.py   (slow first time — ~90 daily files)
"""
import urllib.request, io, zipfile, csv, json, os, time, statistics
from datetime import date, timedelta

UNIVERSE = ["RELIANCE","TCS","INFY","HDFCBANK","ITC","SUNPHARMA","BAJFINANCE",
            "ADANIGREEN","TATAPOWER","ONGC","HINDUNILVR","MARUTI","DMART","COALINDIA"]
TRADING_DAYS = 90
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "*/*", "Referer": "https://www.nseindia.com/"}

def url_for(d):
    return ("https://nsearchives.nseindia.com/content/cm/"
            f"BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip")

def closes_for(d):
    """Return {symbol: close} for one day, or None if no file (holiday/weekend)."""
    try:
        req = urllib.request.Request(url_for(d), headers=UA)
        data = urllib.request.urlopen(req, timeout=25).read()
        z = zipfile.ZipFile(io.BytesIO(data))
        out = {}
        for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), "utf-8")):
            if r.get("SctySrs") == "EQ" and r.get("TckrSymb") in set(UNIVERSE):
                try: out[r["TckrSymb"]] = float(r["ClsPric"])
                except (ValueError, KeyError): pass
        return out
    except Exception:
        return None

def main():
    series = {s: [] for s in UNIVERSE}
    dates = []
    d = date.today()
    tried = 0
    while len(dates) < TRADING_DAYS and tried < TRADING_DAYS * 2 + 30:
        tried += 1
        day = closes_for(d)
        if day:
            dates.append(d.isoformat())
            for s in UNIVERSE:
                series[s].append(day.get(s))
            time.sleep(0.15)  # be polite to NSE
        d -= timedelta(days=1)
    # we walked backwards; flip to chronological
    dates.reverse()
    for s in UNIVERSE:
        series[s].reverse()
        series[s] = [c for c in series[s] if c is not None]

    # ---- metrics ----
    raw = {}
    for s in UNIVERSE:
        cl = series[s]
        if len(cl) < 5:
            continue
        rets = [cl[i]/cl[i-1]-1 for i in range(1, len(cl)) if cl[i-1]]
        vol = statistics.pstdev(rets) if rets else 0
        ret = (cl[-1]/cl[0]-1) if cl[0] else 0
        raw[s] = {"vol": vol, "ret": ret}

    def band(values, labels):
        """Tercile-band a dict {sym:value} into labels[low,mid,high]."""
        order = sorted(values, key=lambda k: values[k])
        n = len(order); out = {}
        for i, k in enumerate(order):
            out[k] = labels[0] if i < n/3 else (labels[1] if i < 2*n/3 else labels[2])
        return out

    vol_band = band({s: raw[s]["vol"] for s in raw}, ["low", "medium", "high"])
    mom_band = band({s: raw[s]["ret"] for s in raw}, ["soft", "steady", "hot"])

    metrics = {s: {"vol": vol_band[s], "mom": mom_band[s],
                   "ret": round(raw[s]["ret"]*100, 1)} for s in raw}

    out = {"from": dates[0] if dates else None, "to": dates[-1] if dates else None,
           "days": len(dates), "series": {s: series[s] for s in UNIVERSE},
           "metrics": metrics}
    os.makedirs("data", exist_ok=True)
    with open("data/history.json", "w") as f:
        json.dump(out, f)
    print(f"Wrote data/history.json — {len(dates)} trading days "
          f"({dates[0] if dates else '?'} → {dates[-1] if dates else '?'}).")
    for s in UNIVERSE:
        m = metrics.get(s, {})
        print(f"  {s:12s} {len(series[s]):3d} pts  vol={m.get('vol','?'):6s} "
              f"mom={m.get('mom','?'):6s} 90d={m.get('ret','?')}%")

if __name__ == "__main__":
    main()
