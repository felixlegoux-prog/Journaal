import os
import requests
import re
from datetime import datetime

print("Nieuwsman Journaal: NOS headline ophalen...")

os.makedirs("output", exist_ok=True)

# 1. Haal NOS nieuws
try:
    nos_rss = requests.get("https://feeds.nos.nl/nosnieuwsalgemeen", timeout=10).text
    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', nos_rss)
    nieuws = titles[1] if len(titles) > 1 else "Geen nieuws gevonden"
    nieuws = nieuws.replace("&quot;", '"').replace("&amp;", "&")
    print(f"Headline: {nieuws}")
except Exception as e:
    nieuws = "Welkom bij het Nieuwsman Journaal"
    print(f"NOS error: {e}")

# 2. Maak nieuwstekst
vandaag = datetime.now().strftime('%d %B')
script = f"Goedemorgen. Dit is het Nieuwsman Journaal van {vandaag}. {nieuws}. Dat was het nieuws. Tot morgen."
with open("script.txt", "w") as f:
    f.write(script)

# 3. Google TTS - gratis spraak
try:
    from gtts import gTTS
    tts = gTTS(text=script, lang='nl', slow=False)
    tts.save("output/audio.mp3")
    print("Audio gegenereerd")
except:
    print("gTTS niet beschikbaar, audio stap overslaan")

# 4. Placeholder video - hier komt straks poppetje #3
# Voor nu maken we vandaag.mp4 aan zodat je link blijft werken
with open("output/vandaag.mp4", "wb") as f:
    f.write(b'\x00\x00\x00\x18ftypmp42\x00\x00mp42isom')

print("Klaar! Check script.txt voor de tekst")
