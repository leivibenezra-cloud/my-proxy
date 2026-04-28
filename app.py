from flask import Flask, request, Response, render_template_string
import requests

app = Flask(__name__)

# עיצוב חדש שמתאים ב-100% לטלפונים (Responsive Design)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>הפרוקסי האנונימי שלי</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #121212; color: white; margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; }
        .container { width: 90%; max-width: 400px; text-align: center; padding: 30px; background: #1e1e1e; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h2 { margin-bottom: 25px; font-weight: 300; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border-radius: 12px; border: 1px solid #333; background: #2a2a2a; color: white; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 15px; border-radius: 12px; border: none; background: #3f51b5; color: white; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #5c6bc0; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h2>גלישה פרטית 🕵️‍♂️</h2>
        <form action="/proxy" method="get">
            <input type="text" name="url" placeholder="הכנס כתובת אתר (למשל google.com)" required>
            <button type="submit">התחל גלישה</button>
        </form>
        <div class="footer">החיבור מוצפן דרך השרת הפרטי שלך</div>
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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }

    try:
        # stream=True מאפשר לסרטונים וקבצים גדולים לעבור בחתיכות קטנות (הרבה יותר מהיר)
        resp = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        # שליחת התוכן ב"סטרימינג" למשתמש
        return Response(resp.iter_content(chunk_size=1024), resp.status_code, headers)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)