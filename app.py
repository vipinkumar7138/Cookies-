#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from http.cookies import SimpleCookie
from flask import Flask, request, render_template_string, jsonify
import os

app = Flask(__name__)

# HTML और Python कोड एक साथ
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook EAAD6V7 Token Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1877f2; /* Facebook blue */
            text-align: center;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            resize: vertical;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
            width: 100%;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Extractor</h1>
        <p>Facebook कुकीज़ पेस्ट करें (c_user, xs, fr, आदि):</p>
        
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="c_user=12345; xs=abcde; fr=EAAD6V7..."></textarea>
            <button type="submit">टोकन निकालें</button>
        </form>
        
        <div id="result" class="{% if result %}{% if result.error %}error{% else %}success{% endif %}{% endif %}">
            {% if result %}
                {% if result.error %}
                    <strong>त्रुटि:</strong> {{ result.error }}
                {% else %}
                    <strong>EAAD6V7 टोकन:</strong><br>
                    <code>{{ result.token }}</code>
                    <br><br>
                    <a href="/download" download="fb_token.txt" style="color: #1877f2;">टोकन डाउनलोड करें</a>
                {% endif %}
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def extract_eaad6v7_token(cookie_string):
    """कुकी स्ट्रिंग से EAAD6V7 टोकन निकालें"""
    try:
        # सबसे पहले सीधे टोकन खोजें
        token_match = re.search(r'EAAD6V7[0-9A-Za-z]{100,200}', cookie_string)
        if token_match:
            return token_match.group(), None
        
        # अगर सीधे नहीं मिला तो कुकी पार्स करके देखें
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        
        # fr कुकी में टोकन हो सकता है
        if 'fr' in cookie:
            fr_token = cookie['fr'].value
            token_match = re.search(r'EAAD6V7[0-9A-Za-z]{100,200}', fr_token)
            if token_match:
                return token_match.group(), None
        
        return None, "EAAD6V7 टोकन नहीं मिला"
    except Exception as e:
        return None, f"त्रुटि: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def handle_extraction():
    cookies = request.form.get('cookies', '').strip()
    if not cookies:
        return render_template_string(HTML_TEMPLATE, result={'error': 'कृपया Facebook कुकीज़ पेस्ट करें'})
    
    token, error = extract_eaad6v7_token(cookies)
    if error:
        return render_template_string(HTML_TEMPLATE, result={'error': error})
    
    app.config['EXTRACTED_TOKEN'] = token
    return render_template_string(HTML_TEMPLATE, result={'token': token})

@app.route('/download')
def download_token():
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
