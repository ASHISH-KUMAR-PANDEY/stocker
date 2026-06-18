# Stocker — "Dating, but for stocks"

*Concept v0.2 — working draft*

**Locked decisions:**
1. Positioning is **education & discovery only** — never "buy this."
2. v1 is **market-agnostic** — prototype with sample data.
3. **Paper-only**, no real money in v1 (follows from education-only positioning).
4. **Solo discovery** — no social/following in v1.
5. Name: **Stocker** (placeholder, kept for now).

**Still open:** US vs NSE/BSE — deferred until real data integration; prototype
runs on sample data until then.

## One-liner
A swipe-first discovery app that learns your investing "type" and serves you a
daily deck of stocks to swipe on. Swipe right to add to your watchlist; the more
you swipe, the better it understands what you actually like — turning research
from a chore into a habit.

## The problem
Picking stocks is intimidating. Beginners face a wall of tickers, charts, and
jargon and bounce. Existing apps (brokerages, screeners) are built for people who
*already know what they want*. There's no fun, low-pressure way to **discover**
stocks that fit you and gradually build conviction.

## The insight (why the dating metaphor works)
Dating apps solved "too many options, don't know my type" with a simple loop:
show one profile, swipe, learn preferences, improve matches. Stock discovery has
the same shape — overwhelming choice, fuzzy personal taste, and a need to learn
over time. The swipe is a low-commitment way to express preference *before*
money is on the line.

## Target user
- **Primary:** curious first-time / early investors (early 20s–30s) who find
  brokerages intimidating and want to learn by browsing, not by reading 10-Ks.
- **Secondary:** experienced retail investors who want a fast, fun discovery
  feed for ideas outside their usual names.

## Core loop
1. **Onboard** → quick quiz sets your profile: risk appetite, time horizon,
   values (e.g. clean energy, no tobacco), sectors you like, ticket size.
2. **Daily deck** → a curated stack of ~15–25 stock "cards."
3. **Swipe** → right = like (→ watchlist), left = pass, up = "super-like /
   deep dive," tap = expand the card.
4. **Learn** → every swipe tunes your taste model; tomorrow's deck improves.
5. **Match moments** → "It's a match!" when a liked stock also scores high on
   your profile fit — nudges you toward a deeper look or a paper trade.
6. **Portfolio** → watchlist + optional paper-trading portfolio to track how
   your "matches" would have performed.

## The stock "card" (the profile)
Designed to be glanceable, like a dating profile — personality first, depth on tap.
- **Hero:** ticker, company name, logo, one-line "bio" (what they do, in plain English).
- **Vital stats:** price, today's move, market cap, sector, a simple sparkline.
- **"Green/red flags":** 2–3 auto-generated plain-language pros and cons
  (e.g. "🟢 Profitable & growing revenue" / "🔴 Pricey vs. peers").
- **Fit score:** how well it matches *your* profile (0–100), with a one-line why.
- **Deep dive (on tap):** fuller chart, key metrics, news headlines, "people with
  your taste also liked…".

## What makes it differentiated
- **Taste model, not a screener.** It learns implicitly from swipes, not just the
  intake quiz. Two users with the same risk profile get different decks.
- **Plain-language flags.** No jargon walls; every number is translated.
- **Discovery, not transactions.** It's the top of the funnel — the fun part —
  and can hand off to a real broker for execution rather than being one.

## Monetization (options, not commitments)
- **Freemium:** free daily deck; premium unlocks unlimited swipes, advanced
  filters, richer analytics, alerts.
- **Affiliate/referral:** "Open with [broker]" handoff for actual trades.
- **Data-light B2B (later):** anonymized taste/sentiment trends.
- **Explicitly NOT** payment-for-order-flow or pushing trades — keeps incentives
  aligned with the "discovery, not churn" positioning.

## MVP scope (smallest thing worth shipping)
- Onboarding quiz → profile.
- Swipe deck over a fixed universe (e.g. S&P 500 + popular tickers).
- Card with bio, vitals, sparkline, 2–3 flags, fit score.
- Watchlist of right-swipes.
- A simple, transparent fit-score + ranking (rules-based first, ML later).
- **Out of scope for MVP:** real-money trading, social/following, news feed,
  options/crypto.

## Data & tech (sketch)
- **Market data:** start with a free/cheap API (e.g. delayed quotes + fundamentals)
  for the MVP; upgrade to real-time later. Delayed data is fine for discovery.
- **Fit score v1:** transparent rules over fundamentals + your profile weights.
- **Taste model v2:** lightweight recommender (collaborative + content-based)
  trained on swipe history.
- **Stack:** mobile-first (web prototype first to validate the feel).

## Risks & the regulation question (important, since direction is TBD)
- **If it ever touches recommendations or real money in the US/India, it likely
  triggers regulation** (SEBI / SEC / "investment adviser" rules). The safe early
  framing is **education & discovery, not advice** — show information and *fit*,
  avoid "you should buy this." This single choice shapes the whole product, so
  decide it early.
- **Gamification risk:** swiping can encourage impulsive behavior. Counter with
  friction before money moves (paper trade first, "matches" ≠ "buy now").
- **Data costs:** real-time market data licensing gets expensive at scale.

## Open questions (to decide next)
1. **Geography:** US stocks or Indian (NSE/BSE) market first? *(Deferred — prototype
   is market-agnostic with sample data; decide before real data integration. This is
   now the one remaining strategic fork.)*

*Resolved in v0.2:* paper-only (no real money), solo discovery (no social), name
stays "Stocker" for now.

---

# Refinements (v0.2)

## Positioning guardrails: education, not advice
This is the spine of the product, so here's what "education only" concretely means
in the UI — these are design rules, not just a legal posture:
- **No imperatives.** Never "Buy", "Sell", "You should". The fit score answers
  *"how much is this like what you've liked?"* — a similarity/taste signal, **not**
  *"is this a good investment?"*
- **Reframe the score's label.** Call it a **"Match score"** or **"Your-type score,"**
  never a "rating" or "recommendation." Always paired with a plain-language *why*.
- **No performance promises.** Show what *happened* (history), never project returns.
- **Friction before money.** Right-swipe = watchlist only. Any path to real trading
  is an explicit handoff to a licensed broker, clearly outside our walls.
- **Standard disclaimers** + "not investment advice" framing throughout.
- **Litmus test for any feature:** *Would a regulator read this as steering a
  specific person toward a specific trade?* If yes, cut or reframe it.

## How the "Match score" actually works (v1, transparent + rules-based)
Deliberately simple and explainable for v1 — no black box, which also keeps us on
the right side of the advice line (it's clearly *taste similarity*, not a verdict).

1. **Profile vector** from onboarding: risk (1–5), horizon (short/long), sector
   likes/dislikes, values screens (e.g. exclude tobacco/fossil), volatility tolerance.
2. **Stock attribute vector** per ticker: sector, size bucket, volatility band,
   valuation band, profitability flag, dividend flag, momentum band.
3. **Score = weighted overlap** between the two vectors, 0–100. Hard *exclusions*
   (values screens) drop a stock out entirely rather than just lowering its score.
4. **The "why" line** is generated from the top 1–2 matching attributes
   (e.g. "Matches your taste for steady, profitable large-caps").
- v2 layers a **learned taste model** on top (see below), but the rules-based core
  stays as the explainable fallback.

## The taste model & the cold-start problem
- **Cold start (day 1):** rely on the onboarding quiz + rules-based score so the
  very first deck is already personalized — don't make users swipe 50 times to get
  value.
- **Implicit learning:** each swipe is a labeled example (right/up = positive,
  left = negative, plus dwell time and deep-dive taps as weak signals).
- **What it learns:** attribute weights drift toward what the user *actually*
  swipes right on, which may diverge from what they *said* in the quiz — that gap is
  the magic ("you say low-risk but you keep liking high-growth tech").
- **Content-based first, collaborative later:** start by learning per-user attribute
  weights (works with zero other users); add "people with your taste also liked…"
  once there's a user base.
- **Anti-filter-bubble:** inject a small % of "wildcard" cards so the deck doesn't
  collapse to one sector — both for discovery quality and to avoid over-narrowing.

## Anti-gamification design (taking the dark side seriously)
The swipe loop is engaging *by design*, which is exactly the risk with money.
Counter-measures baked in from v1:
- Right-swipe never buys anything — it's a watchlist, full stop.
- **Paper-trading first** as the default way to "act on" a match.
- No streaks/pressure mechanics that reward frequency of *trading*; reward
  *learning* instead (e.g. "you understood 5 new concepts this week").
- Surface holding-period and volatility context so swiping doesn't read as day-trading.

## Competitive landscape (rough)
- **Brokerages (Robinhood, Zerodha/Groww):** great at execution, weak at fun
  discovery for novices. We're the top-of-funnel they don't own.
- **Screeners (Finviz, Tickertape):** powerful but built for people who already
  know what to filter for. We replace "configure 12 filters" with "swipe."
- **Robo-advisors:** give you a portfolio but no agency or learning. We keep the
  user in the driver's seat and teach taste.
- **The gap we fill:** *playful, personalized discovery that builds conviction* —
  nobody owns the "learn what you like, before you buy" moment.

## Suggested next steps
- Pick answers to the open questions above (esp. geography + education/advice).
- Build a **clickable web prototype** of the swipe deck to feel the core loop.
- Validate the "fit score" framing with a handful of target users.
