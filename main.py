import os
import json
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"
STATUS_FILE_NAME = "login_status.txt"
COOKIE_FILE_NAME = "Loging Cookie.json"

async def generate_proper_playlist():
    print("টফি সাইট থেকে চ্যানেলগুলোর তালিকা সংগ্রহ করা হচ্ছে...")
    
    channels_info = []
    cookie_name = "Edge-Cache-Cookie"
    cookie_value = ""
    login_status_msg = "❌ [FAILED]: কুকি লোড বা লগইন স্ট্যাটাস চেক করা যায়নি।"
    
    # ফাইল থেকে কুকি এবং সেশন ডাটা পার্স করার নিরাপদ পদ্ধতি
    cookies_to_add = []
    try:
        if os.path.exists(COOKIE_FILE_NAME):
            with open(COOKIE_FILE_NAME, "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                
            # প্রথমে চেষ্টা করা হবে জেসন হিসেবে পার্স করার
            try:
                raw_data = json.loads(file_content)
                cookie_string = raw_data.get("cookies", "")
                if cookie_string:
                    for item in cookie_string.split(";"):
                        if "=" in item:
                            parts = item.strip().split("=", 1)
                            if len(parts) == 2:
                                cookies_to_add.append({
                                    "name": parts[0].strip(),
                                    "value": parts[1].strip(),
                                    "url": "https://toffeelive.com"
                                })
                
                # লোকালস্টোরেজ থেকে auth_session বা সাবস্ক্রিপশন ডাটা যুক্ত করা
                local_storage = raw_data.get("localStorage", {})
                if "auth_session" in local_storage:
                    try:
                        auth_data = json.loads(local_storage["auth_session"])
                        if "access" in auth_data:
                            cookies_to_add.append({
                                "name": "auth_access_token",
                                "value": auth_data["access"],
                                "url": "https://toffeelive.com"
                            })
                    except:
                        pass

            except json.JSONDecodeError:
                # যদি জেসন ফরম্যাটে কোনো সিনট্যাক্স এরর থাকে, তবে র-টেক্সট বা স্ট্রিং হিসেবে কুকি রিড করা হবে
                print("⚠️ জেসন ফরম্যাটে সিনট্যাক্স এরর পাওয়া গেছে, র-টেক্সট থেকে কুকি রিড করা হচ্ছে...")
                for item in file_content.split(";"):
                    if "=" in item:
                        parts = item.strip().split("=", 1)
                        if len(parts) == 2:
                            cookies_to_add.append({
                                "name": parts[0].strip(),
                                "value": parts[1].strip(),
                                "url": "https://toffeelive.com"
                            })

            login_status_msg = "🎉 [SUCCESS]: প্রিমিয়াম সেশন এবং কুকি ফাইল থেকে সফলভাবে লোড হয়েছে!"
            print(login_status_msg)
        else:
            print(f"⚠️ {COOKIE_FILE_NAME} ফাইলটি পাওয়া যায়নি!")
            login_status_msg = f"❌ [ERROR]: {COOKIE_FILE_NAME} ফাইলটি পাওয়া যায়নি।"
    except Exception as e:
        print("❌ কুকি পড়তে সমস্যা হয়েছে:", e)
        login_status_msg = f"❌ [ERROR]: {str(e)}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Toffee (Linux;Android 14)",
            viewport={"width": 1280, "height": 800}
        )
        
        # ব্রাউজারে কুকিগুলো ইনজেক্ট করা
        if cookies_to_add:
            try:
                await context.add_cookies(cookies_to_add)
            except Exception as e:
                print("ব্রাউজারে কুকি সেট করার সময় ত্রুটি:", e)
        
        page = await context.new_page()
        
        # পারফরম্যান্স বাড়ানোর জন্য ছবি, ফন্ট এবং স্টাইলশিট ব্লক করা
        await page.route("**/*", lambda route: route.continue_() if route.request.resource_type not in ["image", "media", "font", "stylesheet"] else route.abort())

        try:
            main_url = "https://toffeelive.com/en/live"
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(5000)

            # পেজের নিচ পর্যন্ত স্ক্রোল করে সব চ্যানেল লোড করা
            previous_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await page.wait_for_timeout(2000)
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                previous_height = current_height

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

            print(f"মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। প্রিমিয়াম স্ট্রিম লিংক সংগ্রহ করা হচ্ছে...")

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
                    await new_page.goto(item['watch_url'], timeout=30000)
                    
                    # প্রিমিয়াম লিংক সঠিকভাবে ধরার জন্য পর্যাপ্ত সময় অপেক্ষা করা
                    await new_page.wait_for_timeout(7000) 
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

    # লগইন স্ট্যাটাস টেক্সট ফাইলে সেভ করা
    with open(STATUS_FILE_NAME, "w", encoding="utf-8") as sf:
        sf.write("Toffee Premium Login Status Report\n")
        sf.write("========================================\n")
        sf.write(f"{login_status_msg}\n")

    print(f"✅ M3U ফাইল এবং লগইন স্ট্যাটাস ফাইল তৈরি করা হচ্ছে...")

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

    print(f"🎉 সফলভাবে প্রিমিয়াম M3U প্লেলিস্ট তৈরি হয়েছে!")

if __name__ == "__main__":
    asyncio.run(generate_proper_playlist())
