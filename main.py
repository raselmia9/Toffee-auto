import os
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def update_or_add_cookies():
    if not os.path.exists(M3U_FILE_NAME):
        print(f"ত্রুটি: {M3U_FILE_NAME} ফাইলটি পাওয়া যায়নি!")
        return

    print("টফি সাইটে প্রবেশ করা হচ্ছে এবং পেজ সম্পূর্ণ লোডের জন্য অপেক্ষা করা হচ্ছে...")
    edge_cookie = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # টফির লাইভ পেজে যাওয়া
            await page.goto("https://toffeelive.com/en/live", timeout=60000)
            
            # পেজ ও প্লেয়ার পুরোপুরি লোড হওয়ার জন্য একটু সময় দেওয়া এবং স্ক্রল করা
            print("পেজ স্ক্রল করা হচ্ছে যাতে কুকি ও স্ট্রিম রিকোয়েস্ট ট্রিগার হয়...")
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 500);")
                await page.wait_for_timeout(3000)

            # সর্বোচ্চ ১৫ সেকেন্ড পর্যন্ত বারবার চেক করা যতক্ষণ না Edge-Cache-Cookie পাওয়া যায়
            for attempt in range(5):
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie["name"] == "Edge-Cache-Cookie":
                        edge_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                        break
                if edge_cookie:
                    print(f"সফলভাবে কুকি পাওয়া গেছে! (চেষ্টা নং: {attempt + 1})")
                    break
                else:
                    print(ل쿠키 := f"কুকির জন্য অপেক্ষা করা হচ্ছে... (চেষ্টা {attempt + 1}/5)")
                    await page.wait_for_timeout(4000)

        except Exception as e:
            print("কুকি ফেচ করার সময় ত্রুটি ঘটেছে:", e)
        finally:
            await browser.close()

    if not edge_cookie:
        print("❌ দুঃখিত, পেজ পুরোপুরি লোড হওয়ার পরেও কোনো 'Edge-Cache-Cookie' পাওয়া যায়নি।")
        return

    print(f"✅ নতুন কুকি দিয়ে M3U ফাইল আপডেট করা হচ্ছে...")

    # M3U ফাইল পড়া
    with open(M3U_FILE_NAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    link_count = 0
    
    for line in lines:
        line_str = line.strip()
        # চেক করা হচ্ছে এটি কোনো লিংক কি না
        if line_str and not line_str.startswith("#"):
            link_count += 1
            # যদি আগে থেকে পাইপ (|) থাকে, তবে মূল লিংকটা আলাদা করা
            base_link = line_str.split("|")[0]
            # নতুন কুকি জোড়া লাগানো
            new_line = f"{base_link}|Cookie={edge_cookie}\n"
            updated_lines.append(new_line)
        else:
            updated_lines.append(line)

    # আপডেট করা কন্টেন্ট ফাইলে সেভ করা
    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"সফলভাবে {link_count} টি লিংকের সাথে কুকি যুক্ত ও আপডেট করা হয়েছে!")

if __name__ == "__main__":
    asyncio.run(update_or_add_cookies())
