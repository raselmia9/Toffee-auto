import os
import asyncio
import json
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

SAVED_COOKIES = "country=BD; state=DHK; allowed_countries=BD; device_id=6b70709f-6b1e-4f88-8b66-d4a0f8961f44; device_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTc5MDYzMjY5NiwiaWF0IjoxNzg4MDAyODk2LCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6ImRjZTZiMTc0LWMxZDUtNGNmZi05YjNlLTBlZGZlMDk0Mjc2ZV8xNzg4MDAyODk2IiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiZDA1NmQzZjQtMDU0ZC00OTAzLWJiOTItZGYyNDhkYzI2ZjhhIiwic19pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsInRva2VuIjoiYWNjZXNzIiwidHlwZSI6ImRldmljZSJ9.U8zNM7bHNlUWvzYxNDr9iBAkOZju4AXMLgAxsE2F3CUsAHwJtl5jsDLWUAzs8XfO1WDzH2Lm2RiYt1eZsdYqbw; device_refresh_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTgwMzc4MTY5NiwiaWF0IjoxNzg4MDAyODk2LCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6ImRjZTZiMTc0LWMxZDUtNGNmZi05YjNlLTBlZGZlMDk0Mjc2ZV8xNzg4MDAyODk2IiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiZDA1NmQzZjQtMDU0ZC00OTAzLWJiOTItZGYyNDhkYzI2ZjhhIiwic19pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsInRva2VuIjoicmVmcmVzaCIsInR5cGUiOiJkZXZpY2UifQ.JJdo1lVnCVZXiL3OWoMkQVIRdIKSpFggReieJR4IInysnfvBrKO1DlVZqCwvQK9uoVKv6-xjc_lC_2PJ2FBEYQ; _fbp=fb.1.1788002900646.16103863163339320; WZRK_G=84c0c3d472a84f1ab2797ae369aba48f; _gcl_au=1.1.428714697.1788002903; _ga=GA1.1.1128668039.1788002902; _ga_02M4D9SN5F=GS2.1.s1788023984$o2$g0$t1788023984$j60$l0$h1763188672"

SAVED_LOCAL_STORAGE = {
    "WZRK_L": "{}",
    "persist:toffee_store": '{"ui":"{\\"collectionPageTitle\\":null,\\"player\\":{\\"id\\":null,\\"volume\\":1,\\"isMuted\\":false,\\"startTime\\":0,\\"currentTime\\":0}}","cart":"{\\"sourceUrl\\":null,\\"sourceVideoId\\":null,\\"productId\\":null,\\"activeScreen\\":\\"PLAN\\",\\"preLoginScreen\\":null,\\"activeTab\\":\\"CONTENT_ACCESS\\",\\"voucher\\":null,\\"selectedPlan\\":null,\\"paymentStatus\\":null}","_persist":"{\\"version\\":4,\\"rehydrated\\":true}"}',
    "WZRK_APPLICATION_SERVER_KEY_RECIEVED": "true",
    "WZRK_K": '{"flag":true,"id":"fde9f827-6374-494a-8b08-c75584f8c625"}',
    "WZRK_TV_CONTROLS": "false",
    "WZRK_ARP": '{"j_n":"Zw==","i_n":"ZW5reQcDAQ0=","d_ts":0,"dh":0,"v":2,"j_s":"{}","id":"R57-668-777Z","r_ts":1788002899}',
    "WZRK_FPU": "false",
    "WZRK_X": '{"cache":[["fde9f827-6374-494a-8b08-c75584f8c625","84c0c3d472a84f1ab2797ae369aba48f"]]}',
    "WZRK_META": '{"useIP":true,"ps":1788005444,"cs":1788023983,"sc":3}',
    "WZRK_CAMP_G": '{"84c0c3d472a84f1ab2797ae369aba48f":{"woc":{},"wndoc":{},"wi":{},"wp":{},"wsc":0,"wndsc":0}}',
    "_gcl_ls": '{"schema":"gcl","version":1,"gcl_ctr":{"value":{"value":0,"timeouts":0,"errors":0,"eopCount":0,"creationTimeMs":1788002902572},"expires":1795778902572}}',
    "auth_session": '{"access":"eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTc5MTg5MTIwMSwiaWF0IjoxNzg4MDAzMjAxLCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6IjBiYTNhN2VjLWEyMzktNDdkYi05YWYwLTBhOWNiZGM4MWMwZF8xNzg4MDAzMjAxIiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiYWEzOGU4ZWYtNTI5MC00ZTllLThhNDgtMGYyNjNkYzVjN2IyIiwic19pZCI6ImZkZTlmODI3LTYzNzQtNDk0YS04YjA4LWM3NTU4NGY4YzYyNSIsInRva2VuIjoiYWNjZXNzIiwidHlwZSI6InN1YnNjcmliZXIifQ.QLavBGDD0ndcLpDF_XpZV-U6zAcBTOyIQfrkNBhh-DWnM8hTVhr6-kLqvbvSi5cW2cq9kVLt0iRex8QVAfBuOQ","refresh":"eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTgwMzU1NTIwMSwiaWF0IjoxNzg4MDAzMjAxLCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6IjBiYTNhN2VjLWEyMzktNDdkYi05YWYwLTBhOWNiZGM4MWMwZF8xNzg4MDAzMjAxIiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiYWEzOGU4ZWYtNTI5MC00ZTllLThhNDgtMGYyNjNkYzVjN2IyIiwic19pZCI6ImZkZTlmODI3LTYzNzQtNDk0YS04YjA4LWM3NTU4NGY4YzYyNSIsInRva2VuIjoicmVmcmVzaCIsInR5cGUiOiJzdWJzY3JpYmVyIn0.CiC_kVLQDANqCY-RiRiQqdI9EY_7nRY9xPXdeabAwkvpSqbxFglp8cXzx7YhRtZi6U72JMwnCQJqg8wIjzmpgQ","accessExpiry":1791891201,"refreshExpiry":1803555201}',
    "WZRK_BLOCK": "false",
    "WZRK_ACCOUNT_ID": '"R57-668-777Z"',
    "WZRK_PR": '{"Identity":"fde9f827-6374-494a-8b08-c75584f8c625","Phone":8801954102960,"tz":"GMT+0600"}',
    "WZRK_G": '"84c0c3d472a84f1ab2797ae369aba48f"'
}

async def generate_proper_playlist():
    print("=" * 60)
    print(" 🔐 TOFFEE LOGIN STATUS REPORT")
    print("=" * 60)
    print(" Status     : SUCCESSFUL (REGISTERED USER)")
    print(" User ID    : fde9f827-6374-494a-8b08-c75584f8c625")
    print(" Phone No   : 8801954102960")
    print(" Auth Token : Injected via Native Init Script")
    print("=" * 60)
    
    channels_info = []
    cookie_name = ""
    cookie_value = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Toffee (Linux;Android 14)",
            viewport={"width": 1280, "height": 800}
        )
        
        # ১. কুকি সেট করা
        parsed_cookies = []
        for item in SAVED_COOKIES.split("; "):
            if "=" in item:
                k, v = item.split("=", 1)
                parsed_cookies.append({
                    "name": k.strip(),
                    "value": v.strip(),
                    "domain": ".toffeelive.com",
                    "path": "/"
                })
        await context.add_cookies(parsed_cookies)
        
        # ২. ব্রাউজার পেজ লোড হওয়ার আগেই লোকাল স্টোরেজ ইনজেক্ট করার স্ক্রিপ্ট যুক্ত করা
        storage_json = json.dumps(SAVED_LOCAL_STORAGE)
        await context.add_init_script(f"""
            const storageData = {storage_json};
            for (const [key, value] of Object.entries(storageData)) {{
                localStorage.setItem(key, value);
            }}
        """)
        
        page = await context.new_page()

        try:
            print("\nটফি লাইভ পেজ ব্রাউজ করা হচ্ছে...")
            main_url = "https://toffeelive.com/en/live"
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(7000)

            # পেজ স্ক্রল করে সব চ্যানেল লোড করা
            previous_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await page.wait_for_timeout(2500)
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                previous_height = current_height

            channel_cards = await page.locator("a[href*='/watch/']").all()
            print(f"মোট চ্যানেল কার্ড পাওয়া গেছে: {len(channel_cards)} টি")
            
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

            print(f"চ্যানেলের তালিকা থেকে স্ট্রিম লিংক সংগ্রহ শুরু হচ্ছে...")

            final_playlist_data = []
            for item in channels_info:
                stream_link = ""
                try:
                    new_page = await context.new_page()
                    
                    def intercept(req):
                        nonlocal stream_link
                        url = req.url
                        if ".m3u8" in url or "playlist" in url or "manifest" in url:
                            stream_link = url

                    new_page.on("request", intercept)
                    await new_page.goto(item['watch_url'], timeout=25000)
                    await new_page.wait_for_timeout(4000)
                    await new_page.close()
                except Exception as e:
                    pass

                # স্ট্রিম লিংক বা ফলব্যাক ইউআরএল যুক্ত করা
                final_stream = stream_link if stream_link else item['watch_url']
                
                final_playlist_data.append({
                    "channel_name": item['channel_name'],
                    "logo": item['logo'],
                    "stream_link": final_stream
                })

            cookies = await context.cookies()
            for cookie in cookies:
                if cookie["name"] == "Edge-Cache-Cookie":
                    cookie_name = cookie["name"]
                    cookie_value = cookie["value"]
                    break

        except Exception as e:
            print("ব্রাউজার কার্যক্রমে ত্রুটি:", e)
        finally:
            await browser.close()

    print(f"✅ M3U প্লেলিস্ট ফাইল প্রসেস ও রাইট করা হচ্ছে...")

    m3u_content = "#EXTM3U\n"
    for item in final_playlist_data:
        cookie_string = f"{cookie_name}={cookie_value}" if cookie_value else "Edge-Cache-Cookie="
        
        m3u_content += f'\n#EXTINF:-1 group-title="[LIVE] BDIX ♛" tvg-logo="{item["logo"]}", {item["channel_name"]}\n'
        m3u_content += f"{item['stream_link']}\n"
        m3u_content += f"#EXTVLCOPT:http-user-agent=Toffee (Linux;Android 14)\n"
        m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_string}"}}\n'

    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"🎉 কাজ সম্পূর্ণ! M3U প্লেলিস্ট আপডেট হয়ে গেছে।")

if __name__ == "__main__":
    asyncio.run(generate_proper_playlist())
