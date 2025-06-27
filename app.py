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
    <title>Facebook EAAD6V7 Token Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #272822;
            color: #f8f8f2;
        }
        h1 {
            color: #a6e22e;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 10px;
            margin: 10px 0;
            background-color: #3e3d32;
            color: #f8f8f2;
            border: 1px solid #75715e;
        }
        button {
            background-color: #66d9ef;
            color: #272822;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #a6e22e;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .success {
            background-color: #2e8b57;
        }
        .error {
            background-color: #f92672;
        }
    </style>
</head>
<body>
    <h1>Facebook EAAD6V7 Token Extractor</h1>
    <p>Paste your Facebook login cookies below:</p>
    <form method="POST" action="/extract">
        <textarea name="cookies" placeholder="Paste cookies here (e.g., c_user=12345; xs=abcde; ...)"></textarea>
        <button type="submit">Extract Token</button>
    </form>
    {% if result %}
    <div class="result {% if result.error %}error{% else %}success{% endif %}">
        {% if result.error %}
            <strong>Error:</strong> {{ result.error }}
        {% else %}
            <strong>Extracted Token:</strong><br>{{ result.token }}
            <br><br>
            <a href="/download" download="fb_token.txt">Download Token</a>
        {% endif %}
    </div>
    {% endif %}
</body>
</html>
"""

def extract_eaad6v7_token(cookie_string):
    """
    Extract EAAD6V7 token from Facebook login cookies
    """
    cookie = SimpleCookie()
    try:
        cookie.load(cookie_string)
    except Exception as e:
        return None, f"Error parsing cookies: {str(e)}"

    # Check for required Facebook cookies
    if 'c_user' not in cookie or 'xs' not in cookie:
        return None, "Required Facebook cookies (c_user, xs) not found"

    # Try to find the EAAD6V7 token
    token_pattern = r'EAAD6V7[0-9A-Za-z]+'
    match = re.search(token_pattern, cookie_string)
    
    if match:
        return match.group(0), None
    else:
        return None, "EAAD6V7 token not found in cookies"

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def extract():
    cookies = request.form.get('cookies', '').strip()
    if not cookies:
        return render_template_string(HTML_TEMPLATE, result={'error': 'Please enter Facebook cookies'})
    
    token, error = extract_eaad6v7_token(cookies)
    if error:
        return render_template_string(HTML_TEMPLATE, result={'error': error})
    else:
        # Store token in session for download
        app.config['EXTRACTED_TOKEN'] = token
        return render_template_string(HTML_TEMPLATE, result={'token': token})

@app.route('/download')
def download():
    token = app.config.get('EXTRACTED_TOKEN', '')
    if not token:
        return "No token available to download", 400
    return token, 200, {'Content-Disposition': 'attachment; filename=fb_token.txt'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
