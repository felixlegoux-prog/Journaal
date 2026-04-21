import os
import requests
import re
import base64
import time
from datetime import datetime

print("Nieuwsman Journaal: NOS + Audio + Lipsync...")

os.makedirs("output", exist_ok=True)

# 1. NOS nieuws ophalen
try:
    nos_rss = requests.get("https://feeds.nos.nl/nosnieuwsalgemeen", timeout=10).text
    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', nos_rss)
    nieuws_items = titles[1:4] if len(titles) > 3 else ["Geen nieuws gevonden"]
    nieuws_items = [item.replace("&quot;", '"').replace("&amp;", "&") for item in nieuws_items]
    print(f"Headlines: {len(nieuws_items)}")
except Exception as e:
    nieuws_items = ["Welkom bij het Nieuwsman Journaal"]
    print(f"NOS error: {e}")

# 2. Script maken
vandaag = datetime.now().strftime('%A %d %B')
script = f"Goedemorgen! Dit is het Nieuwsman Journaal van {vandaag}. "
for i, item in enumerate(nieuws_items, 1):
    script += f"Item {i}: {item}. "
script += "Dat was het nieuws. Fijne dag!"

with open("output/script.txt", "w") as f:
    f.write(script)

# 3. Google TTS audio - NU IN OUTPUT MAP
try:
    from gtts import gTTS
    tts = gTTS(text=script, lang='nl', slow=False)
    tts.save("output/audio.mp3")  # <- nu in output/
    print("Audio gemaakt in output/audio.mp3")
except Exception as e:
    print(f"TTS error: {e}")
    # Maak lege audio zodat D-ID niet crasht
    with open("output/audio.mp3", "wb") as f:
        f.write(b'')

# 4. Check of D-ID key bestaat
did_key = os.environ.get("DID_API_KEY")
heeft_poppetje = os.path.exists("poppetje.png")

if did_key and heeft_poppetje:
    print("D-ID key + poppetje gevonden, lipsync starten...")
    try:
        with open("poppetje.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
        
        with open("output/audio.mp3", "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode()
        
        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": f"Basic {did_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "source_url": f"data:image/png;base64,{img_base64}",
            "script": {
                "type": "audio",
                "audio": f"data:audio/mp3;base64,{audio_base64}"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 201:
            talk_id = response.json().get("id")
            print(f"D-ID talk gestart: {talk_id}")
            
            # Wacht op resultaat
            for i in range(36):  # max 6 minuten
                time.sleep(10)
                result = requests.get(f"{url}/{talk_id}", headers=headers).json()
                status = result.get("status")
                print(f"D-ID status: {status}")
                if status == "done":
                    video_url = result.get("result_url")
                    video_data = requests.get(video_url).content
                    with open("output/vandaag.mp4", "wb") as f:
                        f.write(video_data)
                    print("Lipsync video met audio klaar!")
                    break
                elif status == "error":
                    raise Exception(f"D-ID error: {result}")
            else:
                raise Exception("D-ID timeout na 6 min")
        else:
            raise Exception(f"D-ID API error: {response.text}")
            
    except Exception as e:
        print(f"D-ID gefaald: {e}")
        print("Fallback: alleen audio beschikbaar")
        # Als D-ID faalt, kopiëren we audio.mp3 naar vandaag.mp4
        # Dan heb je in elk geval geluid
        with open("output/audio.mp3", "rb") as src:
            with open("output/vandaag.mp4", "wb") as dst:
                dst.write(src.read())
else:
    print("Geen D-ID key of poppetje.png gevonden")
    print("Fallback: alleen audio.mp3 beschikbaar")
    # Zonder D-ID: kopieer audio naar mp4 naam
    with open("output/audio.mp3", "rb") as src:
        with open("output/vandaag.mp4", "wb") as dst:
            dst.write(src.read())

print("Klaar! Check output/ map")
