import os
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def generate_proper_playlist():
    print("টফি সাইট থেকে চ্যানেলগুলোর তালিকা সংগ্রহ করা হচ্ছে...")
    
    channels_info = []
    cookie_name = ""
    cookie_value = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Toffee (Linux;Android 14)"
        )
        
        # আপনার প্রিমিয়াম অ্যাকাউন্ট বা ডিভাইসের কুকিগুলো ব্রাউজারে ইনজেক্ট করা হচ্ছে
        await context.add_cookies([
            {
                "name": "device_token",
                "value": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6IjcyMzgzZDhkLThhNzctNDRjOS04OGY4LTcyZmE0YTdlMjE5ZiIsImV4cCI6MTc5MDU2NzU2MywiaWF0IjoxNzg3OTM3NzYzLCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6IjRhNzBlNjYwLWY0ODYtNDBjMS1iYzlhLTI5ZGMyZWFjMmJkYl8xNzg3OTM3NzYzIiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiNzIzODNkOGQtOGE3Ny00NGM5LTg4ZjgtNzJmYTRhN2UyMTlmIiwic19pZCI6IjcyMzgzZDhkLThhNzctNDRjOS04OGY4LTcyZmE0YTdlMjE5ZiIsInRva2VuIjoiYWNjZXNzIiwidHlwZSI6ImRldmljZSJ9.1cdEXXUXVaZyrBB-_7Yr2hcbSXHgJ-tCzZBG9tIZMaw7LcItOteaE5KrAN0bI0bh5x44Hv5YapzE4tjEBGhYNQ",
                "domain": "toffeelive.com",
                "path": "/"
            },
            {
                "name": "device_refresh_token",
                "value": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6IjcyMzgzZDhkLThhNzctNDRjOS04OGY4LTcyZmE0YTdlMjE5ZiIsImV4cCI6MTgwMzcxNjU2MywiaWF0IjoxNzg3OTM3NzYzLCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6IjRhNzBlNjYwLWY0ODYtNDBjMS1iYzlhLTI5ZGMyZWFjMmJkYl8xNzg3OTM3NzYzIiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiNzIzODNkOGQtOGE3Ny00NGM5LTg4ZjgtNzJmYTRhN2UyMTlmIiwic19pZCI6IjcyMzgzZDhkLThhNzctNDRjOS04OGY4LTcyZmE0YTdlMjE5ZiIsInRva2VuIjoicmVmcmVzaCIsInR5cGUiOiJkZXZpY2UifQ.fPaIITIowUp9QD0vrmDUMqifG_WA5FUlvBWIeINCQiaFLbixkUDCpeJhuXQ6qMbDNQrZzsesjDS6RqCnFEprOw",
                "domain": "toffeelive.com",
                "path": "/"
            }
        ])
        
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

            print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। স্ট্রিম লিংক ও কুকি সংগ্রহ করা হচ্ছে...")

            final_playlist_data = []
            for idx, item in enumerate(channels_info):
                stream_link = ""
                try:
                    new_page = await context.new_page()
                    
                    def intercept(req):
                        nonlocal stream_link
                        url = req.url
                        if ".m3u8" in url or "playlist" in url or "manifest" in url:
                            stream_link = url

                    new_page.on("request", intercept)
                    await new_page.goto(item['watch_url'], timeout=30000)
                    await new_page.wait_for_timeout(5000)
                    await new_page.close()
                except Exception as e:
                    print(f"লিংক সংগ্রহে সমস্যা ({item['channel_name']}):", e)

                final_stream = stream_link if stream_link else item['watch_url']
                
                final_playlist_data.append({
                    "channel_name": item['channel_name'],
                    "logo": item['logo'],
                    "stream_link": final_stream
                })

            # ব্রাউজার থেকে Edge-Cache-Cookie সংগ্রহ করা
            cookies = await context.cookies()
            for cookie in cookies:
                if cookie["name"] == "Edge-Cache-Cookie":
                    cookie_name = cookie["name"]
                    cookie_value = cookie["value"]
                    break

        except Exception as e:
            print("মূল ব্রাউজার ত্রুটি:", e)
        finally:
            await browser.close()

    if not cookie_value:
        print("⚠️ সতর্কবার্তা: সরাসরি Edge-Cache-Cookie পাওয়া যায়নি, তবে ডিভাইস টোকেন দিয়ে ফাইল তৈরি করা হচ্ছে...")

    print(f"✅ ফাইল তৈরি করা হচ্ছে...")

    # M3U ফাইল তৈরি করা
    m3u_content = "#EXTM3U\n"
    for item in final_playlist_data:
        cookie_string = f"{cookie_name}={cookie_value}" if cookie_value else "Edge-Cache-Cookie="
        
        m3u_content += f'\n#EXTINF:-1 group-title="[LIVE] BDIX ♛" tvg-logo="{item["logo"]}", {item["channel_name"]}\n'
        m3u_content += f"{item['stream_link']}\n"
        m3u_content += f"#EXTVLCOPT:http-user-agent=Toffee (Linux;Android 14)\n"
        m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_string}"}}\n'

    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"🎉 সফলভাবে M3U প্লেলিস্ট তৈরি হয়েছে!")

if __name__ == "__main__":
    asyncio.run(generate_proper_playlist())
