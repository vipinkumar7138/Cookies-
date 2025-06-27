#!/usr/bin/env python3
from flask import Flask, request, render_template_string, jsonify
import re
import json
import os

app = Flask(__name__)

# Configuration for Render
PORT = os.getenv('PORT', '5000')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Token Extractor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f6f7;
        }
        h1 {
            color: #1877f2;
            text-align: center;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            resize: vertical;
            font-family: monospace;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
            width: 100%;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f2f5;
            border-radius: 6px;
            word-wrap: break-word;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
        .disclaimer {
            margin-top: 30px;
            padding: 15px;
            background-color: #fff4e6;
            border-radius: 6px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Extractor</h1>
        <form id="tokenForm">
            <p>Paste your Facebook cookies below (in JSON format):</p>
            <textarea id="cookies" name="cookies" placeholder='[{"name": "c_user", "value": "100123456789"}, {"name": "xs", "value": "abc123xyz456"}]' required></textarea>
            <br>
            <button type="submit">Extract Tokens</button>
        </form>
        
        <div id="error" class="error" style="display: none;"></div>
        
        <div id="result" class="result" style="display: none;">
            <h3>Extracted Tokens:</h3>
            <p><strong>User ID:</strong> <span id="user_id"></span></p>
            <p><strong>Access Token:</strong> <span id="access_token"></span></p>
            <p><strong>Profile Token:</strong> <span id="profile_token"></span></p>
            <p><strong>XS Token:</strong> <span id="xs_token"></span></p>
        </div>
        
        <div class="disclaimer">
            <strong>Disclaimer:</strong> This tool is for educational purposes only. Never share your Facebook tokens with anyone as they provide access to your account. The developer is not responsible for any misuse of this tool.
        </div>
    </div>

    <script>
        document.getElementById('tokenForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const cookies = document.getElementById('cookies').value;
            const errorDiv = document.getElementById('error');
            const resultDiv = document.getElementById('result');
            
            errorDiv.style.display = 'none';
            resultDiv.style.display = 'none';
            
            fetch('/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cookies: cookies })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    errorDiv.textContent = data.error;
                    errorDiv.style.display = 'block';
                } else {
                    document.getElementById('user_id').textContent = data.user_id || 'Not found';
                    document.getElementById('access_token').textContent = data.access_token || 'Not found';
                    document.getElementById('profile_token').textContent = data.profile_token || 'Not found';
                    document.getElementById('xs_token').textContent = data.xs_token || 'Not found';
                    resultDiv.style.display = 'block';
                }
            })
            .catch(error => {
                errorDiv.textContent = 'An error occurred while processing your request.';
                errorDiv.style.display = 'block';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract', methods=['POST'])
def extract_tokens():
    try:
        data = request.get_json()
        cookies = data.get('cookies', '')
        
        if not cookies:
            return jsonify({'error': 'No cookies provided'}), 400
        
        try:
            cookie_data = json.loads(cookies)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format. Please provide cookies in proper JSON format.'}), 400
        
        tokens = {
            'user_id': None,
            'access_token': None,
            'profile_token': None,
            'xs_token': None
        }
        
        # Extract tokens from cookies
        for cookie in cookie_data:
            if not isinstance(cookie, dict):
                continue
                
            name = cookie.get('name', '').lower()
            value = cookie.get('value', '')
            
            if name == 'c_user':
                tokens['user_id'] = value
            elif name == 'xs':
                tokens['xs_token'] = value
                # Sometimes the access token is part of the xs token
                if len(value.split('|')) == 2:
                    tokens['access_token'] = value.split('|')[0]
            elif name == 'fr':
                # FR cookie often contains an access token
                match = re.search(r'([a-f0-9]{32})', value)
                if match:
                    tokens['access_token'] = match.group(1)
        
        # If we have user_id and xs_token, we can create a profile token
        if tokens['user_id'] and tokens['xs_token']:
            tokens['profile_token'] = f"{tokens['user_id']}|{tokens['xs_token']}"
        
        return jsonify(tokens)
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(PORT))
