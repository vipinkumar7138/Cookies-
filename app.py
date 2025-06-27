from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Messenger Group UID Extractor</title>
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
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 16px;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            background-color: #f0f2f5;
            display: none;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Messenger Group UID Extractor</h1>
        
        <div class="form-group">
            <label for="access-token">Facebook Access Token:</label>
            <input type="text" id="access-token" placeholder="EAAD... (your access token)">
        </div>
        
        <button onclick="extractMessengerGroups()">Extract Messenger Group UIDs</button>
        
        <div id="result" class="result"></div>
        <div id="error" class="error"></div>
    </div>

    <script>
        function extractMessengerGroups() {
            const accessToken = document.getElementById('access-token').value.trim();
            
            if (!accessToken) {
                showError('Please enter your access token');
                return;
            }
            
            // Clear previous results
            showError('');
            document.getElementById('result').style.display = 'none';
            
            fetch('/extract-messenger-groups', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    access_token: accessToken
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data.groups);
                }
            })
            .catch(error => {
                showError('An error occurred: ' + error.message);
            });
        }
        
        function displayResults(groups) {
            const resultDiv = document.getElementById('result');
            
            if (groups.length === 0) {
                resultDiv.innerHTML = '<strong>No Messenger groups found</strong>';
            } else {
                let html = '<strong>Your Messenger Groups:</strong><br><br>';
                groups.forEach(group => {
                    html += `
                        <strong>Group ID:</strong> ${group.id}<br>
                        <strong>Group Name:</strong> ${group.name}<br><br>
                    `;
                });
                resultDiv.innerHTML = html;
            }
            resultDiv.style.display = 'block';
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = message ? 'block' : 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract-messenger-groups', methods=['POST'])
def extract_messenger_groups():
    data = request.get_json()
    access_token = data.get('access_token', '').strip()
    
    if not access_token:
        return jsonify({'error': 'Access token is required'})
    
    try:
        # Get Messenger groups using the access token
        api_url = f'https://graph.facebook.com/v12.0/me/groups?fields=id,name&access_token={access_token}'
        response = requests.get(api_url)
        result = response.json()
        
        if 'error' in result:
            return jsonify({'error': result['error']['message']})
        
        return jsonify({
            'groups': result.get('data', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
