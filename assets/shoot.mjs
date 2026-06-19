// Dependency-free screenshot driver: launches headless Chrome, drives the live
// app on :4192 via the DevTools Protocol, saves PNGs to assets/shots/.
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const APP = 'http://localhost:4192/';
const OUT = new URL('./shots/', import.meta.url).pathname;
mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--hide-scrollbars',
  '--remote-debugging-port=9222', '--user-data-dir=/tmp/stocker-shots',
  '--window-size=430,900', APP,
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
await send('Emulation.setDeviceMetricsOverride', { width: 430, height: 900, deviceScaleFactor: 2, mobile: true });
await evall("try{localStorage.clear()}catch(e){}; location.reload(); return 1;");
await sleep(1800);

// 1) onboarding
await evall("window.scrollTo(0,0); return 1;");
await shot('01-onboarding');

// answer the quiz + build the deck
const picked = await evall(`
  function pick(t){var e=[].slice.call(document.querySelectorAll('.chip')).find(function(x){return x.textContent.indexOf(t)>-1;}); if(e){e.click(); return true;} return false;}
  var ok=[pick('Grow long-term'),pick('Balanced'),pick('1\\u20135 years'),pick('Growth'),pick('Tech'),pick('Clean')];
  var b=[].slice.call(document.querySelectorAll('button')).find(function(x){return x.textContent.indexOf('Build my deck')>-1;}); if(b)b.click();
  return JSON.stringify(ok);
`);
console.log('picked', picked);
await sleep(900);
// dismiss any coach/explainer overlays (general coach + "your-type score" tip)
const closeCoach = `
  var c=document.querySelector('#coach-ok'); if(c){c.click();}
  var b=[].slice.call(document.querySelectorAll('button,.btn')).find(function(x){return /^(got it|ok|keep swiping)$/i.test(x.textContent.trim());});
  if(b){b.click(); return b.textContent.trim();}
  return c?'coach-ok':'none';
`;
await evall(closeCoach); await sleep(400);
await evall(closeCoach); await sleep(400);   // second pass for a chained tip
await evall("window.scrollTo(0,0); return 1;");
await sleep(1300); // let the card rise + score meter fill

// 2) deck card
const top = await evall("var t=document.querySelector('#deck .card .tk, .card .tk'); return t?t.textContent:'?';");
console.log('top card', top);
await shot('02-deck');

// like one card first (adds a holding) so the portfolio is diversified
await evall("var b=document.getElementById('b-like'); if(b)b.click(); return 1;");
await sleep(1000); // card flies out, next card rises

// 3) match moment (super-like guarantees the modal)
await evall("var b=document.getElementById('b-super'); if(b)b.click(); return 1;");
await sleep(500);
await shot('03-match');

// 4) portfolio
await evall("var b=document.getElementById('mv'); if(b)b.click(); window.scrollTo(0,0); return 1;");
await sleep(700);
await shot('04-portfolio');

// 5) you / your investing type
await evall("var t=[].slice.call(document.querySelectorAll('[data-tab]')).find(function(x){return x.getAttribute('data-tab')==='you';}); if(t)t.click(); window.scrollTo(0,0); return 1;");
await sleep(600);
await shot('05-you');

ws.close();
chrome.kill();
console.log('done');
process.exit(0);
