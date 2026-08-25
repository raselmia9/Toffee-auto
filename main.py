import asyncio
import json
from playwright.async_api import async_playwright

async def generate_accurate_playlist():
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
                    logo = "Logo not found"
                    
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

            print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। লিংক ও কুকি সংগ্রহ করা হচ্ছে...\n")
        except Exception as e:
            print("ত্রুটি:", e)
            await browser.close()
            return

        await browser.close()

    complete_playlist = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for item in channels_info:
            stream_link = ""
            edge_cookie = ""
            
            try:
                new_page = await context.new_page()
                
                def intercept(req):
                    nonlocal stream_link
                    url = req.url
                    if ".m3u8" in url or "playlist" in url or "manifest" in url:
                        stream_link = url

                new_page.on("request", intercept)

                await new_page.goto(item['watch_url'], timeout=45000)
                await new_page.wait_for_timeout(7000)

                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie["name"] == "Edge-Cache-Cookie":
                        edge_cookie = f"Edge-Cache-Cookie={cookie['value']}"
                        break

                await new_page.close()
            except Exception as err:
                pass

            result_item = {
                "logo": item["logo"],
                "channel_name": item["channel_name"],
                "watch_url": item["watch_url"],
                "cookie": edge_cookie,
                "streaming_link": stream_link
            }

            complete_playlist.append(result_item)
            print(f"প্রসেস শেষ: {item['channel_name']}")

        await browser.close()

    # ফাইনাল আউটপুট ফাইল যা গিটহাব অটো কমিট করবে
    with open("toffee_complete_playlist.json", "w", encoding="utf-8") as f:
        json.dump(complete_playlist, f, indent=4, ensure_ascii=False)

    print("\n========== কাজ সফলভাবে সম্পন্ন হয়েছে! ==========")

asyncio.run(generate_accurate_playlist())
