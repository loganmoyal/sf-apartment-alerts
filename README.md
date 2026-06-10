# 🏠 SF Apartment Alert Bot

Automatically monitors Craigslist San Francisco for new apartments matching your criteria, and emails you the moment one appears.

**Criteria configured:**
- 🛏 Studio or 1 Bedroom
- 💰 Max $4,000/month
- 📍 Within ~12 min walk of Equinox Marina **or** ~8 min walk of Jackson & Polk
- ⏰ Checks every 30 minutes, 24/7

---

## ⚙️ One-Time Setup (Required)

### Step 1 — Create a Gmail App Password

You need a dedicated password for this bot (not your real Gmail password).

1. Go to your Google Account → **Security** → **2-Step Verification** (must be enabled)
2. Search for **"App passwords"** at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Create a new app password — name it `sf-apartment-bot`
4. Copy the 16-character password

### Step 2 — Add Secrets to GitHub

1. Go to your repo: [github.com/loganmoyal/sf-apartment-alerts](https://github.com/loganmoyal/sf-apartment-alerts)
2. Click **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
3. Add these two secrets:

| Secret Name | Value |
|---|---|
| `GMAIL_USER` | Your Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character app password from Step 1 |

### Step 3 — Enable GitHub Actions

1. Go to the **Actions** tab in your repo
2. Click **"I understand my workflows, go ahead and enable them"**
3. Click **Run workflow** → **Run workflow** to test it immediately

---

## 📬 How It Works

1. Every 30 minutes, GitHub runs `scraper.py` for free
2. It fetches Craigslist SF RSS feeds filtered by price and bedroom count
3. For each listing, it checks coordinates against your two target anchor points
4. New matches trigger an email to `loganmoyal@github.com`
5. Already-seen listings are saved to `seen_listings.json` so you never get duplicates

---

## 🔧 Customizing Your Criteria

Edit `scraper.py` to change:
- **`MAX_PRICE`** — your rent ceiling
- **`TARGET_LOCATIONS`** — anchor points and walking radius
- **`ALERT_EMAIL`** — where emails are sent

---

## 🗺 Target Area Map

```
Anchor 1: Equinox Marina (near Chestnut St)   37.7998, -122.4350  — 0.65 mi radius
Anchor 2: Jackson & Polk (Russian Hill)        37.7944, -122.4221  — 0.45 mi radius
```

Covers: **Pacific Heights · Cow Hollow · Marina · Russian Hill**
