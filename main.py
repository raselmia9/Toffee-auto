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

    print(f"নতুন কুকি সফলভাবে পাওয়া গেছে: {edge_cookie[:30]}...")

    # M3U ফাইল পড়া
    with open(M3U_FILE_NAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        line_str = line.strip()
        # যদি লাইনটি খালি না হয় এবং # দিয়ে শুরু না হয় (অর্থাৎ এটি একটি লিংক)
        if line_str and not line_str.startswith("#"):
            # যদি লিঙ্কে আগে থেকেই পাইপ (|) থাকে, তবে শুধু মূল লিংক অংশটা আলাদা করে নেওয়া
            base_link = line_str.split("|")[0]
            
            # নতুন কুকি সহ লিংক তৈরি করা
            new_line = f"{base_link}|Cookie={edge_cookie}\n"
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    # আপডেট করা কন্টেন্ট ফাইলে সেভ করা
    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"সফলভাবে {M3U_FILE_NAME} ফাইলের লিংকে কুকি যুক্ত ও আপডেট করা হয়েছে!")

if __name__ == "__main__":
    asyncio.run(update_or_add_cookies())
