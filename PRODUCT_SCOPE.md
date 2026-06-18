# Stocker — Full Product Scope (end-to-end)

*Scope v1 — the ideal experience, assuming the boring stuff (licensing, custody,
clearing, KYC) is handled by a partner and out of scope here. This doc is about
**how the product works and feels** when it's a real, ready-to-invest tool.*

Companion to [CONCEPT.md](CONCEPT.md). Where CONCEPT.md is the "why," this is the "what & how."

---

## 0. The promise in one line
**Discover stocks like you're swiping a feed, understand them in seconds, and
turn the ones that fit you into a real, diversified portfolio — without ever
feeling lost, lectured, or pressured.**

Three product principles, in priority order:
1. **The swipe is sacred — it's discovery, never a trade.** Money is always a
   separate, deliberate, calmer action. (This is both the ethic and the safety rail.)
2. **Fun rewards *learning and consistency*, never trading frequency.** Streaks,
   confetti, and recaps celebrate good habits, not churn.
3. **Every number is translated.** No jargon wall, ever. If we show it, we explain it.

---

## 1. End-to-end journey (the narrative)

**First 3 minutes (Activation).** Open → 30-sec taste quiz (risk, horizon,
sectors, values, goal) → instantly a personalized deck. Swipe ~15 cards, feel the
"your-type score" land, hit a couple of "It's a match!" moments. Land softly on a
**paper portfolio** seeded from the matches: "Here's what your taste looks like as
a portfolio — ₹0 real, all practice." Aha achieved before any money.

**First week (Habituation).** Daily deck refreshes. Price/news alerts on matches
pull the user back ("NOVA, your match, just popped 6% — here's why"). Paper P&L
gives a reason to check in. Bite-size "Learn" cards appear contextually. A
**weekly recap** ("Your week in matches") closes the loop. After a few sessions the
app surfaces the *insight*: "You say balanced, but you keep matching bold growth —
want to update your type?"

**Graduation (Conversion).** Once the user has run a paper portfolio for a bit and
opened N sessions, the **"Go live" toggle** unlocks. Fund the account, and the
**Invest** action becomes real: fund a **basket built from your matches**, on a
schedule, ETF-weighted by default. The swipe still just parks.

**Ongoing (Retention/Depth).** Recurring auto-invest runs quietly. Portfolio view
shows real holdings, P&L, taste drift, and "matches you haven't acted on." Themed
decks ("Dividend payers," "Clean energy," "This week's movers") keep discovery
fresh. Monthly "Wrapped"-style recap. Optional challenges and goals.

---

## 2. Modules / feature scope

### A. Onboarding & profiling
- **Taste quiz — 6 questions** *(built; revised per PM audit)*. Four required, two optional:
  1. **Goal** — "What brings you here?": Grow long-term / Income / Quick gains / Just learning. *(Anchors the vector + sets safe framing; "just learning" → no money nudges.)*
  2. **Risk** — true **5-point** scale: Very cautious / Cautious / Balanced / Adventurous / Bold. *(5 points, not 3 — so the middle option actually differentiates; see scoring.)*
  3. **Horizon** — "When might you want the money back?": Under 1 yr / 1–5 yrs / 5+ yrs. *(Time-to-need, not "how long would you hold" — clearer, less advice-y.)*
  4. **Style** — Growth / Income / Value / No preference. *(Replaces the old dividend Y/N; one question now drives dividend AND valuation tilt.)*
  5. **Sectors** *(optional, multi)* — tech / health / energy / finance / consumer / auto; no selection = broad market.
  6. **Values** *(optional)* — avoid (tobacco / fossil, **hard exclusion**) + lean toward (🌿 clean / sustainable, **soft signal**).
- **Editable anytime** *(built)*: the **You tab** shows "Your investing type" with an **Edit** button that reopens the quiz pre-filled; saving re-tunes the deck live.
- **Ticket size is asked later** — at the paper-portfolio / first-invest moment, not in the quiz, to protect the <60s cold start.
- Output: a **profile vector** `{goal, risk, horizon, style, sectors[], exclude[], lean[]}` that seeds the score on day one (no cold start).
- **Account creation is deferred** — swipe before signup; gate only paper-save / go-live behind an account.
- One-time explainers (the "your-type score" coach) introduced contextually, never a wall of text.

### A.1 The Match score — methodology *(built; rewritten per PM audit)*
Transparent, rules-based **normalized weighted overlap** (not additive bumps). Each
sub-score is 0–1; weights are explicit and a deliberate product lever:

| Dimension | Weight | How it scores |
|---|---|---|
| **Risk fit** | 0.30 | Banded tolerance vs the stock's volatility — *widest band at Balanced* so the middle works; unprofitable names penalized for cautious profiles |
| **Style fit** | 0.25 | Growth → non-dividend / momentum; Income → dividend payers; Value → cheap valuation; No-pref → neutral |
| **Sector fit** | 0.20 | In a picked sector = 1.0; not picked = 0.25; *no sectors chosen = neutral 0.5* (capped so it can't dominate) |
| **Horizon fit** | 0.15 | Long → steady & profitable; Short → momentum; decoupled from dividends (no double-count) |
| **Values lean** | 0.10 | Clean lean + clean stock = uplift; never penalizes if no lean |

`score = round(clamp(weightedSum × 100, 5, 98))` — natural 0–100 spread, clamp rarely fires.
- **Hard exclusions** (tobacco/fossil) drop a stock out entirely (not just lower it).
- **"Why" copy is similarity-framed, never suitability** — "Matches your type —
  volatility sits in your balanced range, and it's value-priced" — never "the
  dividend you want / suitable for you" (the education-only firewall).
- **One shared risk↔vol mapping** powers both the score and the You-tab
  stated-vs-revealed insight (no scale mismatch).
- **Wildcard slot**: `buildQueue` surfaces one low-fit name mid-deck (anti-filter-bubble).
- **v2 (not yet built):** revealed-taste learning — swipe behavior drifts the per-user
  weights over time; the rules-based core above stays as the explainable fallback.

### B. Discovery — "The Deck" (the heart)
- **Daily deck**: a curated stack (~15–25 cards) that refreshes daily. A visible
  "X left today" gives a finish line; finishing earns a small streak credit.
- **The stock card** (existing, refined): plain-English bio, "your-type score" +
  meter, a meaningful **Past-Year chart with % performance**, two key stats, a
  green flag + red flag. Tap = deep dive.
- **Swipe actions**: right = like (→ watchlist), left = pass, up = "watch closely"
  (super-like → priority alerts), tap = expand. **Rewind/undo** one swipe.
- **Themed decks** (beyond the daily): "Dividend machines," "Clean & green,"
  "This week's movers," "Beginner-friendly ETFs," "Outside your comfort zone"
  (deliberate wildcards to avoid a filter bubble).
- **ETFs/index funds are swipeable too** — a diversified basket is on-brand and the
  healthiest match a beginner can make; flagged as "Beginner-friendly."
- **Deep-dive sheet** (existing): fuller chart, snapshot, "why people like/worry,"
  news (clearly marked illustrative until real data), and "people with your taste
  also liked…" once there's a base.

### C. The Invest action (separate, deliberate — never the swipe)
- **Default: right-swipe parks** the stock on the watchlist/paper portfolio.
- **Investing is a distinct, calmer surface** reached from the watchlist/portfolio,
  not the deck. The match score is **not shown** on the order screen (firewall).
- **Primary path — "Invest in your matches" basket**: the app proposes a
  **diversified basket** assembled from the user's right-swipes, **ETF-weighted by
  default**, fundable as a **recurring auto-invest (DCA)**, e.g. ₹500/week. Single
  stocks are a capped minority of the basket.
- **Secondary path — single stock**: allowed, but with gentle friction and a
  diversification nudge ("This would make NOVA 60% of your portfolio — add a basket?").
- **Mechanics**: fractional shares (so ₹50/$1 works), round-ups as an *optional
  funding* mechanism (not a swipe action), recurring schedules, pause anytime.
- **Paper-first → graduate**: real-money invest unlocks only after a paper period;
  the paper portfolio mirrors the real flow exactly so there's zero new learning.

### D. Portfolio & tracking (the retention engine)
- **Paper portfolio from day one**: matches become a tracked, P&L'd practice
  portfolio. This is the day-2 reason to return *before* any money.
- **Real portfolio post-graduation**: holdings, cost basis, P&L, allocation
  donut, recurring-invest status.
- **Taste insights**: "Your portfolio is 70% high-growth, 30% steady — matches your
  bold profile" / "You've drifted toward dividends — update your type?"
- **"Matches not acted on"**: gentle surfacing of liked-but-unfunded names.
- **Tax/statements** (post-real): capital-gains/P&L docs. (Mechanics via partner.)

### E. Engagement & fun system (rewards habits, not churn)
- **Streaks**: for *showing up & finishing the daily deck* and for *consistent
  recurring investing* — never for trading frequency.
- **Weekly recap & monthly "Wrapped"**: "Your week in matches" — how many swiped,
  top matches, paper/real P&L, a learning stat, taste shifts. Highly shareable.
- **Achievements/badges**: "First basket," "Diversified" (held ≥N sectors),
  "Buy-and-hold" (held through a dip), "Curious" (read 10 deep-dives) — all
  reinforcing *good* behavior.
- **Goals & challenges**: "Invest ₹X/month," "Build a 5-sector basket," "Learn 3
  new concepts." Progress rings, gentle nudges.
- **Match moments**: keep the "It's a match!" celebration for discovery; pair with
  "no money moved — added to your watchlist" so it never reads as a trade.
- **Daily delight**: a "Card of the day," subtle motion, satisfying transitions —
  the app should feel alive (the motion system already exists).

### F. Money movement (conceptual — partner-handled)
- **Funding**: link a payment method; one-tap top-ups; recurring mandates for DCA.
- **Withdrawals**: clear, friction-light, with expected-settlement messaging.
- **Balance & cash**: a simple wallet/cash view; "available to invest."
- Out of scope to *build* here (partner), but the **UX of funding/withdrawing**
  is in scope and must feel as smooth as the swipe.

### G. Notifications & re-engagement (the pull-back)
- **Match-driven**: price/news moves on watched/owned names ("VOLT −12% — here's why").
- **Habit-driven**: "Your daily deck is ready," streak reminders, recap-ready.
- **Money-driven**: recurring-invest confirmations, funding reminders.
- **Insight-driven**: taste-drift nudges, "a new ETF matches your type."
- All **frequency-capped and user-tunable**; default to helpful, never spammy.

### H. Personalization & the taste model (the moat)
- **Cold start**: quiz → rules-based score (transparent, explainable).
- **Implicit learning**: every swipe, dwell, deep-dive, and invest is a signal;
  per-user attribute weights drift toward revealed taste.
- **Stated vs revealed**: surface the gap as a delightful insight, with consent to
  update the profile.
- **Collaborative later**: "people with your taste…" once there's scale.
- **Anti-bubble**: deliberate wildcard injection in every deck.

### I. Education layer (invisible until needed)
- **Contextual micro-lessons**: tap any term → 1-line plain-English definition.
- **"Learn" cards** interleaved in the deck occasionally (swipeable, bite-size).
- **The "why" everywhere**: every score, flag, and nudge explains itself.
- **No course, no homework** — learning is ambient, earned through use.

### J. Responsible-investing guardrails (kept even with licensing aside)
- Swipe never buys; money is always a deliberate second step.
- Diversification defaults (baskets/ETFs over single-stock concentration).
- Friction + education before concentrated or volatile bets.
- Celebrate holding, learning, consistency — not trading.
- Cooling-off on large/concentrated actions; clear "this is practice" labeling in paper.

### K. (Later) Social / community — explicitly phased out of v1
Following investors, shared decks, leaderboards. Powerful but adds moderation,
comparison-pressure, and "hot tip" risk. Park until the solo loop is proven.

---

## 2.5 Data & execution architecture — "the two engines" *(built in prototype)*

The product runs on **two separate data engines**, split by *who a surface serves*.
Nothing crosses the line; the your-type score never reaches an order screen.

| | **Discover** (deck, charts, watchlist) | **Invest + Portfolio** (orders, holdings, live P&L) |
|---|---|---|
| **Serves** | Everyone — no account, no broker | One logged-in user, their own account only |
| **Powered by** | **One delayed / EOD data feed** licensed once | **That user's own broker** (Zerodha/Upstox/…) they connect |
| **Freshness** | ~15-min delayed / EOD (labeled "Delayed") | Realtime (it's their live account) |
| **Login?** | No | Yes — "Connect your broker" |
| **Why allowed** | One licensed feed, displayed to all | The user's own data + own broker executes |

**Why broker APIs can't power Discover.** Exchange (NSE/BSE) data-vending rules
prohibit redistribution: a broker API (e.g. Zerodha **Kite Connect**, ~₹500/mo for
data) licenses realtime data to *one authenticated user for their own use*. Showing
it across a public catalog = redistribution = not allowed, regardless of whose token
fetched it. It's also per-user behind a daily login, which would gate Discover and
kill top-of-funnel. So: **delayed/vendor data for Discover; realtime only at the
order screen + the connected user's own portfolio.**

**Execution = bring-your-own-broker (the smallcase model).** Instead of becoming a
broker (custody, clearing, licensing — 18–24 months + capital), the user **connects
their own broker account**; we assemble the basket and route the order through *their*
broker. We never hold money or place trades on our own. Order/account APIs are free
on Kite (since Mar 2025). This makes Stocker **ready-to-invest without being a
broker** — sidestepping the single biggest barrier.

**Built in the prototype (simulated):**
- Discover cards + deep-dive carry a **"Delayed"** indicator.
- A **"Connect your broker"** flow (picker → simulated authorize → connected; with
  error/retry) gates the invest confirm — basket + paper portfolio work without it.
- Portfolio flips **Paper ⇄ "Live · via {broker}"**; disconnect preserves paper
  holdings and shows the plan as **paused** until reconnect. "You" tab shows connected accounts.
- Everything is simulated — connection changes framing/routing copy, not the
  underlying sim P&L. Real wiring would swap the sim for a vendor feed (Discover)
  and a broker Connect SDK (Invest/Portfolio).

---

## 3. Information architecture (navigation)
A simple, thumb-friendly tab bar:
1. **Discover** (the deck) — default.
2. **Portfolio** (paper or real: holdings, P&L, taste insights, "matches not acted on").
3. **Invest** (baskets, recurring, fund/withdraw) — or fold into Portfolio as a CTA.
4. **You** (profile/taste, streaks, achievements, recaps, settings, the score "?").

Plus overlays: deep-dive sheet, invest sheet, recap/Wrapped, coach explainers.

> Note: today's prototype has Discover + Matches. The **You** tab (taste,
> achievements, the learned-type payoff) and **Portfolio** are the biggest gaps,
> and both reviewers flagged "the taste model is invisible" — the You tab fixes that.

---

## 4. Key flows (step-by-step)

**Flow 1 — Signup → first paper portfolio**
Quiz → deck → swipe ≥10 → "Here's your taste as a portfolio (paper)" → optional
account save → daily-deck habit begins.

**Flow 2 — Daily return**
Notification → open → "Daily deck ready, 18 cards" → swipe → check paper/real P&L →
maybe read a Learn card → streak credit → close.

**Flow 3 — Go live (graduation)**
Eligibility met → "Ready to invest for real?" explainer → fund account → choose a
**basket from matches** (ETF-weighted default) → set recurring amount → confirm
(score absent on this screen) → done; recurring runs quietly.

**Flow 4 — Sell / withdraw**
Portfolio → holding → sell (with a calm "are you sure / tax note" if applicable) →
cash to wallet → withdraw. No pressure, no dark patterns.

---

## 5. Data model (sketch)
- **User**: profile vector, goal, ticket size, streak, achievements, settings.
- **Stock/Instrument**: ticker, type (stock/ETF), attributes (sector, size,
  volatility, valuation, profit, dividend, momentum), bio, flags, price series.
- **Swipe event**: user, instrument, direction, timestamp, dwell, context (deck).
- **Watchlist / Paper holding / Real holding**: user, instrument, qty, cost basis.
- **Basket**: user, constituents + weights, recurring schedule, status.
- **Score**: computed (profile × attributes), with "why" reasons.
- **Notification**: type, trigger, payload, sent/opened.

---

## 6. Success metrics
- **Activation**: % completing quiz → 10 swipes → paper portfolio created.
- **Retention (the north star)**: **D7 / D30 return rate**; daily-deck completion rate.
- **Differentiation**: stated-vs-revealed taste divergence; deep-dive open rate.
- **Conversion**: paper → go-live rate; recurring-invest setup rate.
- **Health (guardrail)**: avg holding period, diversification of new baskets,
  single-stock concentration — watch these *don't* trend toward overtrading.

---

## 7. Phasing (within "full product")
- **P1 — Sticky discovery + paper (no money):** deck, refined card, You tab,
  paper portfolio with P&L, alerts, recaps, achievements, themed decks, ETFs in deck.
  *(Everything here is buildable now and proves retention.)*
- **P2 — Real invest (partner-powered):** funding, baskets/DCA, recurring,
  go-live graduation, real portfolio, withdrawals.
- **P3 — Depth:** richer taste model (collaborative), more themed decks, goals,
  tax surfaces; *maybe* social.

---

## 8. Open questions
1. **Geography** (US vs NSE/BSE) — still the one strategic fork; gates instruments,
   currency, partners. Prototype stays market-agnostic.
2. **Baskets vs single-stock emphasis** — how hard to default people into ETFs/baskets.
3. **How much gamification is too much** — where's the line before it feels like a game, not investing.
4. **Account-gate timing** — how long to let users go anonymous before signup.
