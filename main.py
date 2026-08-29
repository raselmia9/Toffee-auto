import os
import json
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"
LOG_FILE_NAME = "login_status_log.txt"

async def write_log(status_message):
    """লগইন স্ট্যাটাস বা সমস্যা একটি আলাদা টেক্সট ফাইলে লেখার জন্য"""
    with open(LOG_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(status_message)
    print(f"📝 লগ স্ট্যাটাস সেভ হয়েছে: {LOG_FILE_NAME}")

async def generate_proper_playlist():
    print("🔐 আপনার লগইন সেশন এবং কুকিজ ব্রাউজারে ইনজেক্ট করা হচ্ছে...")
    
    channels_info = []
    cookie_name = "Edge-Cache-Cookie"
    cookie_value = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Toffee (Linux;Android 14)",
            viewport={"width": 1280, "height": 800}
        )
        
        # ১. কুকিজ ইনজেক্ট করা
        raw_cookies = "country=BD; state=DHK; allowed_countries=BD; device_id=6b70709f-6b1e-4f88-8b66-d4a0f8961f44; device_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTc5MDYzMjY5NiwiaWF0IjoxNzg4MDAyODk2LCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6ImRjZTZiMTc0LWMxZDUtNGNmZi05YjNlLTBlZGZlMDk0Mjc2ZV8xNzg4MDAyODk2IiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiZDA1NmQzZjQtMDU0ZC00OTAzLWJiOTItZGYyNDhkYzI2ZjhhIiwic19pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsInRva2VuIjoiYWNjZXNzIiwidHlwZSI6ImRldmljZSJ9.U8zNM7bHNlUWvzYxNDr9iBAkOZju4AXMLgAxsE2F3CUsAHwJtl5jsDLWUAzs8XfO1WDzH2Lm2RiYt1eZsdYqbw; device_refresh_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTgwMzc4MTY5NiwiaWF0IjoxNzg4MDAyODk2LCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6ImRjZTZiMTc0LWMxZDUtNGNmZi05YjNlLTBlZGZlMDk0Mjc2ZV8xNzg4MDAyODk2IiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiZDA1NmQzZjQtMDU0ZC00OTAzLWJiOTItZGYyNDhkYzI2ZjhhIiwic19pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsInRva2VuIjoicmVmcmVzaCIsInR5cGUiOiJkZXZpY2UifQ.JJdo1lVnCVZXiL3OWoMkQVIRdIKSpFggReieJR4IInysnfvBrKO1DlVZqCwvQK9uoVKv6-xjc_lC_2PJ2FBEYQ; _fbp=fb.1.1788002900646.16103863163339320; WZRK_G=84c0c3d472a84f1ab2797ae369aba48f; _gcl_au=1.1.428714697.1788002903; _ga=GA1.1.1128668039.1788002902; mp_6019860d585d6c9cc82edba9d456e36c_mixpanel=%7B%22distinct_id%22%3A%22fde9f827-6374-494a-8b08-c75584f8c625%22%2C%22%24device_id%22%3A%224ea986bc-3b4f-4285-beea-044f3d3ae6b9%22%2C%22%24initial_referrer%22%3A%22%24direct%22%2C%22%24initial_referring_domain%22%3A%22%24direct%22%2C%22__mps%22%3A%7B%7D%2C%22__mpso%22%3A%7B%22%24initial_referrer%22%3A%22%24direct%22%2C%22%24initial_referring_domain%22%3A%22%24direct%22%7D%2C%22__mpus%22%3A%7B%7D%2C%22__mpa%22%3A%7B%7D%2C%22__mpu%22%3A%7B%7D%2C%22__mpr%22%3A%5B%5D%2C%22__mpap%22%3A%5B%5D%2C%22%24user_id%22%3A%22fde9f827-6374-494a-8b08-c75584f8c625%22%7D; WZRK_S_R57-668-777Z=%7B%22p%22%3A1%2C%22s%22%3A1788005444%2C%22t%22%3A1788005446%7D; _ga_02M4D9SN5F=GS2.1.s1788002902$o1$g1$t1788005446$j60$l0$h540491668"
        cookie_list = []
        for item in raw_cookies.split("; "):
            if "=" in item:
                parts = item.split("=", 1)
                cookie_list.append({
                    "name": parts[0],
                    "value": parts[1],
                    "domain": "toffeelive.com",
                    "path": "/"
                })
        await context.add_cookies(cookie_list)
        
        page = await context.new_page()
        
        # ২. লোকাল স্টোরেজ সেট আপ
        await page.goto("https://toffeelive.com/en", timeout=60000)
        
        local_storage_data = {
            "WZRK_L": "{}",
            "persist:toffee_store": "{\"ui\":\"{\\\"collectionPageTitle\\\":null,\\\"player\\\":{\\\"id\\\":null,\\\"volume\\\":1,\\\"isMuted\\\":false,\\\"startTime\\\":0,\\\"currentTime\\\":0}}\",\"cart\":\"{\\\"sourceUrl\\\":null,\\\"sourceVideoId\\\":null,\\\"productId\\\":null,\\\"activeScreen\\\":\\\"PLAN\\\",\\\"preLoginScreen\\\":null,\\\"activeTab\\\":\\\"CONTENT_ACCESS\\\",\\\"voucher\\\":null,\\\"selectedPlan\\\":null,\\\"paymentStatus\\\":null}\",\"_persist\":\"{\\\"version\\\":4,\\\"rehydrated\\\":true}\"}",
            "WZRK_APPLICATION_SERVER_KEY_RECIEVED": "true",
            "WZRK_K": "{\"flag\":true,\"id\":\"fde9f827-6374-494a-8b08-c75584f8c625\"}",
            "WZRK_TV_CONTROLS": "false",
            "WZRK_ARP": "{\"j_n\":\"Zw==\",\"i_n\":\"ZW5reQcDAQ0=\",\"d_ts\":0,\"dh\":0,\"v\":2,\"j_s\":\"{}\",\"id\":\"R57-668-777Z\",\"r_ts\":1788002899}",
            "WZRK_FPU": "false",
            "WZRK_X": "{\"cache\":[[\"fde9f827-6374-494a-8b08-c75584f8c625\",\"84c0c3d472a84f1ab2797ae369aba48f\"]]}",
            "WZRK_META": "{\"useIP\":true,\"ps\":1788002899,\"cs\":1788005444,\"sc\":2}",
            "WZRK_CAMP_G": "{\"84c0c3d472a84f1ab2797ae369aba48f\":{\"woc\":{},\"wndoc\":{},\"wi\":{},\"wp\":{},\"wsc\":0,\"wndsc\":0}}",
            "_gcl_ls": "{\"schema\":\"gcl\",\"version\":1,\"gcl_ctr\":{\"value\":{\"value\":0,\"timeouts\":0,\"errors\":0,\"eopCount\":0,\"creationTimeMs\":1788002902572},\"expires\":1795778902572}}",
            "auth_session": "{\"access\":\"eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTc5MTg5MTIwMSwiaWF0IjoxNzg4MDAzMjAxLCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6IjBiYTNhN2VjLWEyMzktNDdkYi05YWYwLTBhOWNiZGM4MWMwZF8xNzg4MDAzMjAxIiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiYWEzOGU4ZWYtNTI5MC00ZTllLThhNDgtMGYyNjNkYzVjN2IyIiwic19pZCI6ImZkZTlmODI3LTYzNzQtNDk0YS04YjA4LWM3NTU4NGY4YzYyNSIsInRva2VuIjoiYWNjZXNzIiwidHlwZSI6InN1YnNjcmliZXIifQ.QLavBGDD0ndcLpDF_XpZV-U6zAcBTOyIQfrkNBhh-DWnM8hTVhr6-kLqvbvSi5cW2cq9kVLt0iRex8QVAfBuOQ\",\"refresh\":\"eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTgwMzU1NTIwMSwiaWF0IjoxNzg4MDAzMjAxLCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6IjBiYTNhN2VjLWEyMzktNDdkYi05YWYwLTBhOWNiZGM4MWMwZF8xNzg4MDAzMjAxIiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiYWEzOGU4ZWYtNTI5MC00ZTllLThhNDgtMGYyNjNkYzVjN2IyIiwic19pZCI6ImZkZTlmODI3LTYzNzQtNDk0YS04YjA4LWM3NTU4NGY4YzYyNSIsInRva2VuIjoicmVmcmVzaCIsInR5cGUiOiJzdWJzY3JpYmVyIn0.CiC_kVLQDANqCY-RiRiQqdI9EY_7nRY9xPXdeabAwkvpSqbxFglp8cXzx7YhRtZi6U72JMwnCQJqg8wIjzmpgQ\",\"accessExpiry\":1791891201,\"refreshExpiry\":1803555201}",
            "WZRK_EV": "{\"wzrk_fetch\":[2,1788002898,1788005442],\"page_viewed\":[15,1788002899,1788005445],\"login\":[1,1788003200,1788003200],\"content_thumbnail_click\":[1,1788003896,1788003896],\"view_item_list\":[1,1788003899,1788003899]}",
            "lastExternalReferrerTime": "1788005444446",
            "WZRK_BLOCK": "false",
            "WZRK_ACCOUNT_ID": "\"R57-668-777Z\"",
            "lastExternalReferrer": "empty",
            "WZRK_PR": "{\"Identity\":\"fde9f827-6374-494a-8b08-c75584f8c625\",\"Phone\":8801954102960,\"tz\":\"GMT+0600\"}",
            "WZRK_G": "\"84c0c3d472a84f1ab2797ae369aba48f\""
        }

        await page.evaluate("(data) => { for (let k in data) { localStorage.setItem(k, data[k]); } }", local_storage_data)
        
        # ৩. মেইন লাইভ পেজে যাওয়া এবং লগইন স্ট্যাটাস চেক করা
        main_url = "https://toffeelive.com/en/live"
        try:
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(6000)

            # লগইন ভ্যালিডেশন চেক: লোকাল স্টোরেজে auth_session আছে কি না এবং তা সাবস্ক্রাইবার কি না যাচাই
            auth_check = await page.evaluate("() => localStorage.getItem('auth_session')")
            if auth_check and "subscriber" in auth_check:
                log_msg = "SUCCESS: Login Successful! Premium subscription session is active."
                print(f"✅ {log_msg}")
            else:
                log_msg = "WARNING: Session injected, but subscriber status could not be fully verified in LocalStorage."
                print(f"⚠️ {log_msg}")
            
            await write_log(log_msg)

        except Exception as e:
            err_msg = f"ERROR: Failed during login verification or page load. Details: {str(e)}"
            print(f"❌ {err_msg}")
            await write_log(err_msg)
            await browser.close()
            return

        # ৪. চ্যানেল স্ক্যানিং এবং লিংক ক্যাপচার অংশ
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

        print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। স্ট্রিম লিংক ক্যাপচার করা হচ্ছে...")

        final_playlist_data = []
        for item in channels_info:
            stream_link = ""
            try:
                new_page = await context.new_page()
                
                # উন্নত লিংক ইন্টারসেপশন (m3u8, manifest বা mpd লিংক ধরার জন্য)
                def handle_request(req):
                    nonlocal stream_link
                    url = req.url
                    if any(ext in url for ext in [".m3u8", "playlist", "manifest", ".mpd"]):
                        stream_link = url

                new_page.on("request", handle_request)
                await new_page.goto(item['watch_url'], timeout=30000)
                
                try:
                    await new_page.wait_for_selector("video", timeout=8000)
                except:
                    pass
                await new_page.wait_for_timeout(4000)
                await new_page.close()
            except Exception as e:
                print(f"লিংক সংগ্রহে সমস্যা ({item['channel_name']}):", e)

            final_stream = stream_link if stream_link else item['watch_url']
            
            final_playlist_data.append({
                "channel_name": item['channel_name'],
                "logo": item['logo'],
                "stream_link": final_stream
            })

        cookies = await context.cookies()
        for cookie in cookies:
            if cookie["name"] == "Edge-Cache-Cookie":
                cookie_value = cookie["value"]
                break

        await browser.close()

    print(f"✅ M3U ফাইল তৈরি করা হচ্ছে...")

    m3u_content = "#EXTM3U\n"
    for item in final_playlist_data:
        cookie_string = f"{cookie_name}={cookie_value}" if cookie_value else "Edge-Cache-Cookie="
        
        m3u_content += f'\n#EXTINF:-1 group-title="[LIVE] BDIX ♛" tvg-logo="{item["logo"]}", {item["channel_name"]}\n'
        m3u_content += f"{item['stream_link']}\n"
        m3u_content += f"#EXTVLCOPT:http-user-agent=Toffee (Linux;Android 14)\n"
        m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_string}"}}\n'

    with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"🎉 সফলভাবে প্রিমিয়াম চ্যানেলসহ M3U প্লেলিস্ট তৈরি হয়েছে!")

if __name__ == "__main__":
    asyncio.run(generate_proper_playlist())
