from playwright.sync_api import sync_playwright
import json

def fetch_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # stealth ব্যবহার না করেই প্রথমে দেখি কাজ করে কি না
        print("Navigating to Toffee...")
        try:
            page.goto("https://toffeelive.com/en/watch/oDRWpp4Bb1O6C9k7We2Q", timeout=60000)
            page.wait_for_timeout(10000) 
            
            cookies = context.cookies()
            with open('cookies.json', 'w') as f:
                json.dump(cookies, f, indent=4)
            print("Successfully saved cookies.json")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_cookies()
    
