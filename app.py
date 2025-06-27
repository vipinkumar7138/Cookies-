from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

# HTML Template (Frontend)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Token Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f2f5; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 150px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; }
        button { background: #1877f2; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        button:hover { background: #166fe5; }
        .result { margin-top: 20px; padding: 15px; background: #f0f2f5; border-radius: 6px; white-space: pre-wrap; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Facebook Token Extractor</h2>
        <p>अपने Facebook Cookies को यहाँ पेस्ट करें:</p>
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="fr=0P9pRH9yNk4iNA5Wu...; xs=38:P4jp5MSqp9tqSA...; c_user=615..."></textarea>
            <button type="submit">टोकन निकालें (Extract Token)</button>
        </form>
        {% if result %}
        <div class="result">
            {% if result.status == "success" %}
                ✅ <strong>Token Extraction Successful</strong><br><br>
                <strong>Access Token:</strong> {{ result.access_token or "Not found" }}<br>
                <strong>DTSG Token:</strong> {{ result.fb_dtsg or "Not found" }}<br><br>
                <strong>Cookies Used:</strong><br>
                <pre>{{ result.cookies }}</pre>
            {% else %}
                ❌ <span class="error">Error: {{ result.message }}</span>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_tokens(cookies):
    try:
        # Parse cookies into a dictionary
        cookie_dict = {}
        for cookie in cookies.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookie_dict[name] = value

        # Extract tokens (simulated logic)
        access_token = None
        fb_dtsg = None

        if 'c_user' in cookie_dict and 'xs' in cookie_dict:
            # Generate a dummy token (replace with actual extraction logic)
            access_token = f"EAAC{cookie_dict['c_user']}|{cookie_dict['xs'].split(':')[1][:10]}"
            fb_dtsg = f"dtsg:{cookie_dict.get('fr', '')[0:10]}"

        return {
            "status": "success",
            "access_token": access_token,
            "fb_dtsg": fb_dtsg,
            "cookies": cookie_dict
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        cookies = request.form.get("cookies", "")
        result = extract_tokens(cookies)
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(debug=True)
