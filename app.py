# app.py - Combined Flask backend and HTML frontend for Render deployment
from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook UID Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #1877f2;
            text-align: center;
        }
        textarea, input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            box-sizing: border-box;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f8ff;
            border-radius: 6px;
            word-break: break-all;
        }
        .disclaimer {
            margin-top: 20px;
            font-size: 12px;
            color: #65676b;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook UID Extractor</h1>
        <p>Enter your Facebook access token to retrieve your User ID:</p>
        
        <textarea id="tokenInput" rows="5" placeholder="Paste Facebook access token here..."></textarea>
        
        <button onclick="extractUID()">Get UID</button>
        
        <div id="result" class="result" style="display: none;">
            <h3>Result:</h3>
            <p id="uidOutput"></p>
        </div>
        
        <div class="disclaimer">
            <p>This tool extracts your Facebook User ID from an access token. Never share your token with untrusted parties.</p>
        </div>
    </div>

    <script>
        function extractUID() {
            const token = document.getElementById('tokenInput').value.trim();
            
            if (!token) {
                alert('Please enter a Facebook access token');
                return;
            }
            
            // Show loading state
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            document.getElementById('uidOutput').textContent = 'Processing...';
            
            // Send token to backend for processing
            fetch('/extract-uid', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: token }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('uidOutput').textContent = 'Error: ' + data.error;
                } else {
                    document.getElementById('uidOutput').textContent = 'User ID: ' + data.uid;
                }
            })
            .catch(error => {
                document.getElementById('uidOutput').textContent = 'Error: ' + error.message;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract-uid', methods=['POST'])
def extract_uid():
    data = request.get_json()
    token = data.get('token', '').strip()
    
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    
    try:
        # Method 1: Try to extract from token directly (JWT format)
        if '.' in token:
            parts = token.split('.')
            if len(parts) > 1:
                import base64
                import json
                try:
                    payload = parts[1]
                    # Add padding if needed
                    payload += '=' * (-len(payload) % 4)
                    decoded = base64.b64decode(payload).decode('utf-8')
                    data = json.loads(decoded)
                    if 'user_id' in data:
                        return jsonify({'uid': data['user_id']})
                except:
                    pass
        
        # Method 2: Query Facebook's API
        try:
            response = requests.get(
                f'https://graph.facebook.com/me?access_token={token}',
                timeout=10
            )
            data = response.json()
            if 'id' in data:
                return jsonify({'uid': data['id']})
            elif 'error' in data:
                return jsonify({'error': data['error']['message']}), 400
        except requests.RequestException as e:
            return jsonify({'error': str(e)}), 500
        
        # Method 3: Try to find UID in token string
        match = re.search(r'(\d{10,})', token)
        if match:
            return jsonify({'uid': match.group(1)})
        
        return jsonify({'error': 'Could not extract UID from token'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
