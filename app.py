#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template_string
import re
from http.cookies import SimpleCookie
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook EAAD6V7 Token Extractor</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1877f2;
            text-align: center;
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 16px;
            margin-bottom: 15px;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
        }
        .success {
            background-color: #e7f3ff;
            border: 1px solid #b3d4ff;
            color: #1a73e8;
        }
        .error {
            background-color: #fef0f0;
            border: 1px solid #fbd8d8;
            color: #d93025;
        }
        .token {
            word-break: break-all;
            font-family: monospace;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook EAAD6V7 Token Extractor</h1>
        <p>Facebook कुकीज़ पेस्ट करें (c_user, xs, fr, आदि):</p>
        
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="c_user=12345; xs=abcde; fr=EAAD6V7..."></textarea>
            <button type="submit">टोकन निकालें</button>
        </form>
        
        {% if result %}
        <div class="result {% if result.error %}error{% else %}success{% endif %}">
            {% if result.error %}
                <strong>त्रुटि:</strong> {{ result.error }}
            {% else %}
                <strong>EAAD6V7 टोकन:</strong><br>
                <div class="token">{{ result.token }}</div>
                <br>
                <a href="/download" download="fb_token.txt" style="color: #1877f2; text-decoration: none;">
                    <button style="background-color: #42b72a;">टोकन डाउनलोड करें</button>
                </a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_token(cookie_string):
    """Facebook कुकीज़ से EAAD6V7 टोकन निकालें"""
    try:
        # पहले सीधे टोकन खोजें
        token_match = re.search(r'(EAAD6V7[a-zA-Z0-9]+)', cookie_string)
        if token_match:
            return token_match.group(1), None
        
        # फिर कुकी पार्स करके देखें
        cookie = SimpleCookie()
        cookie.load(cookie_string.strip())
        
        # fr कुकी में टोकन हो सकता है
        if 'fr' in cookie:
            fr_value = cookie['fr'].value
            token_match = re.search(r'(EAAD6V7[a-zA-Z0-9]+)', fr_value)
            if token_match:
                return token_match.group(1), None
        
        return None, "EAAD6V7 टोकन नहीं मिला। कृपया सही Facebook कुकीज़ पेस्ट करें।"
    except Exception as e:
        return None, f"कुकीज़ पार्स करने में त्रुटि: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def extract():
    cookies = request.form.get('cookies', '').strip()
    if not cookies:
        return render_template_string(HTML_TEMPLATE, result={'error': 'कृपया Facebook कुकीज़ पेस्ट करें'})
    
    token, error = extract_token(cookies)
    if error:
        return render_template_string(HTML_TEMPLATE, result={'error': error})
    
    app.config['EXTRACTED_TOKEN'] = token
    return render_template_string(HTML_TEMPLATE, result={'token': token})

@app.route('/download')
def download():
    token = app.config.get('EXTRACTED_TOKEN', '')
    if not token:
        return "डाउनलोड के लिए कोई टोकन उपलब्ध नहीं", 400
    return token, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=fb_token.txt'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
