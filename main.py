from datetime import datetime

import requests
import time
import json
from telegram import Bot

KUFAR_URL = 'https://api.kufar.by/search-api/v2/search/rendered-paginated?cat=1010&cur=USD&gtsy=country-belarus~province-grodnenskaja_oblast~locality-grodno&lang=ru&rms=v.or%3A2&size=30&typ=let'
BOT_TOKEN = '7771477869:AAGwIsKy8-RFhfN2-RDlpBNHZRfzjvVXqoc'
CHAT_ID = '626693491'
SENT_ADS_FILE = 'sent_ads.json'

bot = Bot(token=BOT_TOKEN)

def fetch_kufar_ads():
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(KUFAR_URL, headers=headers)
    return resp.json().get("ads", [])

def load_sent_ids():
    try:
        with open(SENT_ADS_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_sent_ids(sent_ids):
    with open(SENT_ADS_FILE, 'w') as f:
        json.dump(list(sent_ids), f)

def send_new_ads():
    ads = fetch_kufar_ads()
    sent_ids = load_sent_ids()

    for ad in ads:
        ad_id = ad['ad_id']
        if ad_id not in sent_ids:
            title = ad.get('body_short', 'Без описания')
            link = ad['ad_link']
            price = float(ad.get('price_usd', '???')) / 100

            # 🏠 Адрес
            address = next(
                (p['v'] for p in ad.get('account_parameters', []) if p.get('p') == 'address'),
                'Адрес не указан'
            )

            # ⏰ Время публикации
            time_str = ad.get('list_time', '')  # Пример: 2025-06-30T15:32:54Z
            try:
                dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                published = dt.strftime('%d.%m.%Y %H:%M')
            except:
                published = '???'

            msg = (
                f"🏡 {title}\n"
                f"📍 {address}\n"
                f"💰 {price:.2f} USD\n"
                f"🕒 {published}\n"
                f"🔗 {link}"
            )

            #bot.send_message(chat_id=738477952, text=msg)
            bot.send_message(chat_id=626693491, text=msg)

            sent_ids.add(ad_id)

    save_sent_ids(sent_ids)

send_new_ads()

