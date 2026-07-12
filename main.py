from playwright.sync_api import sync_playwright
import json

def get_channel_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Visiting Homepage...")
        page.goto("https://toffeelive.com/en/", timeout=60000)
        page.wait_for_timeout(10000) 
        
        # সব চ্যানেলের লিংকের জন্য CSS selector ব্যবহার করা
        # এটি সাধারণত 'a' ট্যাগ থেকে নেওয়া হয় যা নির্দিষ্ট পাথে যায়
        links = page.eval_on_selector_all('a[href*="/watch/"]', "elements => elements.map(e => e.href)")
        
        # ইউনিক লিংকগুলো রাখা
        unique_links = list(set(links))
        
        with open('channels.json', 'w') as f:
            json.dump(unique_links, f, indent=4)
            
        print(f"Found {len(unique_links)} channels. Saved to channels.json")
        browser.close()

if __name__ == "__main__":
    get_channel_links()
        
