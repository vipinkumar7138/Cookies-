# app.py (Improved EAAD Token Detection)
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
        /* ... (same styles as before) ... */
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
            <p><strong>Note:</strong> Make sure you're copying <em>all</em> cookies including the long access token</p>
        </div>
        
        <form method="POST" action="/extract">
            <textarea name="cookies" placeholder="Paste ALL cookies here (including long strings)" required></textarea>
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
        
        {% if debug_info %}
        <div class="instructions" style="margin-top:20px;">
            <h3>Debug Info:</h3>
            <p>{{ debug_info|safe }}</p>
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
        
        # Improved EAAD token detection
        access_token_match = re.search(r'(EAAD[a-zA-Z0-9]{150,})', cookies, re.IGNORECASE)
        
        if not access_token_match:
            # Try alternative patterns
            access_token_match = re.search(r'(access_token=[\'"]?([a-zA-Z0-9]{150,}))', cookies, re.IGNORECASE)
            if access_token_match:
                access_token_match = re.search(r'([a-zA-Z0-9]{150,})', access_token_match.group(0))
        
        debug_info = f"Scanned {len(cookies)} characters of cookie data"
        
        if access_token_match:
            token = access_token_match.group(1)
            if len(token) >= 150:  # EAAD tokens are typically very long
                result = f"<strong>EAAD Token:</strong> {token}"
                return render_template_string(HTML_TEMPLATE, result=result)
        
        return render_template_string(HTML_TEMPLATE, 
                                  error="No valid EAAD Token found",
                                  debug_info=debug_info)
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=f"Error: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
