# app.py (Final tested version for Render)
from flask import Flask, request, render_template_string
import re
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook EAAD Token Extractor</title>
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
        .error {
            color: red;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook EAAD Token Extractor</h1>
        
        <div class="instructions">
            <h3>How to use:</h3>
            <ol>
                <li>Get cookies from Monokai Toolkit app</li>
                <li>Paste all cookies in the box below</li>
                <li>Click "Extract EAAD Token" button</li>
            </ol>
        </div>
        
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="Paste cookies here in format: name=value; name2=value2; ..." required></textarea>
            <button type="submit">Extract EAAD Token</button>
        </form>
        
        {% if result %}
        <div class="result">
            <h3>Extracted EAAD Token:</h3>
            {{ result|safe }}
        </div>
        {% endif %}
        
        {% if error %}
        <div class="error">
            {{ error|safe }}
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
    try:
        cookies = request.form.get('cookies', '').strip()
        
        if not cookies:
            return render_template_string(HTML_TEMPLATE, error="Please paste cookies in the input box")
        
        # Find EAAD... format access token (case insensitive)
        access_token_match = re.search(r'(EAAD[a-zA-Z0-9]{100,})', cookies, re.IGNORECASE)
        
        if access_token_match:
            result = f"<strong>EAAD Token:</strong> {access_token_match.group(1)}"
        else:
            result = "No EAAD Token found in the provided cookies."
        
        return render_template_string(HTML_TEMPLATE, result=result)
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"Error processing request: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
