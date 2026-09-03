import os
import json
import asyncio
from playwright.async_api import async_playwright

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"
STATUS_FILE_NAME = "login_status.txt"
COOKIE_FILE_NAME = "Loging Cookie.json"
PREMIUM_JSON_FILE = "Premium_channel_List.json"

# জেসন ফাইল থেকে প্রিমিয়াম চ্যানেল লিস্ট লোড এবং ডিকশনারি রূপান্তর করার ফাংশন
def load_premium_channels_dict():
    premium_dict = {}
    if os.path.exists(PREMIUM_JSON_FILE):
        try:
            with open(PREMIUM_JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for ch in data:
                    if "name" in ch and "url" in ch:
                        # নামকে ছোট হাতের ও স্পেস ট্রিম করে কি (Key) হিসেবে রাখা হলো যাতে হুবহু মিলে যায়
                        clean_name = ch["name"].strip().lower()
                        premium_dict[clean_name] = ch["url"]
        except Exception as e:
            print(f"⚠️ [WARNING]: প্রিমিয়াম জেসন ফাইল পড়তে সমস্যা হয়েছে -> {e}")
    return premium_dict

async def generate_proper_playlist():
    print("টফি সাইট থেকে চ্যানেলগুলোর তালিকা সংগ্রহ করা হচ্ছে...")
    
    # প্রিমিয়াম চ্যানেলগুলোকে ফাস্ট লুকআপের জন্য ডিকশনারিতে লোড করা হলো
    premium_dict = load_premium_channels_dict()
    
    execution_logs = []
    execution_logs.append("╔════════════════════════════════════════════════╗")
    execution_logs.append("║       TOFFEE AUTO PLAYLIST GENERATOR LOGS      ║")
    execution_logs.append("╚════════════════════════════════════════════════╝\n")
    
    channels_info = []
    final_playlist_data = [] 
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
            except:
                import re
                match = re.search(r'"cookies"\s*:\s*"(.*?)"', file_content)
                cookie_string = match.group(1) if match else ""

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

            login_status_msg = "🎉 [SUCCESS]: প্রিমিয়াম কুকি সফলভাবে লোড হয়েছে!"
            execution_logs.append(f"🟢 {login_status_msg}")
            print(login_status_msg)
        else:
            msg = f"⚠️ [ERROR]: {COOKIE_FILE_NAME} ফাইলটি পাওয়া যায়নি!"
            execution_logs.append(f"🔴 {msg}")
            print(msg)
    except Exception as e:
        err_msg = f"❌ [ERROR]: কুকি পড়তে সমস্যা হয়েছে -> {str(e)}"
        execution_logs.append(f"🔴 {err_msg}")
        print(err_msg)

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
        
        await page.route("**/*", lambda route: route.continue_() if route.request.resource_type not in ["media", "font", "stylesheet"] else route.abort())

        try:
            main_url = "https://toffeelive.com/en/live"
            execution_logs.append(f"🔵 [NAVIGATE]: মূল পেজ লোড হচ্ছে ({main_url})...")
            await page.goto(main_url, timeout=60000)
            await page.wait_for_timeout(6000)

            try:
                for _ in range(8):
                    await page.evaluate("window.scrollBy(0, 800);")
                    await page.evaluate("""
                        document.querySelectorAll('[class*="scroll"], [class*="slider"], [class*="horizontal"]').forEach(el => {
                            el.scrollLeft += 400;
                        });
                    """)
                    await page.wait_for_timeout(1500)
            except:
                pass

            channel_cards = await page.locator("a[href*='/watch/']").all()
            
            seen_links = set()
            for card in channel_cards:
                try:
                    href = await card.get_attribute("href")
                    if href and href not in seen_links:
                        seen_links.add(href)
                        watch_url = href if href.startswith("http") else f"https://toffeelive.com{href}"

                        name = await card.evaluate("""el => {
                            const img = el.querySelector('img');
                            if (img && img.alt && img.alt.trim() !== '') {
                                return img.alt.trim();
                            }
                            const headings = el.querySelectorAll('h3, h4, span, p');
                            for (let h of headings) {
                                const t = h.innerText.trim();
                                if (t.length > 0 && t.length < 40) return t;
                            }
                            const text = el.innerText || el.textContent;
                            if (text) {
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                                if (lines.length > 0) return lines[0];
                            }
                            return "";
                        }""")

                        if not name or "Live Channel" in name or len(name) < 2:
                            continue

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

            msg_total = f"🟢 [INFO]: মোট {len(channels_info)} টি সঠিক চ্যানেল পাওয়া গেছে। স্ট্রিম লিংক সংগ্রহ শুরু হচ্ছে..."
            execution_logs.append(msg_total)
            print(msg_total)

            for item in channels_info:
                final_stream = ""
                channel_key = item['channel_name'].strip().lower()
                
                # সবচেয়ে নিখুঁত ও নিশ্চিত চেক: জেসন ডিকশনারিতে চ্যানেলটি আছে কি না
                if channel_key in premium_dict:
                    final_stream = premium_dict[channel_key]
                    execution_logs.append(f"🔄 [BACKUP]: '{item['channel_name']}' চ্যানেলটি JSON ব্যাকআপ লিস্ট থেকে নেওয়া হয়েছে।")
                else:
                    # সাধারণ চ্যানেলের জন্য সাইট থেকে লিংক খোঁজা হবে
                    stream_link = ""
                    try:
                        new_page = await context.new_page()
                        
                        def intercept(req):
                            nonlocal stream_link
                            url = req.url
                            if ".m3u8" in url or "manifest" in url:
                                if not stream_link:
                                    stream_link = url

                        new_page.on("request", intercept)
                        
                        await new_page.goto(item['watch_url'], timeout=30000)
                        await new_page.wait_for_timeout(4000) 

                        if not stream_link:
                            try:
                                new_secondary_stream = await new_page.evaluate("""() => {
                                    const html = document.documentElement.innerHTML;
                                    const regex = /https?:\\/\\/[^\\s"']+\\.m3u8[^\\s"']*/g;
                                    const matches = html.match(regex);
                                    if (matches && matches.length > 0) {
                                        return matches[0].replace(/\\\\/g, '');
                                    }
                                    const v = document.querySelector('video');
                                    if (v && v.src) return v.src;
                                    return "";
                                }""")
                                
                                if new_secondary_stream:
                                    stream_link = new_secondary_stream
                            except:
                                pass

                        await new_page.close()
                    except Exception as e:
                        pass

                    if stream_link:
                        final_stream = stream_link
                    else:
                        final_stream = item['watch_url']
                        execution_logs.append(f"⚠️ [WARNING]: '{item['channel_name']}' এর কোনো স্ট্রিম লিংক পাওয়া যায়নি, ওয়াচ ইউআরএল বসানো হয়েছে।")
                
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
