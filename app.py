#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template_string, jsonify
import re
from http.cookies import SimpleCookie
import os

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MonokaiToolkit Cookie Token Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #2c3e50;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 4px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <h1>MonokaiToolkit Cookie Token Extractor</h1>
    <p>MonokaiToolkit से कॉपी की गई Facebook कुकीज़ पेस्ट करें:</p>
    <form method="POST" action="/extract">
        <textarea name="cookies" placeholder="c_user=12345; xs=abcde; fr=EAAD6V7..."></textarea>
        <button type="submit">टोकन निकालें</button>
    </form>
    {% if result %}
    <div class="result {% if result.error %}error{% else %}success{% endif %}">
        {% if result.error %}
            <strong>त्रुटि:</strong> {{ result.error }}
        {% else %}
            <strong>मिला टोकन:</strong><br>{{ result.token }}
            <br><br>
            <a href="/download" download="fb_token.txt">टोकन डाउनलोड करें</a>
        {% endif %}
    </div>
    {% endif %}
</body>
</html>
"""

def extract_token(cookie_string):
    """कुकी स्ट्रिंग से EAAD6V7 टोकन निकालें"""
    try:
        # Facebook की जरूरी कुकीज़ चेक करें
        if 'c_user=' not in cookie_string or 'xs=' not in cookie_string:
            return None, "Facebook की जरूरी कुकीज़ (c_user, xs) नहीं मिलीं"
        
        # टोकन खोजें
        token_match = re.search(r'EAAD6V7[0-9A-Za-z]+', cookie_string)
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
        return render_template_string(HTML_TEMPLATE, result={'error': 'कृपया कुकीज़ पेस्ट करें'})
    
    token, error = extract_token(cookies)
    if error:
        return render_template_string(HTML_TEMPLATE, result={'error': error})
    
    # टोकन को सेशन में सेव करें
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
