from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>הפרוקסי הפרטי שלי</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
        .container { max-width: 600px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input { padding: 12px; width: 80%; font-size: 16px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>הפרוקסי האנונימי שלי 🕵️‍♂️</h2>
        <form action="/proxy" method="get">
            <input type="text" name="url" placeholder="הכנס כתובת אתר..." required>
            <br>
            <button type="submit">גלוש באנונימיות</button>
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

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers)
        
        # אם זה דף HTML, נשכתב את הקישורים שלו
        if "text/html" in resp.headers.get("Content-Type", ""):
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # עוברים על כל הקישורים (a), התמונות (img) והסקריפטים (script)
            for tag in soup.find_all(['a', 'img', 'script', 'link']):
                attr = 'href' if tag.name in ['a', 'link'] else 'src'
                if tag.has_attr(attr):
                    original_url = tag[attr]
                    # הופכים כתובת יחסית לכתובת מלאה
                    full_url = urljoin(url, original_url)
                    # משכתבים את הכתובת כך שתעבור דרך הפרוקסי שלנו
                    tag[attr] = f"/proxy?{urlencode({'url': full_url})}"
            
            return soup.decode()
        
        return Response(resp.content, resp.status_code, dict(resp.headers))
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)