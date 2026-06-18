# Stocker — "Dating, but for stocks" 🔥📈

Swipe through stocks like a dating app. Stocker learns your **investing type** from a
quick quiz + your swipes, serves a personalized deck, and lets you build a paper
portfolio — then (optionally) place **real orders through your own broker**, with
**Stocker never touching your money.**

> **Education & discovery only — not investment advice.** Self-hosted: you run your
> own copy, you connect your own broker, you hold your own keys. See [disclaimer](#disclaimer).

*(Add a screenshot here: `docs/screenshot.png`)*

---

## What it does

- **Swipe to discover** — right = like, left = pass, ★ = watch. A personalized deck.
- **"Your-type score"** — a transparent, rules-based *similarity* score (not a buy
  rating). Shows *why* a stock matches your taste.
- **Real NSE data (free)** — live end-of-day prices, 90-day charts, computed
  volatility/momentum, and real news headlines (NSE Bhavcopy + Google News).
- **Paper portfolio** — matches become a tracked practice portfolio with P&L, an
  allocation donut, cash, buy/sell — all play money by default.
- **Optional real investing** — connect *your own* Zerodha (Kite Connect) and place a
  real, diversified basket order. The swipe never buys; investing is a separate,
  deliberate step with a cost/funds guard.
- **Your data persists** locally (browser) across reloads. Reset wipes it.

## Quickstart (safe demo — no keys, no money)

```bash
git clone https://github.com/ASHISH-KUMAR-PANDEY/stocker.git
cd stocker
python3 -m pip install -r requirements.txt
python3 server.py     # → http://127.0.0.1:4173
```
Open **http://127.0.0.1:4173** and play. Everything works; the broker/orders are
simulated. To refresh the market data: `python3 fetch_bhavcopy.py && python3 fetch_history.py && python3 fetch_news.py`.

## Real trading (optional — your own broker)

Stocker uses **bring-your-own-broker**: you create your *own* free Kite Connect app,
run Stocker with your keys, and orders route through *your* Zerodha account. Stocker
never holds your money or your login. Full steps in **[INTEGRATION.md](INTEGRATION.md)**.

```bash
cp .env.example .env   # add your KITE_API_KEY / KITE_API_SECRET
KITE_API_KEY=... KITE_API_SECRET=... python3 server.py
```

⚠️ In real mode, a confirmed order **buys real shares with real money**. There's a
₹5,000 safety cap by default (`MAX_ORDER_VALUE`). Test with one cheap stock first.

## Deploy a public demo

See **[DEPLOY.md](DEPLOY.md)** — deploy the demo (no keys → no money) to a domain so
others can try it.

## How it works

- **One Flask app** ([server.py](server.py)) serves the UI ([index.html](index.html))
  *and* a small API (`/api/connect`, `/api/order`, `/api/preview`, `/api/orders`…).
- **Two data engines:** *delayed/EOD data* powers Discovery for everyone; your *own
  broker* powers real Invest/Portfolio for you. (Details in [PRODUCT_SCOPE.md](PRODUCT_SCOPE.md) §2.5.)
- No database — single self-hosted user; state persists in the browser.

## Docs

- [CONCEPT.md](CONCEPT.md) — the vision & product thinking
- [PRODUCT_SCOPE.md](PRODUCT_SCOPE.md) — full feature scope & architecture
- [INTEGRATION.md](INTEGRATION.md) — connect your Zerodha for real trading
- [DEPLOY.md](DEPLOY.md) — host a public demo

## Honest limitations

- A self-serve Kite app is **single-account** — only *your* Zerodha can trade through
  your copy. True multi-user investing needs [smallcase Gateway](https://gateway.smallcase.com/) (a separate project).
- **No fractional shares in India** — the smallest real buy is one whole share (use
  low-cost ETFs for small tickets).
- Company info (sector, bios, "flags") is **curated/illustrative**; prices, charts,
  volatility, momentum and news are real.

## Disclaimer

Stocker is an **educational, self-hosted** project. It is **not investment advice**,
not a brokerage, and does not hold your money or securities. You run it yourself and
are solely responsible for your own trades and any losses. Provided "as is", no
warranty. Comply with your broker's terms and local regulations.
