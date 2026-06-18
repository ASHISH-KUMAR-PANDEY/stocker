# Broker integration — Connect → confirm in your broker → done

The "Connect broker → invest → done" flow is **real**, implemented against
**Zerodha Kite Connect**. It runs in two modes:

- **DEMO mode (default, no keys):** the whole flow works end-to-end with
  simulated connect + simulated orders. No login, no money. Order ids look like
  `DEMO-ITC`. This is what runs in the prototype today.
- **REAL mode (your keys):** the Connect button redirects to the actual Zerodha
  login; a confirmed order **places a real trade in the user's own account with
  real money.** Stocker never holds funds — the user's own broker executes and
  custodies everything.

## Architecture (why there's a backend now)

A pure static file can't do this safely: the Kite **API secret** and the
login-token exchange must stay **server-side**. So:

- `server.py` — tiny Flask backend. Serves the app + exposes `/api/*`
  (`status`, `connect`, `callback`, `order`, `holdings`, `disconnect`).
- `index.html` — the front-end calls those endpoints (connect, then one
  `POST /api/order` per basket stock, qty 1 — whole shares, since India has no
  fractional shares).

Money flow stays: **user's bank → user's broker → the stock.** It never touches
Stocker.

## Run

```bash
cd stock-match
python3 -m pip install -r requirements.txt   # Flask
python3 server.py                            # DEMO mode → http://127.0.0.1:4173
```

## Switch to REAL Zerodha

1. Create a **Kite Connect app** at https://developers.kite.trade (you need a
   Zerodha account). Note the **API key** and **API secret**.
   *(Order/account APIs are free since Mar 2025; live market data is the only paid add-on and isn't needed here.)*
2. Set the app's **Redirect URL** to: `http://127.0.0.1:4173/api/callback`
3. Start the backend with your keys:
   ```bash
   KITE_API_KEY=your_key KITE_API_SECRET=your_secret python3 server.py
   ```
   The banner prints `REAL — Kite connected`.
4. In the app: **Connect → Zerodha** now opens the real Zerodha login. After you
   authorize, you're redirected back connected. **Confirm invest places real
   orders** in your own account.

## ⚠️ Real orders spend real money

In REAL mode a confirmed basket buys **one whole share of each constituent at
market price** in the connected account. Test with the smallest/cheapest names
(or a single low-cost ETF) first. The swipe never buys — only the explicit
invest-confirm does, and every order is authorized by your own broker login.

## Safety & order features (built)

- **Cost + funds guard** — before placing real orders, the app calls `/api/preview`
  (live LTP per stock + your equity funds) and shows *"Spend ₹X? Available ₹Y."*
  It **blocks** if the basket exceeds your funds **or** the safety cap.
- **Order-value cap** — `MAX_ORDER_VALUE` (default **₹5000**) blocks any single order
  above it, both in the UI and server-side, so a stray tap can't buy a ₹13k share.
  Raise it for real use: `MAX_ORDER_VALUE=20000 ... python3 server.py`.
- **AMO fallback** — if the market is closed, the order is automatically re-placed as
  an **After-Market Order** (executes at next open) instead of failing.
- **Live order status** — `/api/orders` returns the real order book (COMPLETE / OPEN /
  REJECTED); the Done screen shows the status of what you placed.

## Single-account testing vs multi-user launch (important)

A self-serve Kite Connect app — **Personal or Connect** — is enabled for **one
account only** (the one whose Client ID created it). You must log in with **that same
account**. This is fine for **testing with your own account**, but it is **not** how you
let the public use Stocker.

**For a published, multi-user product** (each user connects *their own* broker), use
**[smallcase Gateway](https://gateway.smallcase.com/)** — one integration, many brokers
(Zerodha, Upstox, Angel…), purpose-built for multi-user order routing with no custody.
The code shape here (connect → order → done) carries over; you swap the raw-Kite calls
for Gateway's SDK and key the session **per user** (this prototype keeps one global
session). Gateway is an onboarding/approval-gated commercial product — verify fit &
pricing with them directly.

## Not yet wired (next steps)

- Per-order confirmation *screen* inside Zerodha (Kite **Publisher/basket** flow)
  if you want the user to approve each order on Zerodha's UI rather than via the
  API session.
- Multi-broker (Upstox/Angel/etc.) — add via **smallcase Gateway** (one
  integration, many brokers). Today only Zerodha is real; other broker tiles use
  the demo path.
- Reading real holdings into the Portfolio (`/api/holdings` is implemented;
  the UI still shows the simulated paper portfolio).
- True ₹100 recurring SIPs → mutual-fund rail (BSE StAR MF), a separate setup.
