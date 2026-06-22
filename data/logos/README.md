# Company logos

Square-ish PNGs named `<TICKER>.png`, shown on the discovery cards (the avatar
badge) and rendered on a white tile via `object-fit: contain`.

- **Source:** official company logos from Wikipedia / Wikimedia Commons infoboxes,
  rasterised to ≤256px. They are the respective companies' trademarks, used here
  only as identifiers for the stock they represent (nominative use).
- **Fallback:** if a `<TICKER>.png` is absent or fails to load, the card falls
  back to the colored 2-letter initials badge (handled by `onerror` in the app).
- **Coverage:** 13/14 listed stocks have a logo. `SUNPHARMA` has no free logo on
  Commons, so it uses the initials fallback. To add one, drop `SUNPHARMA.png` here.
