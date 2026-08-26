import os
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

async def generate_proper_playlist():
    print("টফি সাইট থেকে চ্যানেলগুলোর তালিকা সংগ্রহ করা হচ্ছে...")
    
    channels_info = []
    global_cookie = ""
    
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

            print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। এবার প্রতিটি চ্যানেলের পেজ ভিজিট করে স্ট্রিম লিংক ও কুকি সংগ্রহ করা হচ্ছে...")

            # প্রতিটি চ্যানেলের ওয়াচ পেজে প্রবেশ করে রিয়েল স্ট্রিম লিংক ও কুকি বের করা
            final_playlist_data = []
            for idx, item in enumerate(channels_info):
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
                    await new_page.goto(item['watch_url'], timeout=30000)
                    await new_page.wait_for_timeout(5000) # পেজ লোড ও ভিডিও ট্রিগার হওয়ার সময়
                    await new_page.close()
                except Exception as e:
                    print(f"লিংক সংগ্রহে সমস্যা ({item['channel_name']}):", e)

                # যদি আসল স্ট্রিম লিংক না পাওয়া যায়, তবে ওয়াচ ইউআরএল ব্যাকআপ হিসেবে থাকবে
                final_stream = stream_link if stream_link else item['watch_url']
                
                final_playlist_data.append({
                    "channel_name": item['channel_name'],
                    "logo": item['logo'],
                    "stream_link": final_stream
                })
                print(f"[{idx+1}/{len(channels_info)}] প্রসেস সম্পন্ন: {item['channel_name']}")

            # ব্রাউজার কুকি সংগ্রহ করা
            cookies = await context.cookies()
            for cookie in cookies:
                if cookie["name"] == "Edge-Cache-Cookie":
                    global_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                    break

        except Exception as e:
            print("মূল ব্রাউজার ত্রুটি:", e)
        finally:
            await browser.close()

    if not global_cookie:
        print("❌ দুঃখিত, কোনো কুকি পাওয়া যায়নি।")
        return

    print(f"✅ কুকি সফলভাবে পাওয়া গেছে এবং ফাইল তৈরি করা হচ্ছে...")

    # VLC ফরম্যাট অনুযায়ী M3U ফাইল তৈরি করা যেখানে নিচে #EXTVLCOPT ট্যাগ থাকবে
    m3u_content = "#EXTM3U\n"
    for item in final_playlist_data:
        m3u_content += f'\n#EXTINF:-1 tvg-logo="{item["logo"]}" group-title="Toffee Live", {item["channel_name"]}\n'
        m3u_content += f"#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n"
        m3u_content += f"#EXTVLCOPT:Cookie={global_cookie}\n"
        m3u_content += f"{item['stream_link']}\n"

    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"🎉 সফলভাবে নতুন M3U প্লেলিস্ট ফাইল তৈরি এবং কুকি `#EXTVLCOPT` ট্যাগের মাধ্যমে যুক্ত করা হয়েছে!")

if __name__ == "__main__":
    asyncio.run(generate_proper_playlist())
