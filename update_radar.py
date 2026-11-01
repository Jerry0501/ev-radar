import os
import feedparser
import pandas as pd
from google import genai
from datetime import datetime

# Autoryzacja nowej biblioteki Gemini
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Wczytanie bazy z pliku csv
df = pd.read_csv('zrodla.csv', header=None)
rss_urls = [url for url in df.iloc[:, 0].tolist() if isinstance(url, str) and url.startswith('http')]

# Pobieranie dzisiejszych nagłówków
zebrane_naglowki = []
for url in rss_urls[:40]: 
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            tytul = entry.title.lower()
            if any(slowo in tytul for slowo in ['kona', 'niro', 'greenway', 'ev', 'elektryk']):
                zebrane_naglowki.append(f"- {entry.title}")
    except:
        continue

tekst_do_analizy = "\n".join(zebrane_naglowki)

# Generowanie raportu przez AI
if tekst_do_analizy.strip():
    prompt = f"""Napisz krótki raport na podstawie dzisiejszych nagłówków. 
    Skup się TYLKO na Hyundai Kona (szczególnie 64 kWh 2020), Kia e-Niro (szczególnie 64 kWh 2021) i stacjach GreenWay. 
    Zwróć wynik jako kod HTML (użyj tagów <h2>, <ul>, <li>). Nie dodawaj formatowania Markdown (żadnych znaków ```).
    Nagłówki: {tekst_do_analizy}"""
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    raport_html = response.text.replace("```html", "").replace("```", "")
else:
    raport_html = "<p>Brak nowych wiadomości pasujących do kryteriów w dzisiejszym skanowaniu.</p>"

# Zapisanie gotowej strony WWW
szablon = f"""<!DOCTYPE html><html lang="pl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>EV Radar</title>
<style>body {{ font-family: sans-serif; max-width: 800px; margin: 20px auto; line-height: 1.6; color: #333; }}</style>
</head><body><h1>EV Radar - Dzienny Raport</h1>
<p style="color: #666;">Wygenerowano: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p><hr>
{raport_html}
</body></html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(szablon)
