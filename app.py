# app.py (Final Working Version)
from flask import Flask, request, render_template_string
import re
import os
import urllib.parse

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Token Extractor Pro</title>
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
            height: 200px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
            font-family: monospace;
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
            width: 100%;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f8ff;
            border-radius: 4px;
            border: 1px solid #1877f2;
            word-wrap: break-word;
        }
        .error {
            margin-top: 20px;
            padding: 15px;
            background-color: #ffebee;
            border-radius: 4px;
            border: 1px solid #f44336;
            color: #d32f2f;
        }
        .debug {
            margin-top: 20px;
            padding: 15px;
            background-color: #fff3e0;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Extractor Pro</h1>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <h3>कैसे उपयोग करें:</h3>
            <ol>
                <li><strong>Monokai Toolkit</strong> से सभी कुकीज कॉपी करें (Ctrl+A, Ctrl+C)</li>
                <li>नीचे दिए बॉक्स में <strong>सभी कुकीज</strong> पेस्ट करें (Ctrl+V)</li>
                <li>"Extract Token" बटन पर क्लिक करें</li>
            </ol>
            <p style="color: #d32f2f; font-weight: bold;">⚠️ ध्यान दें: पूरी कुकीज पेस्ट करें, छोटा हिस्सा नहीं</p>
        </div>
        
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="यहां सभी कुकीज पेस्ट करें (Ctrl+V)" required></textarea>
            <button type="submit">Extract Token</button>
        </form>
        
        {% if result %}
        <div class="result">
            <h3>✅ टोकन मिल गया:</h3>
            <div style="background: black; color: lime; padding: 10px; border-radius: 4px; overflow-x: auto;">
                {{ result|safe }}
            </div>
            <p style="font-size: 12px; color: #666; margin-top: 5px;">
                इस टोकन को किसी के साथ शेयर न करें!
            </p>
        </div>
        {% endif %}
        
        {% if error %}
        <div class="error">
            <h3>❌ समस्या:</h3>
            {{ error|safe }}
        </div>
        {% endif %}
        
        {% if debug_info %}
        <div class="debug">
            <h3>डीबग जानकारी:</h3>
            {{ debug_info|safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def find_facebook_token(cookies):
    # Try multiple patterns to find the token
    patterns = [
        r'(EAAB[a-zA-Z0-9]{200,})',  # Newer FB token format
        r'(EAAD[a-zA-Z0-9]{200,})',  # Older FB token format
        r'([a-zA-Z0-9]{200,})',      # Generic long token
        r'access_token=([a-zA-Z0-9]{150,})',  # URL encoded token
        r'"access_token":"([a-zA-Z0-9]{150,})"'  # JSON format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cookies, re.IGNORECASE)
        if match:
            token = match.group(1)
            # Basic validation
            if len(token) >= 150 and not any(c in token for c in [' ', ';', '"', "'"]):
                return urllib.parse.unquote(token)  # Decode URL encoded tokens
    
    return None

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def extract_tokens():
    try:
        cookies = request.form.get('cookies', '').strip()
        
        if not cookies:
            return render_template_string(HTML_TEMPLATE, error="कृपया कुकीज पेस्ट करें")
        
        if len(cookies) < 100:
            return render_template_string(HTML_TEMPLATE, 
                                      error=f"कुकीज बहुत छोटी हैं ({len(cookies)} कैरेक्टर्स), पूरी कुकीज पेस्ट करें")
        
        # Find token using advanced detection
        token = find_facebook_token(cookies)
        
        debug_info = [
            f"स्कैन की गई डेटा: {len(cookies)} कैरेक्टर्स",
            f"टोकन मिला: {'हाँ' if token else 'नहीं'}"
        ]
        
        if token:
            # Format token for display
            formatted_token = f"{token[:50]}...{token[-50:]}" if len(token) > 100 else token
            full_token = token
            result = f"""
            <strong>पूरा टोकन:</strong><br>
            <span style="user-select: all">{full_token}</span><br><br>
            <strong>संक्षिप्त:</strong> {formatted_token}<br>
            <strong>लंबाई:</strong> {len(token)} कैरेक्टर्स
            """
            return render_template_string(HTML_TEMPLATE, result=result)
        
        return render_template_string(HTML_TEMPLATE,
                                   error="कोई वैध Facebook टोकन नहीं मिला",
                                   debug_info="<br>".join(debug_info))
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
                                   error=f"त्रुटि: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
