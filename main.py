import os
import re
import asyncio
from playwright.async_api import async_playwright

# আপনার M3U ফাইলের নাম
M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def get_fresh_cookie():
    edge_cookie = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            # যেকোনো একটা সচল চ্যানেলের লিংক দিয়ে কুকি ফেচ করা যেতে পারে, মূল পেজ থেকেও কুকি পাওয়া যায়
            await page.goto("https://toffeelive.com/en/live", timeout=60000)
            await page.wait_for_timeout(6000)

            cookies = await context.cookies()
            for cookie in cookies:
                if cookie["name"] == "Edge-Cache-Cookie":
                    edge_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                    break
        except Exception as e:
            print("কুকি ফেচ করতে সমস্যা হয়েছে:", e)
        finally:
            await browser.close()
            
    return edge_cookie

async def update_m3u_cookie():
    if not os.path.exists(M3U_FILE_NAME):
        print(f"ত্রুটি: {M3U_FILE_NAME} ফাইলটি পাওয়া যায়নি! দয়া করে একটি বেস M3U ফাইল আগে আপলোড করুন।")
        return

    print("টফি সাইট থেকে নতুন কুকি সংগ্রহ করা হচ্ছে...")
    new_cookie = await get_fresh_cookie()

    if not new_cookie:
        print("নতুন কুকি পাওয়া যায়নি, তাই আপডেট বাতিল করা হলো।")
        return

    print(f"নতুন কুকি পাওয়া গেছে: {new_cookie[:30]}...")

    # M3U ফাইল পড়া
    with open(M3U_FILE_NAME, "r", encoding="utf-8") as f:
        content = f.read()

    # রেগুলার এক্সপ্রেশন দিয়ে আগের কুকি অংশটুকু রিপ্লেস করা (পিপ | এর পরের অংশ)
    # যেমন: |Cookie=Edge-Cache-Cookie=... এই অংশটি নতুন কুকি দিয়ে প্রতিস্থাপিত হবে
    updated_content = re.sub(
        r'\|Cookie=Edge-Cache-Cookie=[^\s#\n]+', 
        f'|Cookie={new_cookie}', 
        content
    )

    # আপডেট করা কন্টেন্ট আবার ফাইলে সেভ করা
    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"সফলভাবে {M3U_FILE_NAME} ফাইলের কুকি আপডেট করা হয়েছে!")

if __name__ == "__main__":
    asyncio.run(update_m3u_cookie())
