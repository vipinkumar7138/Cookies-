# app.py (this is a combined HTML/Python file that works with Flask)
from flask import Flask, request, render_template_string, jsonify
import re
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Token Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1877f2;
            text-align: center;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .instructions {
            background-color: #fff8e1;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Extractor</h1>
        
        <div class="instructions">
            <h3>How to use:</h3>
            <ol>
                <li>Get cookies from Monokai Toolkit app</li>
                <li>Paste all cookies in the box below</li>
                <li>Click "Extract Tokens" button</li>
            </ol>
        </div>
        
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="Paste cookies here in format: name=value; name2=value2; ..."></textarea>
            <button type="submit">Extract Tokens</button>
        </form>
        
        {% if result %}
        <div class="result">
            <h3>Extracted Tokens:</h3>
            {{ result|safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def extract_tokens():
    cookies = request.form.get('cookies', '')
    
    # Extract Facebook tokens from cookies
    tokens = {
        'access_token': None,
        'xs_token': None,
        'c_user': None,
        'datr': None,
        'sb': None
    }
    
    # Find access token (EAA... format)
    access_token_match = re.search(r'([EAA][a-zA-Z0-9]{100,})', cookies)
    if access_token_match:
        tokens['access_token'] = access_token_match.group(1)
    
    # Find other common Facebook tokens
    cookie_pairs = [c.strip() for c in cookies.split(';') if c.strip()]
    for pair in cookie_pairs:
        if '=' in pair:
            name, value = pair.split('=', 1)
            name = name.strip()
            value = value.strip()
            
            if name == 'xs':
                tokens['xs_token'] = value
            elif name == 'c_user':
                tokens['c_user'] = value
            elif name == 'datr':
                tokens['datr'] = value
            elif name == 'sb':
                tokens['sb'] = value
    
    # Format the result for display
    result = ""
    if tokens['access_token']:
        result += f"<strong>Access Token:</strong> {tokens['access_token']}<br><br>"
    if tokens['xs_token']:
        result += f"<strong>XS Token:</strong> {tokens['xs_token']}<br>"
    if tokens['c_user']:
        result += f"<strong>c_user:</strong> {tokens['c_user']}<br>"
    if tokens['datr']:
        result += f"<strong>datr:</strong> {tokens['datr']}<br>"
    if tokens['sb']:
        result += f"<strong>sb:</strong> {tokens['sb']}<br>"
    
    if not result:
        result = "No Facebook tokens found in the provided cookies."
    
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
