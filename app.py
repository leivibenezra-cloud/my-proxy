from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
import re

app = Flask(__name__)

# עיצוב מקצועי ומודרני למובייל
HTML_PAGE = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Secure Proxy</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --primary: #38bdf8; --text: #f1f5f9; }
        body { font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; overflow: hidden; }
        .container { width: 85%; max-width: 400px; padding: 40px 20px; background: var(--card); border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); text-align: center; }
        h1 { font-size: 24px; margin-bottom: 8px; color: var(--primary); }
        p { font-size: 14px; color: #94a3b8; margin-bottom: 30px; }
        input { width: 100%; padding: 16px; margin-bottom: 20px; border-radius: 12px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 16px; box-sizing: border-box; outline: none; transition: 0.3s; }
        input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }
        button { width: 100%; padding: 16px; border-radius: 12px; border: none; background: var(--primary); color: #0f172a; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:active { transform: scale(0.98); }
        .secure-tag { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: #22c55e; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>גלישה מאובטחת</h1>
        <p>ה-IP שלך מוסתר כעת</p>
        <form action="/proxy" method="get">
            <input type="text" name="url" placeholder="הכנס כתובת אתר..." required autocomplete="off">
            <button type="submit">התחל גלישה</button>
        </form>
        <div class="secure-tag">● חיבור מוצפן פעיל</div>
    </div>
</body>
</html>
"""

def rewrite_html(content, base_url):
    """פונקציה חכמה לשכתוב כל הקישורים והמדיה באתר"""
    soup = BeautifulSoup(content, "lxml") # lxml מהיר יותר מ-html.parser
    
    for tag in soup.find_all(['a', 'img', 'script', 'link', 'form', 'iframe']):
        attrs = ['href', 'src', 'action']
        for attr in attrs:
            if tag.has_attr(attr):
                old_url = tag[attr]
                if old_url.startswith('javascript:') or old_url.startswith('#'):
                    continue
                # הפיכת כתובת יחסית למלאה ושכתוב לפרוקסי
                full_url = urljoin(base_url, old_url)
                tag[attr] = f"/proxy?{urlencode({'url': full_url})}"
    
    return soup.encode()

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url: return "URL missing", 400
    if not url.startswith('http'): url = 'https://' + url

    # תעודת זהות של אייפון מודרני לקבלת אתרים מהירים
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        # שימוש ב-Session לניהול חיבורים מהיר יותר
        with requests.Session() as session:
            resp = session.get(url, headers=headers, stream=True, timeout=15, allow_redirects=True)
            
            content_type = resp.headers.get("Content-Type", "")

            # אם זה דף אינטרנט - נשכתב אותו
            if "text/html" in content_type:
                return Response(rewrite_html(resp.text, url), resp.status_code)

            # אם זה קובץ מדיה (תמונה/וידאו) - נזרים אותו בסטרימינג
            def stream_response():
                for chunk in resp.iter_content(chunk_size=8192):
                    yield chunk

            # העברת כותרות חשובות מהמקור (סוג קובץ וכו')
            res_headers = {k: v for k, v in resp.headers.items() if k.lower() not in ['content-encoding', 'transfer-encoding']}
            return Response(stream_response(), resp.status_code, res_headers)

    except Exception as e:
        return f"<div style='text-align:center; padding:50px; font-family:sans-serif;'><h2>שגיאה בגישה לאתר</h2><p>{str(e)}</p></div>", 500

if __name__ == '__main__':
    # הרצה בפורט של Render
    app.run(host='0.0.0.0', port=10000)