import os
import re
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def generate_and_update_playlist():
    print("টফি সাইট থেকে চ্যানেলগুলোর লিংক, লোগো ও কুকি সংগ্রহ করা হচ্ছে...")
    
    channels_info = []
    edge_cookie = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            main_url = "https://toffeelive.com/en/live"
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(8000)

            # পেজ স্ক্রল করে সব চ্যানেল লোড করা
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2);")
            await page.wait_for_timeout(4000)

            channel_cards = await page.locator("a[href*='/watch/']").all()
            
            seen_links = set()
            for card in channel_cards:
                href = await card.get_attribute("href")
                if href and href not in seen_links:
                    seen_links.add(href)
                    watch_url = href if href.startswith("http") else f"https://toffeelive.com{href}"

                    name = "Live Channel"
                    logo = "https://assets-prod.services.toffeelive.com/logo.webp"
                    
                    try:
                        text_content = await card.inner_text()
                        if text_content and len(text_content.strip()) > 0:
                            name = text_content.strip().split('\n')[0]
                    except:
                        pass

                    try:
                        img_elem = card.locator("img").first
                        if await img_elem.count() > 0:
                            logo = await img_elem.get_attribute("src")
                    except:
                        pass

                    channels_info.append({
                        "channel_name": name.strip(),
                        "logo": logo.strip(),
                        "watch_url": watch_url
                    })

            # কুকি সংগ্রহ করা
            cookies = await context.cookies()
            for cookie in cookies:
                if cookie["name"] == "Edge-Cache-Cookie":
                    edge_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                    break

        except Exception as e:
            print("ত্রুটি:", e)
        finally:
            await browser.close()

    if not edge_cookie:
        print("নতুন কুকি পাওয়া যায়নি।")
        return

    print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে।")

    # যদি ফাইল আগে থেকে না থাকে, তবে একদম নতুন ফুল প্লেলিস্ট তৈরি করবে
    if not os.path.exists(M3U_FILE_NAME):
        print("নতুন M3U ফাইল তৈরি করা হচ্ছে...")
        m3u_content = "#EXTM3U\n"
        for item in channels_info:
            cookie_str = f"|Cookie={edge_cookie}" if edge_cookie else ""
            m3u_content += f'\n#EXTINF:-1 tvg-logo="{item["logo"]}" group-title="Toffee Live", {item["channel_name"]}\n'
            m3u_content += f"{item['watch_url']}{cookie_str}\n"

        with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print("নতুন প্লেলিস্ট সফলভাবে তৈরি হয়েছে!")

    else:
        # ফাইল যদি আগে থাকে, তবে চ্যানেল ঠিক রেখে শুধু কুকি আপডেট বা যুক্ত করবে
        print("বিদ্যমান ফাইল পাওয়া গেছে, কুকি আপডেট/যুক্ত করা হচ্ছে...")
        with open(M3U_FILE_NAME, "r", encoding="utf-8") as f:
            content = f.read()

        # যদি ফাইলে আগে থেকেই কুকি ফরম্যাট থাকে, তবে রিমুভ করে নতুন কুকি বসাবে
        if "Edge-Cache-Cookie=" in content:
            updated_content = re.sub(
                r'\|Cookie=Edge-Cache-Cookie=[^\s#\n]+', 
                f'|Cookie={edge_cookie}', 
                content
            )
        else:
            # কুকি না থাকলে লিংকের শেষে যুক্ত করে দেবে
            lines = content.splitlines()
            updated_lines = []
            for line in lines:
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    base_link = line_str.split("|")[0]
                    updated_lines.append(f"{base_link}|Cookie={edge_cookie}")
                else:
                    updated_lines.append(line_str)
            updated_content = "\n".join(updated_lines)

        with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("সফলভাবে কুকি আপডেট/যুক্ত করা হয়েছে!")

if __name__ == "__main__":
    asyncio.run(generate_and_update_playlist())
