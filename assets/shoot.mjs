// Dependency-free screenshot driver: launches headless Chrome, drives the live
// app on :4192 via the DevTools Protocol, saves PNGs to assets/shots/.
// Captures the current IA: onboarding, swipe tutorial, deck card, match,
// Matches (shortlist), Portfolio (invested), You.
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, rmSync } from 'node:fs';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const APP = 'http://localhost:4192/index.html';
const OUT = new URL('./shots/', import.meta.url).pathname;
try { rmSync(OUT, { recursive: true, force: true }); } catch {}
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--hide-scrollbars',
  '--remote-debugging-port=9222', '--user-data-dir=/tmp/stocker-shots2',
  '--window-size=430,932', APP,
]);
chrome.on('error', (e) => { console.error('chrome spawn error', e); process.exit(1); });

async function findPage() {
  for (let i = 0; i < 40; i++) {
    try {
      const list = await (await fetch('http://localhost:9222/json')).json();
      const p = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
      if (p) return p.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error('no page target');
}

const wsUrl = await findPage();
const ws = new WebSocket(wsUrl);
await new Promise((res) => (ws.onopen = res));
let id = 0; const pending = new Map();
ws.onmessage = (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
};
const send = (method, params = {}) =>
  new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const evall = async (expr) =>
  (await send('Runtime.evaluate', { expression: `(function(){${expr}})()`, returnByValue: true })).result?.value;
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
  writeFileSync(OUT + name + '.png', Buffer.from(r.data, 'base64'));
  console.log('saved', name);
}

await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 430, height: 932, deviceScaleFactor: 2, mobile: true });
await evall("try{localStorage.clear()}catch(e){}; location.reload(); return 1;");
await sleep(1900);

// 1) onboarding
await evall("window.scrollTo(0,0); return 1;");
await shot('01-onboarding');

// answer the quiz + build the deck
await evall(`
  function pick(t){var e=[].slice.call(document.querySelectorAll('.chip')).find(function(x){return x.textContent.indexOf(t)>-1;}); if(e){e.click();}}
  ['Grow long-term','Balanced','1\\u20135 years','Growth','Tech','Clean'].forEach(pick);
  var b=[].slice.call(document.querySelectorAll('button')).find(function(x){return x.textContent.indexOf('Build my deck')>-1;}); if(b)b.click();
  return 1;
`);
await sleep(900);

// 2) first-run swipe tutorial (auto-shows over the first card)
await shot('02-swipe-tutorial');

// dismiss the tutorial + the your-type-score tip that follows
const closeOverlays = `
  var c=document.querySelector('#st-ok'); if(c) c.click();
  var b=[].slice.call(document.querySelectorAll('button,.btn')).find(function(x){return /^(got it|got it — start swiping|ok|keep swiping)$/i.test(x.textContent.trim());});
  if(b){b.click(); return b.textContent.trim();}
  return 'none';
`;
await evall(closeOverlays); await sleep(500);
await evall(closeOverlays); await sleep(500);
await evall("['.swipe-tut','.coach-bg'].forEach(function(s){var e=document.querySelector(s); if(e) e.remove();}); window.scrollTo(0,0); return 1;");
await sleep(1300); // card rise + score meter fill

// 3) deck card (with company logo)
await shot('03-deck');

// 4) match moment — super-like the top card guarantees the modal
await evall("var b=document.getElementById('b-super'); if(b)b.click(); return 1;");
await sleep(1500);
await shot('04-match');
await evall("var k=document.getElementById('mk'); if(k)k.click(); document.querySelectorAll('.modal-bg').forEach(function(e){e.remove();}); return 1;");

// build a richer shortlist, then 5) Matches tab
await evall(`
  ['RELIANCE','TCS','HDFCBANK','DMART','INFY','MARUTI'].forEach(function(tk){ var st=BY_SYM[tk]; if(st) addMatch(Object.assign({}, st, matchScore(st))); });
  document.querySelectorAll('.modal-bg').forEach(function(e){e.remove();});
  saveState(); show('matches'); renderMatches(); window.scrollTo(0,0); return watchlist.length;
`);
await sleep(500);
await shot('05-matches');

// 6) Portfolio — simulate a completed paper investment so positions + P&L show
await evall(`
  plan={amt:1500, freq:'once', weighting:'balanced', tickers:['RELIANCE','TCS','HDFCBANK','DMART'], broker:null, orders:[{demo:true}]};
  saveState(); show('pf'); renderPortfolio(); window.scrollTo(0,0); return 1;
`);
await sleep(500);
await shot('06-portfolio');

// 7) You — opened from the top-right profile button
await evall("var y=document.getElementById('you-btn'); if(y)y.click(); window.scrollTo(0,0); return 1;");
await sleep(500);
await shot('07-you');

ws.close();
chrome.kill();
console.log('=== DONE ===');
process.exit(0);
