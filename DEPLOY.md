# Stocker — Go-live runbook (free stack)

**Launch shape:** public site runs in **DEMO mode** (no Kite keys → no real money, no
regulatory exposure, clean for everyone). You keep **real trading on a private
instance** (your laptop, or a second locked-down VM) with your Kite keys.

**Stack:** Oracle Cloud Always-Free VM (free **static IP**) · Caddy (auto-HTTPS) ·
gunicorn+systemd · Cloudflare DNS · cheap real domain (~₹800/yr) · cron for data.

Artifacts referenced live in `deploy/`. Replace `stocker.example.com` and
`ubuntu`/paths to match your setup.

---

## 1. Domain (~₹800/yr)
- Buy a domain at **Porkbun** or **Cloudflare Registrar** (at-cost). *Avoid free
  .tk/.ml domains — unreliable.*
- Add it to **Cloudflare** (free plan) for DNS.

## 2. Oracle Cloud Always-Free VM
1. Create an Oracle Cloud account → **Compute → Instances → Create**.
2. Shape: **VM.Standard.A1.Flex** (Arm, Always-Free) — if "out of capacity," retry a
   different availability domain or use **VM.Standard.E2.1.Micro** (x86, also free).
3. Image: **Ubuntu 22.04**. Add your SSH key.
4. **Networking → reserve a public IP** (make it **Reserved**, not Ephemeral) — this is
   the **static IP** Kite needs. Note it down.
5. **Ingress rules** (VCN → Security List): allow **TCP 80** and **TCP 443** from
   `0.0.0.0/0`. (SSH 22 is open by default.)

## 3. Point the domain at the VM
- In Cloudflare DNS: add an **A record** `stocker.example.com → <VM static IP>`.
- Set it **DNS-only** (grey cloud) for the first TLS issuance, then you can proxy later.

## 4. Server setup (SSH into the VM)
```bash
sudo apt update && sudo apt install -y python3-venv git
# get the code
git clone <your-repo-url> /home/ubuntu/stocker
cd /home/ubuntu/stocker
python3 -m venv .venv
.venv/bin/pip install -r stock-match/requirements.txt
# seed the free data
cd stock-match && ../.venv/bin/python fetch_bhavcopy.py && ../.venv/bin/python fetch_history.py && ../.venv/bin/python fetch_news.py && cd ..
# (DEMO mode → no .env / no Kite keys needed)
```

## 5. Run it as a service (gunicorn + systemd)
```bash
sudo cp stock-match/deploy/stocker.service /etc/systemd/system/stocker.service
sudo systemctl daemon-reload
sudo systemctl enable --now stocker
curl -s localhost:8000/api/status   # → {"demo":true,...}
```

## 6. HTTPS with Caddy
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy.gpg
echo "deb [signed-by=/usr/share/keyrings/caddy.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main" | sudo tee /etc/apt/sources.list.d/caddy.list
sudo apt update && sudo apt install -y caddy
sudo cp /home/ubuntu/stocker/stock-match/deploy/Caddyfile /etc/caddy/Caddyfile
sudo sed -i 's/stocker.example.com/YOURDOMAIN/' /etc/caddy/Caddyfile
sudo systemctl restart caddy
```
Visit **https://YOURDOMAIN** → Stocker live with a valid certificate. 🎉

## 7. Daily data refresh (cron)
```bash
chmod +x /home/ubuntu/stocker/stock-match/deploy/refresh-data.sh
sudo timedatectl set-timezone Asia/Kolkata   # so the schedule is IST
crontab -e
```
Add:
```
30 18 * * 1-5  /home/ubuntu/stocker/stock-match/deploy/refresh-data.sh daily   >> /home/ubuntu/refresh.log 2>&1
0  9  * * 6     /home/ubuntu/stocker/stock-match/deploy/refresh-data.sh weekly  >> /home/ubuntu/refresh.log 2>&1
```

## 8. Updating later
```bash
bash /home/ubuntu/stocker/stock-match/deploy/deploy.sh
```

---

## Your private REAL-trading instance (just you)
Don't put Kite keys on the public VM. To trade for real, run a **private** instance
(your laptop, or a second small VM whose IP you whitelist on Kite):
```bash
KITE_API_KEY=key KITE_API_SECRET=secret python3 server.py
```
- Whitelist **that machine's** public IP on the Kite app.
- Set the Kite **Redirect URL** to match where it runs (`http://127.0.0.1:4173/api/callback`
  locally, or `https://your-private-host/api/callback`).
- Reminder: single-account Kite app → only your (app-owner) account can place real orders.

---

## When you want REAL multi-user investing (the next project)
This stack is the public demo. To let *the public* invest for real you need:
1. **smallcase Gateway** (multi-broker, multi-user) instead of a raw Kite app.
2. **Per-user sessions + a database** (the prototype keeps one in-memory session).
3. A **registered entity + legal/compliance** review.
4. Likely a **paid VPS** (Hetzner/DigitalOcean ~₹400–500/mo) for dependable uptime —
   Oracle's free tier can reclaim idle resources without warning.

## What I can't do for you
Create the Oracle account, buy the domain, or enter logins/payment/keys — those are
yours. Everything scriptable (configs above) is done; the runbook is copy-paste.
