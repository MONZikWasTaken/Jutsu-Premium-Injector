from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import hashlib
import time

app = Flask(__name__)
CORS(app)

API_SECRET = "WellCodedJUTSUFREE"

COOKIES = {
    "_ym_uid": "your things",
    "_ym_d": "your things",
    "cf_clearance": "your things",
    "dle_user_id": "your things",
    "dle_password": "your things",
    "PHPSESSID": "your things"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Referer": "https://jut.su/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def verify_api_key(api_key):
    """Проверяем API ключ"""
    return api_key == API_SECRET

def extract_video_from_html(html):
    """Извлекаем видео ссылку из HTML (твоя логика)"""
    video_patterns = [
        r'https?://r\d+\.yandexwebcache\.org/[^"\'>\s]+\.mp4[^"\'>\s]*',
        r'https?://[^"\'>\s]*yandex[^"\'>\s]*\.mp4[^"\'>\s]*',
        r'https?://[^"\'>\s]+\.mp4\?hash=[^"\'>\s]+',
        r'"(https?://[^"]+\.mp4[^"]*)"',
        r"'(https?://[^']+\.mp4[^']*)'"
    ]

    for pattern in video_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"Найдено {len(matches)} видео ссылок")

            for match in matches:
                url = match.strip('"\'')
                if "1080" in url and url.startswith('http'):
                    print(f"Найдена 1080p ссылка: {url}")
                    return url

            if matches:
                url = matches[0].strip('"\'')
                if url.startswith('http'):
                    print(f"Найдена ссылка: {url}")
                    return url

    js_patterns = [
        r'src[\s]*:[\s]*["\'](https?://[^"\']+\.mp4[^"\']*)',
        r'video[\s]*:[\s]*["\'](https?://[^"\']+\.mp4[^"\']*)',
        r'url[\s]*:[\s]*["\'](https?://[^"\']+\.mp4[^"\']*)'
    ]

    for pattern in js_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            for match in matches:
                if match.startswith('http'):
                    print(f"Найдена ссылка в JS: {match}")
                    return match

    return None

@app.route('/api/extract', methods=['POST'])
def extract_video():
    try:
        data = request.get_json()

        api_key = data.get('api_key')
        if not verify_api_key(api_key):
            return jsonify({'success': False, 'error': 'Неверный API ключ'}), 401

        episode_url = data.get('url')
        if not episode_url or not episode_url.startswith('https://jut.su/'):
            return jsonify({'success': False, 'error': 'Неверный URL'}), 400

        print(f"Обрабатываю: {episode_url}")

        response = requests.get(episode_url, headers=HEADERS, cookies=COOKIES, timeout=30)

        if response.status_code != 200:
            return jsonify({
                'success': False, 
                'error': f'Ошибка загрузки страницы: {response.status_code}'
            }), 400

        print("Страница загружена, ищу видео...")
        html = response.text

        video_url = extract_video_from_html(html)

        if video_url:
            print(f"✅ Ссылка найдена: {video_url}")
            return jsonify({'success': True, 'video_url': video_url})
        else:
            if any(word in html.lower() for word in ['premium', 'подписка', 'jutsu+']):
                error_msg = 'Требуется premium подписка'
            else:
                error_msg = 'Видео не найдено'

            return jsonify({'success': False, 'error': error_msg}), 404

    except requests.RequestException as e:
        return jsonify({'success': False, 'error': f'Ошибка сети: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Сервер работает'})

if __name__ == '__main__':
    print("🚀 Jut.su Video Extractor Server запущен!")
    print("🔑 Не забудь изменить API_SECRET в коде!")
    app.run(host='0.0.0.0', port=8080, debug=False)