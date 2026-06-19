#!/usr/bin/env python3
"""Stocker backend — real Zerodha Kite Connect 'connect → order → done', with
a demo fallback so the flow runs end-to-end without credentials or real money.

WHY a backend: Kite's API secret and the login-token exchange MUST stay
server-side (never in the browser). This serves the static app AND exposes a few
/api/* endpoints the front-end calls.

REAL mode: set KITE_API_KEY + KITE_API_SECRET (from your Kite Connect app) as env
vars and restart. The Connect button then redirects to the real Zerodha login,
and a confirmed order places a REAL trade in the user's own account.
DEMO mode (no keys): everything is simulated — no login, no money, demo order ids.

Run:  KITE_API_KEY=xxx KITE_API_SECRET=yyy python3 server.py    (real)
      python3 server.py                                          (demo)
Kite app redirect URL must be set to:  http://127.0.0.1:4173/api/callback
"""
import os, json, hashlib, urllib.request, urllib.parse, urllib.error
from flask import Flask, request, redirect, jsonify, send_from_directory

API_KEY = os.environ.get("KITE_API_KEY", "")
API_SECRET = os.environ.get("KITE_API_SECRET", "")
DEMO = not (API_KEY and API_SECRET)
KITE = "https://api.kite.trade"
PORT = int(os.environ.get("PORT", "4173"))
MAX_ORDER_VALUE = float(os.environ.get("MAX_ORDER_VALUE", "5000"))  # ₹ safety cap per order/basket
BASE = os.path.dirname(os.path.abspath(__file__))  # serve files relative to this file (works on Vercel too)

app = Flask(__name__)
# single-user prototype session (a real app keys this per-user)
STATE = {"access_token": None, "user": None}

def kite_post(path, token, data):
    body = urllib.parse.urlencode(data).encode()
    headers = {"X-Kite-Version": "3"}
    if token:
        headers["Authorization"] = f"token {API_KEY}:{token}"
    req = urllib.request.Request(KITE + path, data=body, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=20))

def kite_get(path, token):
    req = urllib.request.Request(KITE + path, headers={
        "X-Kite-Version": "3", "Authorization": f"token {API_KEY}:{token}"})
    return json.load(urllib.request.urlopen(req, timeout=20))

# ---- static app ----
@app.route("/")
def root():
    return send_from_directory(BASE, "index.html")

@app.route("/data/<path:p>")
def data_files(p):
    return send_from_directory(os.path.join(BASE, "data"), p)

# ---- api ----
@app.route("/api/status")
def status():
    return jsonify(demo=DEMO,
                   connected=bool(STATE["access_token"]),
                   broker="zerodha",
                   user=STATE["user"])

@app.route("/api/connect")
def connect():
    if DEMO:
        return jsonify(demo=True)
    return jsonify(login_url=f"https://kite.zerodha.com/connect/login?api_key={API_KEY}&v=3")

@app.route("/api/demo-connect", methods=["POST"])
def demo_connect():
    STATE["access_token"], STATE["user"] = "DEMO", "Demo User"
    return jsonify(ok=True, demo=True, user=STATE["user"])

@app.route("/api/callback")
def callback():
    # Zerodha redirects here after login with ?request_token=...
    rt = request.args.get("request_token")
    if not rt:
        return "Missing request_token", 400
    checksum = hashlib.sha256((API_KEY + rt + API_SECRET).encode()).hexdigest()
    try:
        out = kite_post("/session/token", None,
                        {"api_key": API_KEY, "request_token": rt, "checksum": checksum})
        STATE["access_token"] = out["data"]["access_token"]
        STATE["user"] = out["data"].get("user_name", "Investor")
        return redirect("/?connected=1")
    except urllib.error.HTTPError as e:
        return redirect("/?connect_error=1&msg=" + urllib.parse.quote(e.read().decode()[:200]))

@app.route("/api/disconnect", methods=["POST"])
def disconnect():
    STATE["access_token"], STATE["user"] = None, None
    return jsonify(ok=True)

def _equity_cash():
    """Live equity funds available to trade (real mode only)."""
    try:
        return float(kite_get("/user/margins/equity", STATE["access_token"])["data"]["net"])
    except Exception:
        return None

def _ltps(syms):
    """{symbol: last_price} for NSE symbols via Kite quote/ltp."""
    qs = "&".join("i=" + urllib.parse.quote("NSE:" + s) for s in syms)
    data = kite_get("/quote/ltp?" + qs, STATE["access_token"])["data"]
    return {s: data.get("NSE:" + s, {}).get("last_price") for s in syms}

@app.route("/api/preview", methods=["POST"])
def preview():
    """Cost + funds preview before placing (one whole share per ticker)."""
    b = request.get_json(force=True, silent=True) or {}
    tickers = b.get("tickers", [])
    if DEMO or STATE["access_token"] == "DEMO":   # demo is stateless (works on serverless)
        return jsonify(demo=True, prices={t: None for t in tickers}, cash=None, cap=MAX_ORDER_VALUE)
    if STATE["access_token"] is None:
        return jsonify(error="not_connected"), 401
    try:
        prices = _ltps(tickers)
        return jsonify(prices=prices, cash=_equity_cash(), cap=MAX_ORDER_VALUE)
    except Exception as e:
        return jsonify(error=str(e)[:300]), 400

@app.route("/api/orders")
def orders():
    """Today's order book (status: COMPLETE / OPEN / REJECTED / ...)."""
    if DEMO or STATE["access_token"] == "DEMO":   # demo is stateless
        return jsonify(demo=True, orders=[])
    if STATE["access_token"] is None:
        return jsonify(error="not_connected"), 401
    try:
        rows = kite_get("/orders", STATE["access_token"])["data"]
        slim = [{"order_id": r.get("order_id"), "symbol": r.get("tradingsymbol"),
                 "status": r.get("status"), "qty": r.get("quantity"),
                 "price": r.get("price"), "variety": r.get("variety"),
                 "message": r.get("status_message")} for r in rows]
        return jsonify(orders=slim)
    except Exception as e:
        return jsonify(error=str(e)[:300]), 400

@app.route("/api/order", methods=["POST"])
def order():
    b = request.get_json(force=True, silent=True) or {}
    sym = b.get("symbol", "")
    qty = int(b.get("qty", 1))
    if DEMO or STATE["access_token"] == "DEMO":   # demo is stateless (works on serverless)
        return jsonify(demo=True, order_id="DEMO-" + sym, status="simulated", symbol=sym, qty=qty)
    if STATE["access_token"] is None:
        return jsonify(error="not_connected"), 401
    try:
        # Zerodha disallows bare MARKET orders via API → place a protected LIMIT.
        ltp = _ltps([sym])[sym]
        price = round(round(ltp * 1.005 / 0.05) * 0.05, 2)   # ~0.5% above LTP, tick-aligned
        value = price * qty
        if value > MAX_ORDER_VALUE:                          # server-side safety cap
            print(f"  ✗ order {sym} BLOCKED: ₹{value:.0f} > cap ₹{MAX_ORDER_VALUE:.0f}")
            return jsonify(error=f"Blocked — ₹{value:.0f} exceeds the ₹{MAX_ORDER_VALUE:.0f} safety cap.", symbol=sym, capped=True), 400

        def place(variety):
            return kite_post("/orders/" + variety, STATE["access_token"], {
                "exchange": "NSE", "tradingsymbol": sym, "transaction_type": "BUY",
                "quantity": qty, "product": "CNC", "order_type": "LIMIT", "price": price,
                "variety": variety})
        try:
            out = place("regular")
            print(f"  ✓ order {sym} placed (LIMIT ₹{price}): {out['data']['order_id']}")
            return jsonify(order_id=out["data"]["order_id"], symbol=sym, qty=qty, price=price)
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try: msg = json.loads(body).get("message", body)
            except Exception: msg = body
            # market closed → retry as an After-Market Order
            if "market" in msg.lower() and ("close" in msg.lower() or "not open" in msg.lower()):
                out = place("amo")
                print(f"  ✓ order {sym} placed as AMO (LIMIT ₹{price}): {out['data']['order_id']}")
                return jsonify(order_id=out["data"]["order_id"], symbol=sym, qty=qty, price=price, amo=True)
            print(f"  ✗ order {sym} REJECTED by Zerodha: {msg}")
            return jsonify(error=msg[:400], symbol=sym), 400
    except Exception as e:
        print(f"  ✗ order {sym} error: {e}")
        return jsonify(error=str(e)[:400], symbol=sym), 400

@app.route("/api/holdings")
def holdings():
    if DEMO or STATE["access_token"] == "DEMO":   # demo is stateless
        return jsonify(demo=True, holdings=[])
    if STATE["access_token"] is None:
        return jsonify(error="not_connected"), 401
    return jsonify(holdings=kite_get("/portfolio/holdings", STATE["access_token"])["data"])

if __name__ == "__main__":
    print(f"Stocker backend on :{PORT}  ({'DEMO — no keys' if DEMO else 'REAL — Kite connected'})")
    app.run(host="127.0.0.1", port=PORT)
