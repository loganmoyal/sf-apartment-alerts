# 🏠 SF Apartment Alert Bot

Automatically monitors Craigslist San Francisco for new apartments matching your criteria, and emails you the moment one appears.

**Criteria configured:**
- 🛏 Studio or 1 Bedroom
- 💰 Max $4,000/month
- 📍 Within ~12 min walk of Equinox Marina **or** ~8 min walk of Jackson & Polk
- ⏰ Checks every 30 minutes, 24/7

---

## ⚙️ One-Time Setup (Required)

### Step 1 — Get a Free Resend API Key

[Resend](https://resend.com) is a free email API (3,000 emails/month). No account credentials needed — just a single API key.

1. Sign up free at [resend.com](https://resend.com)
2. Go to **API Keys** → **Create API key** (name it `sf-apartment-bot`)
3. Copy the key (starts with `re_...`)

> If the key ever leaks, just revoke it from the Resend dashboard — your real accounts are never at risk.

### Step 2 — Add the Secret to GitHub

1. Go to your repo: [github.com/loganmoyal/sf-apartment-alerts](https://github.com/loganmoyal/sf-apartment-alerts)
2. Click **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
3. Add one secret:

| Secret Name | Value |
|---|---|
| `RESEND_API_KEY` | Your Resend API key (e.g. `re_abc123...`) |

### Step 3 — Enable GitHub Actions & First Run

1. Go to the **Actions** tab in your repo
2. Click **"I understand my workflows, go ahead and enable them"**
3. Click **Run workflow** → **Run workflow** to kick off the first run

> **First run = seed only.** It silently saves all current listings and sends no email. Every run after that only alerts you to brand-new listings.

---

## ⏸ Pausing / Disabling the Bot

To pause alerts:
1. Go to **Actions** tab → click **SF Apartment Alert Bot**
2. Click the **•••** (three dots) menu → **Disable workflow**

To resume: same steps → **Enable workflow**

> GitHub also auto-disables scheduled workflows after **60 days of repo inactivity** — just re-enable it if that happens.

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
