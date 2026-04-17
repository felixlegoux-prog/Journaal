import os
import datetime
import requests
from pathlib import Path

# 1. Mapje maken voor output
Path("output").mkdir(exist_ok=True)

# 2. Nieuws ophalen van NOS - pak top 3 headlines
print("Nieuws ophalen...")
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get("https://feeds.nos.nl/nosnieuwsalgemeen", headers=headers)
headlines = []
for line in r.text.split("<item>")[1:4]:
    title = line.split("<title>")[1].split("</title>")[0]
    headlines.append(title.replace("<![CDATA[", "").replace("]]>", ""))

# 3. Script schrijven voor Nieuwsman #3
datum = datetime.datetime.now().strftime("%A %d %B")
script = f"Goedemorgen! Dit is het Nieuwsman Journaal van {datum}. "
script += f"Item 1: {headlines[0]}. "
script += f"Item 2: {headlines[1]}. "
script += f"Item 3: {headlines[2]}. "
script += "Dat was het nieuws. Fijne dag!"

with open("output/script.txt", "w") as f:
    f.write(script)

print("Script klaar:", script)

# 4. Video placeholder - vervangen we straks
print("Video maken...")
with open("output/vandaag.mp4", "wb") as f:
    f.write(b'Placeholder')

print("Klaar! Video staat in output/vandaag.mp4")
