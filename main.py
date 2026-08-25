import os
import re
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def generate_or_update_playlist():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        main_url = "https://toffeelive.com/en/live"
        print("টফির মূল পেজ লোড হচ্ছে...")
        
        channels_info = []
        try:
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(8000)

            # পেজ একটু স্ক্রল করা যাতে সব চ্যানেল লোড হয়
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

            print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। স্ট্রিম লিংক ও কুকি সংগ্রহ করা হচ্ছে...\n")
        except Exception as e:
            print("ত্রুটি:", e)
            await browser.close()
            return

        # বর্তমান সেশন থেকে কুকি বের করা
        edge_cookie = ""
        cookies = await context.cookies()
        for cookie in cookies:
            if cookie["name"] == "Edge-Cache-Cookie":
                edge_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                break

        # যদি ফাইলটি আগে থেকে না থাকে, তবে প্রথমবার একদম নতুন ফুল M3U প্লেলিস্ট তৈরি করবে
        if not os.path.exists(M3U_FILE_NAME):
            print("Toffee_Auto_Update.m3u ফাইলটি পাওয়া যায়নি। প্রথমবার নতুন প্লেলিস্ট তৈরি করা হচ্ছে...")
            
            m3u_content = "#EXTM3U\n"
            for item in channels_info:
                stream_link = ""
                try:
                    new_page = await context.new_page()
                    # রিকোয়েস্ট ইন্টারসেপ্ট করে .m3u8 বা প্লেলিস্ট লিংক খোঁজা
                    def intercept(req):
                        nonlocal stream_link
                        url = req.url
                        if ".m3u8" in url or "playlist" in url or "manifest" in url:
                            stream_link = url

                    new_page.on("request", intercept)
                    await new_page.goto(item['watch_url'], timeout=35000)
                    await new_page.wait_for_timeout(5000)
                    await new_page.close()
                except:
                    pass

                # যদি অটো লিংক না পাওয়া যায়, তবে ওয়াচ লিংক ব্যবহার হবে (যা পরে আপনি ম্যানুয়ালি ঠিক করতে পারবেন)
                final_stream = stream_link if stream_link else item['watch_url']
                cookie_str = f"|Cookie={edge_cookie}" if edge_cookie else ""

                m3u_content += f'\n#EXTINF:-1 tvg-logo="{item["logo"]}" group-title="Toffee Live", {item["channel_name"]}\n'
                m3u_content += f"{final_stream}{cookie_str}\n"

            with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
                f.write(m3u_content)
            
            print("প্রথমবার নতুন প্লেলিস্ট ফাইল সফলভাবে তৈরি হয়েছে!")

        else:
            # ফাইল যদি আগে থেকেই থাকে, তবে শুধু কুকিগুলো আপডেট করবে (আপনার ম্যানুয়াল লিংক ও নাম অক্ষুণ্ণ থাকবে)
            print("ফাইল বিদ্যমান রয়েছে। শুধুমাত্র কুকিগুলো আপডেট করা হচ্ছে...")
            
            with open(M3U_FILE_NAME, "r", encoding="utf-8") as f:
                content = f.read()

            if edge_cookie:
                updated_content = re.sub(
                    r'\|Cookie=Edge-Cache-Cookie=[^\s#\n]+', 
                    f'|Cookie=Edge-Cache-Cookie={edge_cookie.replace("Edge-Cache-Cookie=", "")}', 
                    content
                )
                with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print("সফলভাবে বর্তমান কুকিগুলো আপডেট করা হয়েছে!")
            else:
                print("নতুন কুকি সংগ্রহ করা সম্ভব হয়নি।")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(generate_or_update_playlist())
