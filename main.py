from playwright.sync_api import sync_playwright
import json
import os

def capture_stream_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # রিয়েল ব্রাউজার হিসেবে কনফিগারেশন
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # কুকি ফাইল লোড করা
        cookies = []
        if os.path.exists('cookies.json'):
            with open('cookies.json', 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)

        page = context.new_page()
        
        # ডেটা স্টোর করার জন্য ডিকশনারি
        output_data = {
            "streaming_link": None,
            "cookies": cookies,
            "referral_url": "https://toffeelive.com/en/"
        }

        def handle_request(request):
            # স্ট্রিম লিংক ক্যাপচার
            if "m3u8" in request.url and "edge-cache-token" in request.url:
                output_data["streaming_link"] = request.url

        page.on("request", handle_request)

        # হোম পেজ থেকে শুরু
        print("Navigating to Homepage...")
        page.goto("https://toffeelive.com/en/", timeout=90000)
        page.wait_for_timeout(10000) 
        
        # প্রথম চ্যানেলে যাওয়া
        links = page.eval_on_selector_all('a[href*="/watch/"]', "elements => elements.map(e => e.href)")
        if links:
            print(f"Navigating to channel: {links[0]}")
            page.goto(links[0], timeout=90000)
            page.wait_for_timeout(30000)

        # JSON ফাইল হিসেবে আউটপুট দেওয়া
        with open('stream_data.json', 'w') as f:
            json.dump(output_data, f, indent=4)
            
        print("Data saved to stream_data.json")
        browser.close()

if __name__ == "__main__":
    capture_stream_data()
        
