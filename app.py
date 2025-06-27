from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook UID Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
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
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background-color: #e4e6eb;
            margin-right: 5px;
            border-radius: 6px 6px 0 0;
        }
        .tab.active {
            background-color: white;
            font-weight: bold;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook UID Extractor</h1>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('profile')">Profile UID</div>
            <div class="tab" onclick="switchTab('group')">Group UID</div>
        </div>
        
        <div id="profile-tab" class="tab-content active">
            <div class="form-group">
                <label for="profile-url">Facebook Profile URL or Username:</label>
                <input type="text" id="profile-url" placeholder="https://www.facebook.com/username or just username">
            </div>
            <div class="form-group">
                <label for="access-token">Facebook Access Token:</label>
                <input type="text" id="access-token" placeholder="EAAD... (your access token)">
            </div>
            <button onclick="extractProfileUid()">Extract Profile UID</button>
            <div id="profile-result" class="result"></div>
            <div id="profile-error" class="error"></div>
        </div>
        
        <div id="group-tab" class="tab-content">
            <div class="form-group">
                <label for="group-url">Facebook Group URL or ID:</label>
                <input type="text" id="group-url" placeholder="https://www.facebook.com/groups/groupid or just groupid">
            </div>
            <div class="form-group">
                <label for="group-access-token">Facebook Access Token:</label>
                <input type="text" id="group-access-token" placeholder="EAAD... (your access token)">
            </div>
            <button onclick="extractGroupUid()">Extract Group UID</button>
            <div id="group-result" class="result"></div>
            <div id="group-error" class="error"></div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            // Hide all tabs and contents
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Activate selected tab and content
            document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        }
        
        function extractProfileUid() {
            const profileUrl = document.getElementById('profile-url').value.trim();
            const accessToken = document.getElementById('access-token').value.trim();
            
            if (!profileUrl || !accessToken) {
                showError('profile', 'Please fill in all fields');
                return;
            }
            
            // Clear previous results
            showError('profile', '');
            document.getElementById('profile-result').style.display = 'none';
            
            fetch('/extract-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    profile_url: profileUrl,
                    access_token: accessToken
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError('profile', data.error);
                } else {
                    const resultDiv = document.getElementById('profile-result');
                    resultDiv.innerHTML = `
                        <strong>Profile UID:</strong> ${data.uid}<br>
                        <strong>Profile Name:</strong> ${data.name}<br>
                        <strong>Profile Link:</strong> <a href="https://facebook.com/${data.uid}" target="_blank">https://facebook.com/${data.uid}</a>
                    `;
                    resultDiv.style.display = 'block';
                }
            })
            .catch(error => {
                showError('profile', 'An error occurred: ' + error.message);
            });
        }
        
        function extractGroupUid() {
            const groupUrl = document.getElementById('group-url').value.trim();
            const accessToken = document.getElementById('group-access-token').value.trim();
            
            if (!groupUrl || !accessToken) {
                showError('group', 'Please fill in all fields');
                return;
            }
            
            // Clear previous results
            showError('group', '');
            document.getElementById('group-result').style.display = 'none';
            
            fetch('/extract-group', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    group_url: groupUrl,
                    access_token: accessToken
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError('group', data.error);
                } else {
                    const resultDiv = document.getElementById('group-result');
                    resultDiv.innerHTML = `
                        <strong>Group ID:</strong> ${data.id}<br>
                        <strong>Group Name:</strong> ${data.name}<br>
                        <strong>Group Link:</strong> <a href="https://facebook.com/groups/${data.id}" target="_blank">https://facebook.com/groups/${data.id}</a>
                    `;
                    resultDiv.style.display = 'block';
                }
            })
            .catch(error => {
                showError('group', 'An error occurred: ' + error.message);
            });
        }
        
        function showError(type, message) {
            const errorDiv = document.getElementById(`${type}-error`);
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

@app.route('/extract-profile', methods=['POST'])
def extract_profile():
    data = request.get_json()
    profile_url = data.get('profile_url', '').strip()
    access_token = data.get('access_token', '').strip()
    
    if not profile_url or not access_token:
        return jsonify({'error': 'Profile URL and access token are required'})
    
    try:
        # Extract username from URL if provided
        if 'facebook.com' in profile_url:
            username = profile_url.split('facebook.com/')[-1].split('/')[0].split('?')[0]
        else:
            username = profile_url
            
        # Remove any query parameters
        username = username.split('?')[0]
        
        # Make API request to get user ID
        api_url = f'https://graph.facebook.com/v12.0/{username}?fields=id,name&access_token={access_token}'
        response = requests.get(api_url)
        result = response.json()
        
        if 'error' in result:
            return jsonify({'error': result['error']['message']})
        
        return jsonify({
            'uid': result['id'],
            'name': result.get('name', ''),
            'username': username
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/extract-group', methods=['POST'])
def extract_group():
    data = request.get_json()
    group_url = data.get('group_url', '').strip()
    access_token = data.get('access_token', '').strip()
    
    if not group_url or not access_token:
        return jsonify({'error': 'Group URL and access token are required'})
    
    try:
        # Extract group ID from URL if provided
        if 'facebook.com' in group_url:
            group_id = group_url.split('groups/')[-1].split('/')[0].split('?')[0]
        else:
            group_id = group_url
            
        # Remove any query parameters
        group_id = group_id.split('?')[0]
        
        # Make API request to get group info
        api_url = f'https://graph.facebook.com/v12.0/{group_id}?fields=id,name&access_token={access_token}'
        response = requests.get(api_url)
        result = response.json()
        
        if 'error' in result:
            return jsonify({'error': result['error']['message']})
        
        return jsonify({
            'id': result['id'],
            'name': result.get('name', '')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
