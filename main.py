import os
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def update_or_add_cookies():
    if not os.path.exists(M3U_FILE_NAME):
        print(f"ত্রুটি: {M3U_FILE_NAME} ফাইলটি পাওয়া যায়নি!")
        return

    print("টফি সাইট থেকে নতুন কুকি সংগ্রহ করা হচ্ছে...")
    edge_cookie = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto("https://toffeelive.com/en/live", timeout=60000)
            await page.wait_for_timeout(8000)

            cookies = await context.cookies()
            for cookie in cookies:
                if cookie["name"] == "Edge-Cache-Cookie":
                    edge_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                    break
        except Exception as e:
            print("কুকি ফেচ করার সময় সমস্যা হয়েছে:", e)
        finally:
            await browser.close()

    if not edge_cookie:
        print("নতুন কোনো কুকি পাওয়া যায়নি, তাই আপডেট বাতিল করা হলো।")
        return

    print("নতুন কুকি সফলভাবে পাওয়া গেছে!")

    # M3U ফাইল পড়া
    with open(M3U_FILE_NAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        line_str = line.strip()
        # যদি লাইনটি একটি স্ট্রিম লিংক হয় (অর্থাৎ # দিয়ে শুরু না হয়)
        if line_str and not line_str.startswith("#"):
            # যদি লিংকে আগে থেকেই পাইপ (|) বা কুকি থাকে, তবে শুধু মূল লিংকটা আলাদা করে নেওয়া
            base_link = line_str.split("|")[0]
            
            # কুকি না থাকলে যুক্ত হবে, আর থাকলে নতুন কুকি দিয়ে আপডেট/প্রতিস্থাপিত হবে
            new_line = f"{base_link}|Cookie={edge_cookie}\n"
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    # আপডেট করা কন্টেন্ট ফাইলে সেভ করা
    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"সফলভাবে {M3U_FILE_NAME} ফাইলের লিংকে কুকি চেক করে আপডেট/যুক্ত করা হয়েছে!")

if __name__ == "__main__":
    asyncio.run(update_or_add_cookies())
