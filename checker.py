import os
import asyncio
from datetime import datetime, timezone
from playwright.async_api import async_playwright
import requests

URL = "https://miuruguay.com.uy/categoria-producto/outlet/"
SEARCH_STRING = "Pad 7 8GB"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")  # auto-provided by Actions
LAST_HEARTBEAT_VAR = "LAST_HEARTBEAT"

def send_discord(message):
    if not DISCORD_WEBHOOK:
        print("Discord webhook missing")
        return
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def get_last_heartbeat():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/variables/{LAST_HEARTBEAT_VAR}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    r = requests.get(url, headers=headers)
    if r.status_code // 100 == 2:
        return r.json().get("value")
    return None

def set_last_heartbeat(ts: str):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/variables/{LAST_HEARTBEAT_VAR}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    requests.patch(url, headers=headers, json={"name": LAST_HEARTBEAT_VAR, "value": ts})

def check_heartbeat():
    now = datetime.now(timezone.utc)
    last = get_last_heartbeat()
    if last:
        last_dt = datetime.fromisoformat(last)
        diff = (now - last_dt).total_seconds()
        if diff < 86300:  # 24 hours
            return
    send_discord("✅ Outlet checker is alive and running.")
    set_last_heartbeat(now.isoformat())

async def check_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_timeout(6000)
        content = await page.content()
        await browser.close()
        if SEARCH_STRING.lower() in content.lower():
            send_discord(f"Product match found: '{SEARCH_STRING}'\n{URL}")
        else:
            print("String not found.")

if __name__ == "__main__":
    check_heartbeat()
    asyncio.run(check_page())
