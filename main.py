from playwright.sync_api import sync_playwright
import json

def capture_stream_link():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # নেটওয়ার্ক রিকোয়েস্ট মনিটর করার ফাংশন
        def handle_request(request):
            if "m3u8" in request.url:
                print(f"Found Stream Link: {request.url}")
                with open('stream_link.txt', 'w') as f:
                    f.write(request.url)

        page.on("request", handle_request)

        print("Navigating to Toffee...")
        # এখানে আপনার কাঙ্ক্ষিত ভিডিও পেজটির লিংক দিন
        page.goto("https://toffeelive.com/en/watch/oDRWpp4Bb1O6C9k7We2Q", timeout=60000)
        page.wait_for_timeout(15000) # লিংক লোড হওয়ার জন্য সময় দেওয়া
        
        browser.close()

if __name__ == "__main__":
    capture_stream_link()
    
