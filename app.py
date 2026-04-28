from flask import Flask, request, Response, render_template_string
import requests

app = Flask(__name__)

# דף הבית - העיצוב שתראה כשתפתח את האתר
HTML_PAGE = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>הפרוקסי האנונימי שלי</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background-color: #f4f4f9; }
        .container { max-width: 500px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input { padding: 10px; width: 80%; font-size: 16px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; font-size: 16px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h2>הפרוקסי שלי 🕵️‍♂️</h2>
        <form action="/proxy" method="get">
            <input type="text" name="url" placeholder="הכנס כתובת מלאה (כולל https://)" required>
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
# אם הכתובת לא מתחילה ב-http או https, נוסיף https אוטומטית
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url 
    try:
        resp = requests.get(url, stream=True)
        headers = dict(resp.headers)
        headers.pop('Transfer-Encoding', None)
        headers.pop('Content-Encoding', None)
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)