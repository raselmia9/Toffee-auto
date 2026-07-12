from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json
import os

def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page) # ওয়েবসাইটকে বোকা বানাতে এই লাইনটি অত্যন্ত গুরুত্বপূর্ণ

        if os.path.exists('cookies.json'):
            with open('cookies.json', 'r') as f:
                context.add_cookies(json.load(f))

        results = {"streaming_link": None, "referral_url": "https://toffeelive.com/en/"}

        def on_response(response):
            # স্ট্রিম লিংক ধরার জন্য ফিল্টার
            if "m3u8" in response.url and "edge-cache-token" in response.url:
                results["streaming_link"] = response.url

        page.on("response", on_response)

        print("Navigating...")
        page.goto("https://toffeelive.com/en/", timeout=60000)
        page.wait_for_timeout(10000)
        
        # চ্যানেলের লিংকে যাওয়া
        links = page.eval_on_selector_all('a[href*="/watch/"]', "els => els.map(e => e.href)")
        if links:
            page.goto(links[0], timeout=60000)
            page.wait_for_timeout(20000)

        # JSON আউটপুট
        with open('stream_data.json', 'w') as f:
            json.dump(results, f, indent=4)
        
        browser.close()

if __name__ == "__main__":
    capture_all()
                
