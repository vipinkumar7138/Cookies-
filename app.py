import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML टेम्प्लेट (सीधे Python कोड में)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>फेसबुक टोकन एक्सट्रैक्टर</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
               max-width: 700px; margin: 0 auto; padding: 20px; 
               background-color: #f5f5f5; }
        .container { background: white; padding: 25px; border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1877f2; text-align: center; }
        .btn { background: #1877f2; color: white; border: none; 
               padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #166fe5; }
        .result-box { margin-top: 20px; padding: 15px; 
                     border: 1px solid #ddd; border-radius: 5px; }
        .warning { color: #ff0000; font-weight: bold; }
        .instructions { margin-top: 30px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>फेसबुक टोकन एक्सट्रैक्टर</h1>
        
        <form method="post" enctype="multipart/form-data">
            <p><strong>कुकी फाइल अपलोड करें (cookies.txt):</strong></p>
            <input type="file" name="cookie_file" accept=".txt" required>
            <br><br>
            <button type="submit" class="btn">टोकन निकालें</button>
        </form>

        {% if token %}
        <div class="result-box">
            <h3>निकाले गए टोकन:</h3>
            <p><strong>c_user ID:</strong> {{ token.c_user }}</p>
            <p><strong>xs टोकन:</strong> {{ token.xs }}</p>
            <p class="warning">⚠️ चेतावनी: इन टोकन को किसी के साथ शेयर न करें!</p>
        </div>
        {% endif %}

        <div class="instructions">
            <h3>कुकी फाइल कैसे प्राप्त करें?</h3>
            <ol>
                <li>Chrome में <code>chrome://settings/cookies</code> पर जाएं</li>
                <li>Facebook.com के लिए कुकीज़ ढूंढें</li>
                <li>"Export Cookies" एक्सटेंशन का उपयोग करके TXT फाइल सेव करें</li>
                <li>उस फाइल को यहाँ अपलोड करें</li>
            </ol>
            <p class="warning">सावधानी: केवल अपनी खुद की कुकी फाइलें अपलोड करें!</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    token = None
    if request.method == 'POST':
        if 'cookie_file' in request.files:
            file = request.files['cookie_file']
            if file.filename != '':
                cookies_text = file.read().decode('utf-8')
                token = extract_tokens(cookies_text)
    return render_template_string(HTML_TEMPLATE, token=token)

def extract_tokens(cookies_text):
    tokens = {'c_user': None, 'xs': None}
    for line in cookies_text.splitlines():
        if 'facebook.com' in line:
            parts = line.split('\t')
            if len(parts) > 6:
                if parts[5] == 'c_user':
                    tokens['c_user'] = parts[6]
                elif parts[5] == 'xs':
                    tokens['xs'] = parts[6]
    return tokens if tokens['c_user'] and tokens['xs'] else None

# Render.com के लिए जरूरी कॉन्फिगरेशन
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
