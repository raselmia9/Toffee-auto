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
    
    # নিরাপদ কুকি পার্সিং সিস্টেম
    cookies_to_add = []
    try:
        if os.path.exists(COOKIE_FILE_NAME):
            with open(COOKIE_FILE_NAME, "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                
            try:
                raw_data = json.loads(file_content)
                # যদি জেসন ফাইলে সরাসরি কুকিজের লিস্ট থাকে অথবা স্ট্রিং থাকে
                if isinstance(raw_data, list):
                    for c in raw_data:
                        if "name" in c and "value" in c:
                            cookies_to_add.append({
                                "name": c["name"].strip(),
                                "value": c["value"].strip(),
                                "domain": ".toffeelive.com",
                                "path": "/"
                            })
                else:
                    cookie_string = raw_data.get("cookies", "")
                    if cookie_string:
                        for item in cookie_string.split(";"):
                            if "=" in item:
                                parts = item.strip().split("=", 1)
                                if len(parts) == 2:
                                    cookies_to_add.append({
                                        "name": parts[0].strip(),
                                        "value": parts[1].strip(),
                                        "domain": ".toffeelive.com",
                                        "path": "/"
                                    })
            except json.JSONDecodeError:
                execution_logs.append("⚠️ [WARNING]: র-টেক্সট থেকে কুকি রিড করা হচ্ছে...")
                for item in file_content.split(";"):
                    if "=" in item:
                        parts = item.strip().split("=", 1)
                        if len(parts) == 2:
                            cookies_to_add.append({
                                "name": parts[0].strip(),
                                "value": parts[1].strip(),
                                "domain": ".toffeelive.com",
                                "path": "/"
                            })

            login_status_msg = "🎉 [SUCCESS]: প্রিমিয়াম সেশন এবং কুকি সফলভাবে প্রসেস হয়েছে!"
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        if cookies_to_add:
            try:
                await context.add_cookies(cookies_to_add)
                execution_logs.append("🟢 [INFO]: ব্রাউজারে সফলভাবে কুকি ইনজেক্ট করা হয়েছে।")
            except Exception as e:
                execution_logs.append(f"🔴 [ERROR]: ব্রাউজারে কুকি সেট করার সময় ত্রুটি -> {e}")
        
        page = await context.new_page()
        
        # ইমেজ এবং অন্যান্য আনপ্রেডিক্টেড রিসোর্স ব্লক করা যাতে ফাস্ট লোড হয়
        await page.route("**/*", lambda route: route.continue_() if route.request.resource_type not in ["media", "font", "stylesheet"] else route.abort())

        try:
            main_url = "https://toffeelive.com/en/live"
            execution_logs.append(f"🔵 [NAVIGATE]: মূল পেজ লোড হচ্ছে ({main_url})...")
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(6000)

            # পেজ স্ক্রোল করে সব চ্যানেল লোড করা
            previous_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await page.wait_for_timeout(2000)
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    break
                previous_height = current_height

            # সুনির্দিষ্ট সিলেক্টর দিয়ে চ্যানেল কার্ড ও নাম সংগ্রহ করা
            channel_cards = await page.locator("a[href*='/watch/']").all()
            
            seen_links = set()
            for card in channel_cards:
                try:
                    href = await card.get_attribute("href")
                    if href and href not in seen_links:
                        seen_links.add(href)
                        watch_url = href if href.startswith("http") else f"https://toffeelive.com{href}"

                        # সঠিক নাম বের করার উন্নত লজিক
                        name = "Live Channel"
                        try:
                            # কার্ডের ভেতরের হেডিং বা টেক্সট খোঁজা
                            title_elem = card.locator("h3, h4, span, p").first
                            if await title_elem.count() > 0:
                                t_text = await title_elem.inner_text()
                                if t_text and len(t_text.strip()) > 0:
                                    name = t_text.strip()
                            if name == "Live Channel":
                                card_text = await card.inner_text()
                                if card_text:
                                    lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                                    if lines:
                                        name = lines[0]
                        except:
                            pass

                        # লোগো সংগ্রহ
                        logo = "https://assets-prod.services.toffeelive.com/logo.webp"
                        try:
                            img_elem = card.locator("img").first
                            if await img_elem.count() > 0:
                                src = await img_elem.get_attribute("src")
                                if src:
                                    logo = src if src.startswith("http") else f"https://toffeelive.com{src}"
                        except:
                            pass

                        channels_info.append({
                            "channel_name": name,
                            "logo": logo,
                            "watch_url": watch_url
                        })
                except:
                    pass

            msg_total = f"🟢 [INFO]: মোট {len(channels_info)} টি চ্যানেল পাওয়া গেছে। স্ট্রিম লিংক সংগ্রহ শুরু হচ্ছে..."
            execution_logs.append(msg_total)
            print(msg_total)

            final_playlist_data = []
            for item in channels_info:
                stream_link = ""
                try:
                    new_page = await context.new_page()
                    
                    # নেটওয়ার্ক ইন্টারসেপ্ট মেথড
                    def intercept(req):
                        nonlocal stream_link
                        url = req.url
                        if ".m3u8" in url or "manifest" in url:
                            if not stream_link:
                                stream_link = url

                    new_page.on("request", intercept)
                    
                    await new_page.goto(item['watch_url'], timeout=30000)
                    await new_page.wait_for_timeout(5000) 

                    # নতুন কার্যকরী সেকেন্ডারি মেথড: পেজের ফাইনাল রেন্ডার হওয়া সোর্স থেকে সরাসরি এক্সট্রাক্ট করা
                    if not stream_link:
                        execution_logs.append(f"🟡 [FALLBACK START]: নেটওয়ার্কে লিংক মেলেনি ({item['channel_name']}), নতুন সেকেন্ডারি মেথড চেক করা হচ্ছে...")
                        try:
                            new_secondary_stream = await new_page.evaluate("""() => {
                                // পেজের পুরো এইচটিএমএল বা স্ক্রিপ্ট থেকে .m3u8 বা মাস্টার প্লেলিস্ট খোঁজা
                                const html = document.documentElement.innerHTML;
                                const regex = /https?:\\/\\/[^\\s"']+\\.m3u8[^\\s"']*/g;
                                const matches = html.match(regex);
                                if (matches && matches.length > 0) {
                                    return matches[0].replace(/\\\\/g, '');
                                }
                                
                                // যদি ভিডিও সোর্স ট্যাগে সরাসরি থাকে
                                const v = document.querySelector('video');
                                if (v && v.src) return v.src;
                                
                                return "";
                            }""")
                            
                            if new_secondary_stream:
                                stream_link = new_secondary_stream
                                execution_logs.append(f"🟢 [SUCCESS]: সেকেন্ডারি মেথড থেকে লিংক পাওয়া গেছে ({item['channel_name']})!")
                            else:
                                execution_logs.append(f"🔴 [FAILED]: সেকেন্ডারি মেথডও ব্যর্থ হয়েছে ({item['channel_name']})।")
                        except Exception as sec_err:
                            execution_logs.append(f"🔴 [ERROR]: সেকেন্ডারি মেথড এরর ({item['channel_name']}) -> {sec_err}")

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
