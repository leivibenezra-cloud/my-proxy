from flask import Flask, request, Response, render_template_string, stream_with_context
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Proxy Pro</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: white; margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; }
        .container { width: 85%; max-width: 400px; padding: 30px; background: #1e293b; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input { width: 100%; padding: 15px; margin: 20px 0; border-radius: 10px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 15px; border-radius: 10px; border: none; background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>גלישה פרטית 🕵️‍♂️</h2>
        <form action="/proxy" method="get">
            <input type="text" name="url" placeholder="הכנס כתובת אתר..." required>
            <button type="submit">התחל גלישה</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url: return "Missing URL", 400
    if not url.startswith('http'): url = 'https://' + url

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "Range": request.headers.get("Range") # קריטי לסרטונים!
    }

    try:
        # פנייה לאתר המקורי עם תמיכה ב-Stream
        resp = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=20)
        
        # אם זה דף HTML - משכתבים קישורים
        if "text/html" in resp.headers.get("Content-Type", ""):
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup.find_all(['a', 'img', 'script', 'link']):
                attr = 'href' if tag.name in ['a', 'link'] else 'src'
                if tag.has_attr(attr):
                    tag[attr] = f"/proxy?{urlencode({'url': urljoin(url, tag[attr])})}"
            return soup.decode()

        # הזרמת וידאו/קבצים (Streaming)
        def generate():
            for chunk in resp.iter_content(chunk_size=32768): # בלוקים גדולים יותר למהירות
                yield chunk

        # העברת כותרות הוידאו המקוריות (כמו Content-Type ו-Accept-Ranges)
        out_headers = {}
        for h in ['Content-Type', 'Content-Length', 'Accept-Ranges', 'Content-Range']:
            if h in resp.headers:
                out_headers[h] = resp.headers[h]

        return Response(stream_with_context(generate()), resp.status_code, out_headers)

    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)