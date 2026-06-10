import feedparser
import json
import smtplib
import os
import math
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuration ────────────────────────────────────────────────────────────
MAX_PRICE = 4000
ALERT_EMAIL = "loganmoyal@github.com"

# M365 / Office 365 SMTP credentials (set as GitHub Actions secrets)
SMTP_USER     = os.environ.get("SMTP_USER")       # your M365 email address
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")   # your M365 password or app password
SMTP_SERVER   = "smtp.office365.com"
SMTP_PORT     = 587

# Anchor points with max straight-line walking radius in miles
# (straight-line * ~1.3 ≈ actual city walking distance)
TARGET_LOCATIONS = [
    {
        "name": "Equinox Marina (Chestnut St area)",
        "lat": 37.7998,
        "lon": -122.4350,
        "max_miles": 0.65,  # ≈ 12 min walk
    },
    {
        "name": "Jackson & Polk (Russian Hill)",
        "lat": 37.7944,
        "lon": -122.4221,
        "max_miles": 0.45,  # ≈ 8 min walk
    },
]

# Craigslist RSS feeds — studio (0BR) and 1BR, max $4,000
CRAIGSLIST_FEEDS = [
    "https://sfbay.craigslist.org/search/sfc/apa?format=rss&max_price=4000&min_bedrooms=0&max_bedrooms=0",
    "https://sfbay.craigslist.org/search/sfc/apa?format=rss&max_price=4000&min_bedrooms=1&max_bedrooms=1",
]

SEEN_FILE = "seen_listings.json"

# Fallback neighborhood keywords (used when listing has no coordinates)
TARGET_NEIGHBORHOODS = [
    "pacific heights", "pac heights", "pac hts",
    "marina district", "marina",
    "cow hollow",
    "russian hill",
    "lower pac heights", "lower pacific heights",
]


# ── Utilities ─────────────────────────────────────────────────────────────────

def haversine_miles(lat1, lon1, lat2, lon2):
    """Straight-line distance in miles between two lat/lon points."""
    R = 3959
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def within_target_area(lat, lon):
    """Return (True, location_name, est_walk_mins) if within any target radius."""
    for loc in TARGET_LOCATIONS:
        dist = haversine_miles(lat, lon, loc["lat"], loc["lon"])
        if dist <= loc["max_miles"]:
            walk_mins = round(dist / 3 * 60)  # 3 mph walking speed
            return True, loc["name"], walk_mins
    return False, None, None


def neighborhood_match(text):
    t = text.lower()
    return any(n in t for n in TARGET_NEIGHBORHOODS)


def load_seen():
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


# ── Email ─────────────────────────────────────────────────────────────────────

def send_email(matches):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️  Email credentials not set — skipping email.")
        return

    count = len(matches)
    subject = f"🏠 {count} New SF Apartment Match{'es' if count > 1 else ''}!"

    html = """
    <html><body style="font-family:sans-serif;max-width:600px;margin:auto;">
    <h2 style="color:#2c5f2e;">🏠 New SF Apartment Match!</h2>
    <p><strong>Your criteria:</strong> Studio or 1BR &nbsp;|&nbsp; Max $4,000/mo &nbsp;|&nbsp; Near Equinox Marina or Jackson &amp; Polk</p>
    <hr style="margin:20px 0;">
    """
    for m in matches:
        html += f"""
        <div style="margin-bottom:24px;padding:16px;border:1px solid #e0e0e0;border-radius:8px;background:#fafafa;">
            <h3 style="margin:0 0 8px;"><a href="{m['link']}" style="color:#1a0dab;">{m['title']}</a></h3>
            <p style="margin:4px 0;color:#555;">📍 {m['location_info']}</p>
            <p style="margin:8px 0;color:#333;">{m['summary']}</p>
            <a href="{m['link']}" style="display:inline-block;background:#2c5f2e;color:white;padding:8px 18px;
               text-decoration:none;border-radius:6px;font-weight:bold;">View on Craigslist →</a>
        </div>
        """
    html += """
    <p style="color:#aaa;font-size:11px;margin-top:30px;">
        Sent by your SF Apartment Alert Bot · github.com/loganmoyal/sf-apartment-alerts
    </p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())

    print(f"✅ Email sent with {count} match(es).")


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    seen = load_seen()
    is_first_run = len(seen) == 0  # Seed mode: don't alert on first run
    new_matches = []

    if is_first_run:
        print("🌱 First run detected — seeding existing listings silently (no email). Future new listings will trigger alerts.")

    for feed_url in CRAIGSLIST_FEEDS:
        print(f"Fetching: {feed_url}")
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            listing_id = entry.get("id") or entry.get("link", "")
            if listing_id in seen:
                continue
            seen.add(listing_id)

            title = entry.get("title", "No title")
            link = entry.get("link", "")
            summary = entry.get("summary", "")[:400]

            matched = False
            location_info = "Location unknown — verify manually"

            # Try coordinate-based matching first
            raw_lat = entry.get("geo_lat") or entry.get("geo.lat")
            raw_lon = entry.get("geo_long") or entry.get("geo.long")

            if raw_lat and raw_lon:
                try:
                    lat, lon = float(raw_lat), float(raw_lon)
                    ok, loc_name, walk_mins = within_target_area(lat, lon)
                    if ok:
                        matched = True
                        location_info = f"~{walk_mins} min walk from {loc_name}"
                except (ValueError, TypeError):
                    pass

            # Fallback: neighborhood keyword matching
            if not matched and neighborhood_match(title + " " + summary):
                matched = True
                location_info = "Neighborhood keyword match — verify exact location"

            if matched:
                new_matches.append({
                    "title": title,
                    "link": link,
                    "location_info": location_info,
                    "summary": summary,
                })
                print(f"  ✓ MATCH: {title}")

    save_seen(seen)

    if is_first_run:
        print(f"\n✅ Seed complete. {len(seen)} existing listings saved. Bot is now watching for new ones.")
        return

    print(f"\nDone. {len(new_matches)} new match(es) | {len(seen)} total listings seen.")

    if new_matches:
        send_email(new_matches)


if __name__ == "__main__":
    run()
