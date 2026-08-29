import os
import json
import requests
from bs4 import BeautifulSoup

M3U_FILE_NAME = "Toffee_Auto_Update.m3u"

SAVED_COOKIES = "country=BD; state=DHK; allowed_countries=BD; device_id=6b70709f-6b1e-4f88-8b66-d4a0f8961f44; device_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTc5MDYzMjY5NiwiaWF0IjoxNzg4MDAyODk2LCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6ImRjZTZiMTc0LWMxZDUtNGNmZi05YjNlLTBlZGZlMDk0Mjc2ZV8xNzg4MDAyODk2IiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiZDA1NmQzZjQtMDU0ZC00OTAzLWJiOTItZGYyNDhkYzI2ZjhhIiwic19pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsInRva2VuIjoiYWNjZXNzIiwidHlwZSI6ImRldmljZSJ9.U8zNM7bHNlUWvzYxNDr9iBAkOZju4AXMLgAxsE2F3CUsAHwJtl5jsDLWUAzs8XfO1WDzH2Lm2RiYt1eZsdYqbw; device_refresh_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJodHRwczovL3RvZmZlZWxpdmUuY29tIiwiY291bnRyeSI6IkJEIiwiZF9pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsImV4cCI6MTgwMzc4MTY5NiwiaWF0IjoxNzg4MDAyODk2LCJpc3MiOiJ0b2ZmZWVsaXZlLmNvbSIsImp0aSI6ImRjZTZiMTc0LWMxZDUtNGNmZi05YjNlLTBlZGZlMDk0Mjc2ZV8xNzg4MDAyODk2IiwicHJvdmlkZXIiOiJ0b2ZmZWUiLCJyX2lkIjoiZDA1NmQzZjQtMDU0ZC00OTAzLWJiOTItZGYyNDhkYzI2ZjhhIiwic19pZCI6ImQwNTZkM2Y0LTA1NGQtNDkwMy1iYjkyLWRmMjQ4ZGMyNmY4YSIsInRva2VuIjoicmVmcmVzaCIsInR5cGUiOiJkZXZpY2UifQ.JJdo1lVnCVZXiL3OWoMkQVIRdIKSpFggReieJR4IInysnfvBrKO1DlVZqCwvQK9uoVKv6-xjc_lC_2PJ2FBEYQ; _fbp=fb.1.1788002900646.16103863163339320; WZRK_G=84c0c3d472a84f1ab2797ae369aba48f; _gcl_au=1.1.428714697.1788002903; _ga=GA1.1.1128668039.1788002902; _ga_02M4D9SN5F=GS2.1.s1788023984$o2$g0$t1788023984$j60$l0$h1763188672"

def generate_playlist_via_api():
    print("=" * 60)
    print(" 🚀 TOFFEE DIRECT API & DATA EXTRACTOR")
    print("=" * 60)

    headers = {
        "User-Agent": "Toffee (Linux;Android 14)",
        "Cookie": SAVED_COOKIES,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    url = "https://toffeelive.com/en/live"
    print("📡 টফি সার্ভার থেকে সরাসরি ডেটা ফেচ করা হচ্ছে...")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ সার্ভার থেকের এরর কোড এসেছে: {response.status_code}")
            return

        # BeautifulSoup দিয়ে পেজ পার্স করা
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Next.js এর বিল্ট-ইন জেসন ডেটা ট্যাগ খুঁজে বের করা
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            print("❌ পেজে কোনো নেক্সট ডাটা (Next Data) পাওয়া যায়নি!")
            return

        json_data = json.loads(script_tag.string)
        
        # জেজন স্ট্রাকচার থেকে চ্যানেল লিস্ট খুঁজে বের করার চেষ্টা
        channels_info = []
        try:
            # সাধারণত নেক্সট ডেটার প্রপসের ভেতরে চ্যানেল বা লাইভ কন্টেন্টের ডেটা থাকে
            queries = json_data.get("props", {}).get("pageProps", {})
            
            # ডেটার বিভিন্ন সম্ভাব্য পাথ চেক করা
            items_list = []
            if "initialState" in queries:
                # যদি রিডেক্স বা অন্য স্টেট থাকে
                pass
            
            # বিকল্প হিসেবে পেজের ভেতরের সব হাইপারলিংক বা এঙ্কর ট্যাগ থেকে চ্যানেল সংগ্রহ করা
            links = soup.find_all('a', href=lambda href: href and '/watch/' in href)
            print(f"🔍 মোট {len(links)} টি চ্যানেল লিংক পাওয়া গেছে।")

            seen_links = set()
            for a in links:
                href = a.get('href')
                if href and href not in seen_links:
                    seen_links.add(href)
                    watch_url = href if href.startswith("http") else f"https://toffeelive.com{href}"
                    
                    # চ্যানেলের নাম খোঁজা
                    name = "Live Channel"
                    text = a.get_text(strip=True)
                    if text:
                        name = text.split('\n')[0]
                    
                    # লোগো খোঁজা
                    logo = "https://assets-prod.services.toffeelive.com/logo.webp"
                    img = a.find('img')
                    if img and img.get('src'):
                        logo = img.get('src')

                    channels_info.append({
                        "channel_name": name,
                        "logo": logo,
                        "watch_url": watch_url
                    })

        except Exception as e:
            print("⚠️ ডেটা পার্সিংয়ের সময় সমস্যা হয়েছে:", e)

        if not channels_info:
            print("❌ কোনো চ্যানেল লিস্ট এক্সট্রাক্ট করা সম্ভব হয়নি।")
            return

        print(f"✅ সফলভাবে {len(channels_info)} টি চ্যানেলের তথ্য সংগ্রহ করা হয়েছে। M3U ফাইল তৈরি হচ্ছে...")

        # কুকি থেকে Edge-Cache-Cookie আলাদা করা
        cookie_name = "Edge-Cache-Cookie"
        cookie_value = ""
        for item in SAVED_COOKIES.split("; "):
            if item.startswith("Edge-Cache-Cookie="):
                cookie_value = item.split("=", 1)[1]
                break

        m3u_content = "#EXTM3U\n"
        for item in channels_info:
            cookie_string = f"{cookie_name}={cookie_value}" if cookie_value else "Edge-Cache-Cookie="
            
            m3u_content += f'\n#EXTINF:-1 group-title="[LIVE] BDIX ♛" tvg-logo="{item["logo"]}", {item["channel_name"]}\n'
            m3u_content += f"{item['watch_url']}\n"
            m3u_content += f"#EXTVLCOPT:http-user-agent=Toffee (Linux;Android 14)\n"
            m3u_content += f'#EXTHTTP:{{"cookie":"{cookie_string}"}}\n'

        with open(M3U_FILE_NAME, "w", encoding="utf-8") as f:
            f.write(m3u_content)

        print(f"🎉 কাজ সম্পূর্ণ! '{M3U_FILE_NAME}' সফলভাবে আপডেট হয়ে গেছে।")

    except Exception as e:
        print("❌ এক্সিকিউশনে ত্রুটি দেখা দিয়েছে:", e)

if __name__ == "__main__":
    generate_playlist_via_api()
