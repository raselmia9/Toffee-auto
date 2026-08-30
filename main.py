import os
import json
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"
STATUS_FILE_NAME = "login_status.txt"
COOKIE_FILE_NAME = "Loging Cookie.json"

async def generate_proper_playlist():
    print("টফি সাইট থেকে চ্যানেলগুলোর তালিকা সংগ্রহ করা হচ্ছে...")
    
    execution_logs = []
    execution_logs.append("╔════════════════════════════════════════════════╗")
    execution_logs.append("║       TOFFEE AUTO PLAYLIST GENERATOR LOGS      ║")
    execution_logs.append("╚════════════════════════════════════════════════╝\n")
    
    channels_info = []
    cookie_name = "Edge-Cache-Cookie"
    cookie_value = ""
    login_status_msg = "❌ [FAILED]: কুকি লোড বা লগইন স্ট্যাটাস চেক করা যায়নি।"
    
    cookies_to_add = []
    try:
        if os.path.exists(COOKIE_FILE_NAME):
            with open(COOKIE_FILE_NAME, "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                
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
                execution_logs.append("⚠️ [WARNING]: জেসন ফরম্যাটে সিনট্যাক্স এরর পাওয়া গেছে, র-টেক্সট থেকে কুকি রিড করা হচ্ছে...")
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
            execution_logs.append(f"🟢 {login_status_msg}")
            print(login_status_msg)
        else:
            msg = f"⚠️ [ERROR]: {COOKIE_FILE_NAME} ফাইলটি পাওয়া যায়নি!"
            execution_logs.append(f"🔴 {msg}")
            print(msg)
            login_status_msg = msg
    except Exception as e:
        err_msg = f"❌ [ERROR]: কুকি পড়তে সমস্যা হয়েছে -> {str(e)}"
        execution_logs.append(f"🔴 {err_msg}")
        print(err_msg)
        login_status_msg = err_msg

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Toffee (Linux;Android 14)",
            viewport={"width": 1280, "height": 800}
        )
        
        if cookies_to_add:
            try:
                await context.add_cookies(cookies_to_add)
                execution_logs.append("🟢 [INFO]: ব্রাউজারে সফলভাবে কুকি ইনজেক্ট করা হয়েছে।")
            except Exception as e:
                execution_logs.append(f"🔴 [ERROR]: ব্রাউজারে কুকি সেট করার সময় ত্রুটি -> {e}")
        
        page = await context.new_page()
        
        await page.route("**/*", lambda route: route.continue_() if route.request.resource_type not in ["image", "media", "font", "stylesheet"] else route.abort())

        try:
            main_url = "https://toffeelive.com/en/live"
            execution_logs.append(f"🔵 [NAVIGATE]: মূল পেজ লোড হচ্ছে ({main_url})...")
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(5000)

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
                            src = await img_elem.get_attribute("src")
                            if src and src.startswith("http"):
                                logo = src
                            elif src:
                                logo = f"https://toffeelive.com{src}"
                        
                        if logo == "https://assets-prod.services.toffeelive.com/logo.webp":
                            bg_style = await card.evaluate("""el => {
                                const img = el.querySelector('img');
                                if (img) return img.currentSrc || img.src;
                                
                                const bg = window.getComputedStyle(el).backgroundImage;
                                if (bg && bg !== 'none') {
                                    const match = bg.match(/url\\(['"]?(.*?)['"]?\\)/);
                                    return match ? match[1] : null;
                                }
                                return null;
                            }""")
                            if bg_style and bg_style.startswith("http"):
                                logo = bg_style
                    except Exception as logo_err:
                        pass

                    channels_info.append({
                        "channel_name": name.strip(),
                        "logo": logo.strip(),
                        "watch_url": watch_url
                    })

            msg_total = f"🟢 [INFO]: মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। প্রিমিয়াম স্ট্রিম লিংক সংগ্রহ শুরু হচ্ছে..."
            execution_logs.append(msg_total)
            print(msg_total)

            final_playlist_data = []
            for item in channels_info:
                stream_link = ""
                try:
                    new_page = await context.new_page()
                    
                    # -------------------------------------------------------------
                    # ১. প্রাইমারি মেথড: নেটওয়ার্ক রিকোয়েস্ট ইন্টারসেপ্ট করা
                    # -------------------------------------------------------------
                    def intercept(req):
                        nonlocal stream_link
                        url = req.url
                        if ".m3u8" in url or "manifest" in url:
                            if not stream_link:
                                stream_link = url

                    new_page.on("request", intercept)
                    
                    await new_page.goto(item['watch_url'], timeout=30000)
                    await new_page.wait_for_timeout(6000) 

                    # -------------------------------------------------------------
                    # ২. সেকেন্ডারি (ফলব্যাক) মেথড: প্রাইমারি ব্যর্থ হলে এটি কাজ করবে
                    # -------------------------------------------------------------
                    if not stream_link:
                        execution_logs.append(f"🟡 [FALLBACK START]: প্রাইমারি মেথডে লিংক মেলেনি ({item['channel_name']}), সেকেন্ডারি অ্যাডভান্সড মেথড শুরু হচ্ছে...")
                        try:
                            # এপিআই রেসপন্স বা স্ক্রিপ্ট বা __NEXT_DATA__ থেকে লিংক খোঁজা
                            secondary_stream = await new_page.evaluate("""() => {
                                // ক. Next.js ডেটা অবজেক্ট চেক করা
                                if (window.__NEXT_DATA__ && window.__NEXT_DATA__.props) {
                                    try {
                                        const strData = JSON.stringify(window.__NEXT_DATA__.props);
                                        const m = strData.match(/https?:\\/\\/[^\\s"']+\\.m3u8[^\\s"']*/);
                                        if (m) return m[0].replace(/\\\\/g, '');
                                    } catch(e) {}
                                }
                                
                                // খ. পেজের সমস্ত স্ক্রিপ্ট ট্যাগ স্ক্যান করা
                                const scripts = document.querySelectorAll('script');
                                for (let s of scripts) {
                                    const txt = s.textContent || s.innerText;
                                    if (txt && txt.includes('.m3u8')) {
                                        const match = txt.match(/https?:\\/\\/[^\\s"']+\\.m3u8[^\\s"']*/);
                                        if (match) return match[0].replace(/\\\\/g, '');
                                    }
                                }
                                
                                // গ. ভিডিও বা সোর্স ট্যাগ চেক করা
                                const video = document.querySelector('video');
                                if (video && video.src && video.src.includes('.m3u8')) return video.src;
                                
                                const source = document.querySelector('source');
                                if (source && source.src && source.src.includes('.m3u8')) return source.src;

                                return "";
                            }""")
                            
                            if secondary_stream:
                                stream_link = secondary_stream
                                execution_logs.append(f"🟢 [SUCCESS]: সেকেন্ডারি ফলব্যাক থেকে সফলভাবে লিংক উদ্ধার করা হয়েছে ({item['channel_name']})!")
                            else:
                                execution_logs.append(f"🔴 [FAILED]: সেকেন্ডারি মেথডও কোনো লিংক খুঁজে পায়নি ({item['channel_name']})।")
                        except Exception as sec_err:
                            execution_logs.append(f"🔴 [ERROR]: সেকেন্ডারি ফলব্যাক এরর ({item['channel_name']}) -> {sec_err}")

                    await new_page.close()
                except Exception as e:
                    execution_logs.append(f"🔴 [ERROR]: লিংক সংগ্রহে সমস্যা ({item['channel_name']}) -> {e}")

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
            err_msg = f"🔴 [CRITICAL ERROR]: মূল ব্রাউজার ত্রুটি -> {e}"
            execution_logs.append(err_msg)
            print(err_msg)
        finally:
            await browser.close()

    execution_logs.append("🟢 [SUCCESS]: M3U ফাইল এবং প্লেলিস্ট সফলভাবে প্রসেস করা হয়েছে!")

    with open(STATUS_FILE_NAME, "w", encoding="utf-8") as sf:
        sf.write("\n".join(execution_logs))

    print(f"✅ M3U ফাইল এবং স্ট্যাটাস রিপোর্ট ফাইল সফলভাবে তৈরি করা হয়েছে!")

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
