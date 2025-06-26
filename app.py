from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# HTML (सीधे Python में लिखा हुआ)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>फेसबुक टोकन एक्सट्रैक्टर</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        .box { border: 1px solid #ddd; padding: 20px; margin-top: 20px; border-radius: 5px; }
        .warning { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>फेसबुक टोकन निकालें</h1>
    
    <form method="post" enctype="multipart/form-data">
        <p>अपनी ब्राउज़र कुकी फाइल (cookies.txt) अपलोड करें:</p>
        <input type="file" name="cookie_file" accept=".txt" required>
        <br><br>
        <button type="submit">टोकन निकालें</button>
    </form>

    {% if token %}
    <div class="box">
        <h3>मिले टोकन:</h3>
        <p><strong>c_user:</strong> {{ token.c_user }}</p>
        <p><strong>xs टोकन:</strong> {{ token.xs }}</p>
        <p class="warning">⚠️ इन टोकन को किसी के साथ शेयर न करें!</p>
    </div>
    {% endif %}

    <div class="box">
        <h3>कुकी फाइल कैसे ढूंढें?</h3>
        <ul>
            <li><strong>Chrome:</strong> <code>chrome://settings/cookies/detail?site=facebook.com</code></li>
            <li><strong>Firefox:</strong> Addon like "Export Cookies"</li>
            <li><strong>Edge:</strong> <code>edge://settings/siteData</code></li>
        </ul>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    token = None
    if request.method == 'POST':
        file = request.files['cookie_file']
        if file:
            cookies = file.read().decode('utf-8')
            token = extract_facebook_tokens(cookies)
    return render_template_string(HTML, token=token)

def extract_facebook_tokens(cookies_text):
    lines = cookies_text.split('\n')
    tokens = {'c_user': None, 'xs': None}
    
    for line in lines:
        if 'facebook.com' in line:
            if '\tc_user\t' in line:
                tokens['c_user'] = line.split('\t')[-1].strip()
            elif '\txs\t' in line:
                tokens['xs'] = line.split('\t')[-1].strip()
    
    return tokens if tokens['c_user'] and tokens['xs'] else None

if __name__ == '__main__':
    app.run(debug=True)
