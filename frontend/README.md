# Telegram mini app (test client)

Vite + React app for testing the client side of Telegram booking against this backend
(`/api/v1/mini-app`). For now it covers **registration**:

1. On open it calls `GET /mini-app/me` with `Authorization: tma <initData>`.
2. Not registered (`GLOBAL_CLIENT_NOT_REGISTERED`) → registration form: first name, last name,
   sex (required), middle name, birth date, call phone (optional) and a **"Поделиться номером"**
   button (`WebApp.requestContact`) for the verified Telegram phone.
3. Submits `POST /mini-app/me` → shows the saved profile.

Any API error is shown with its `error_code`, to make testing easier.

## Backend requirements

- `TELEGRAM_MINIAPP_BOT_TOKEN` — token of **the bot that opens this mini app**. `initData` and the
  shared contact are signed with it; a token of another bot gives `TELEGRAM_AUTH_INVALID`.
- The `global_clients` table must exist (the updated migration `6fc935148fe5`).
- `TELEGRAM_MINIAPP_ORIGIN` — only if the mini app calls the API on another domain (see below).

## Run locally

```bash
npm install
cp .env.example .env     # defaults are fine for local testing
npm run dev              # http://localhost:5173, /api is proxied to VITE_DEV_PROXY_TARGET
```

Telegram opens mini apps over HTTPS only. To test from your phone, tunnel the dev server
(e.g. `cloudflared tunnel --url http://localhost:5173`) and give the tunnel URL to BotFather.
Opened in a normal browser, the app just says to open it from Telegram.

## Deploy on the VPS

```bash
npm ci
npm run build            # -> dist/
sudo mkdir -p /var/www/miniapp && sudo cp -r dist/* /var/www/miniapp/
```

Serve it on its own subdomain and proxy `/api/v1` to the backend from the same server block.
The mini app then calls the API on its own origin, so no CORS setup is needed
(`VITE_API_BASE_URL` stays empty):

```nginx
server {
    listen 443 ssl;
    server_name miniapp.osipovich.uz;
    # ssl_certificate ... (certbot --nginx -d miniapp.osipovich.uz)

    root /var/www/miniapp;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/v1 {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Alternatively, build with `VITE_API_BASE_URL=https://api.osipovich.uz` and set
`TELEGRAM_MINIAPP_ORIGIN=https://miniapp.osipovich.uz` on the backend, so CORS allows it.

### Or under the existing CRM domain (no new subdomain)

Serve it at `https://crm.osipovich.uz/miniapp/`. The CRM's server block already proxies `/api/v1`,
so the app reaches the API on its own origin - no CORS setup either.

```bash
VITE_BASE_PATH=/miniapp/ npm run build    # assets then load from /miniapp/assets/...
sudo mkdir -p /var/www/miniapp && sudo cp -r dist/* /var/www/miniapp/
```

Add to the existing `crm.osipovich.uz` server block (nginx picks the longest matching prefix, so
this wins over the CRM's `location /`; the CRM itself is untouched):

```nginx
location /miniapp/ {
    alias /var/www/miniapp/;
    try_files $uri $uri/ /miniapp/index.html;
}
```

BotFather URL: `https://crm.osipovich.uz/miniapp/`.

## Connect it to the bot

In @BotFather: `/mybots` → the bot → **Bot Settings → Menu Button** (or **Configure Mini App**)
→ `https://miniapp.osipovich.uz/`. Then open the bot in Telegram and tap the button.

## What to check

- First open → registration form, first/last name prefilled from Telegram.
- "Поделиться номером" → Telegram's own confirmation → ✓ with your number.
- Submit → profile with `telegram_phone` from Telegram and the typed `call_phone`.
- Reopen → the profile right away (already registered).
- Declining Telegram's phone prompt → "Вы не поделились номером", and the form stays disabled until you share it.
