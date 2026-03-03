import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL = "https://miuruguay.com.uy/categoria-producto/outlet/"
SEARCH_STRING = "Jarra eléctrica"

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord(message):
    if not DISCORD_WEBHOOK:
        print("Discord webhook missing")
        return

    data = {
        "content": message
    }

    requests.post(DISCORD_WEBHOOK, json=data)

async def check_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(URL, timeout=60000)
        await page.wait_for_timeout(6000)  # allow JS products to load

        content = await page.content()
        await browser.close()

        if SEARCH_STRING.lower() in content.lower():
            send_discord(
                f"Product match found: '{SEARCH_STRING}'\n{URL}"
            )
        else:
            print("String not found.")

if __name__ == "__main__":
    asyncio.run(check_page())
