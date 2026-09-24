#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests

TZ = ZoneInfo("America/Vancouver")
TODAY = datetime.now(TZ).date()
DATE_ISO = TODAY.isoformat()
YMD = TODAY.strftime("%Y/%m/%d")

OUT_DIR = Path("pritchard-menu")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "current.json"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; PritchardMenuBridge/1.0; +https://github.com/realmyca/MotionSensor-Arduino)"
})

MEALS = ("breakfast", "lunch", "dinner")

def api_candidates():
    candidates = ["ubcok"]
    # Try to discover the Nutrislice API tenant from the public UBCO page.
    try:
        html = SESSION.get("https://ubcok.nutrislice.com/menu", timeout=20).text
        for match in re.findall(r"https?://([a-z0-9-]+)\.api\.nutrislice\.com", html, flags=re.I):
            if match not in candidates:
                candidates.append(match)
    except Exception:
        pass
    return candidates

def compact_nutrition(food):
    n = food.get("rounded_nutrition_info") or {}
    keep = ("calories", "g_protein", "g_fiber", "g_carbs", "g_fat", "g_sugar", "mg_sodium")
    return {k: n.get(k) for k in keep if n.get(k) is not None}

def simplify_day(day, source_url):
    items = []
    current_station = None
    for raw in day.get("menu_items", []):
        if raw.get("is_station_header"):
            current_station = (raw.get("text") or "").strip() or current_station
            continue
        if raw.get("is_section_title"):
            text = (raw.get("text") or "").strip()
            if text:
                current_station = text
            continue

        food = raw.get("food")
        if not food or not food.get("name"):
            continue

        serving = food.get("serving_size_info") or {}
        icons = food.get("icons") or {}
        food_icons = icons.get("food_icons") or []

        items.append({
            "name": food.get("name"),
            "station": current_station,
            "category": food.get("food_category") or raw.get("category") or None,
            "description": food.get("description") or None,
            "ingredients": food.get("ingredients") or None,
            "serving_size": {
                "amount": serving.get("serving_size_amount"),
                "unit": serving.get("serving_size_unit"),
            },
            "nutrition": compact_nutrition(food),
            "dietary_icons": [
                x.get("name") or x.get("synced_name")
                for x in food_icons
                if (x.get("name") or x.get("synced_name"))
            ],
        })

    return {
        "date": day.get("date"),
        "items": items,
        "source": source_url,
    }

def fetch_meal(meal, districts):
    attempts = []
    for district in districts:
        url = (
            f"https://{district}.api.nutrislice.com/menu/api/weeks/"
            f"school/pritchard/menu-type/{meal}/{YMD}/?format=json"
        )
        try:
            r = SESSION.get(url, timeout=25)
            attempts.append({"url": url, "status": r.status_code})
            r.raise_for_status()
            data = r.json()
            for day in data.get("days", []):
                if day.get("date") == DATE_ISO:
                    result = simplify_day(day, url)
                    result["ok"] = True
                    result["attempts"] = attempts
                    return result
            attempts[-1]["error"] = "today_not_present_in_days"
        except Exception as e:
            attempts[-1]["error"] = f"{type(e).__name__}: {e}"

    return {
        "date": DATE_ISO,
        "ok": False,
        "items": [],
        "attempts": attempts,
    }

districts = api_candidates()
result = {
    "generated_at": datetime.now(TZ).isoformat(),
    "timezone": "America/Vancouver",
    "date": DATE_ISO,
    "location": "Pritchard Dining Hall, UBC Okanagan",
    "district_candidates": districts,
    "meals": {},
}

for meal in MEALS:
    result["meals"][meal] = fetch_meal(meal, districts)

tmp = OUT_FILE.with_suffix(".tmp")
tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
tmp.replace(OUT_FILE)

ok_count = sum(1 for m in result["meals"].values() if m.get("ok"))
print(f"Wrote {OUT_FILE}; {ok_count}/{len(MEALS)} meal endpoints succeeded for {DATE_ISO}.")
for meal, payload in result["meals"].items():
    print(meal, "OK" if payload.get("ok") else "FAILED", len(payload.get("items", [])), "items")
    if not payload.get("ok"):
        print(json.dumps(payload.get("attempts", []), indent=2))

# Fail only if all three endpoints are unreachable. This keeps diagnostics committed
# when at least one meal is valid while still making complete outages visible.
if ok_count == 0:
    sys.exit(2)
