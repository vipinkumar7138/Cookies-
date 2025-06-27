from flask import Flask, render_template_string, request, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import json
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Setup Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Setup Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Simple user system
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Messenger Group UID Extractor</title>
    <style>
        :root {
            --primary-color: #1877f2;
            --secondary-color: #f0f2f5;
            --text-color: #1c1e21;
            --card-bg: #ffffff;
            --error-color: #ff4d4f;
            --dark-bg: #18191a;
            --dark-card: #242526;
            --dark-text: #e4e6eb;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            transition: background-color 0.3s, color 0.3s;
        }
        
        body {
            background-color: var(--secondary-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 0;
            margin: 0;
        }
        
        body.dark-mode {
            background-color: var(--dark-bg);
            color: var(--dark-text);
        }
        
        .container {
            max-width: 100%;
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 8px 16px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
            padding: 20px;
            margin: 20px auto;
        }
        
        .dark-mode .card {
            background-color: var(--dark-card);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3), 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        
        h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
        }
        
        .form-group {
            margin-bottom: 15px;
            width: 100%;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 14px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
            background-color: var(--card-bg);
            color: var(--text-color);
        }
        
        .dark-mode input[type="text"] {
            background-color: #3e4042;
            color: var(--dark-text);
            border-color: #3e4042;
        }
        
        input[type="text"]:focus {
            border-color: var(--primary-color);
            outline: none;
        }
        
        button, .export-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
            transition: background-color 0.3s;
        }
        
        button:hover, .export-btn:hover {
            background-color: #166fe5;
        }
        
        .secondary-btn {
            background-color: #e4e6eb;
            color: #1c1e21;
        }
        
        .dark-mode .secondary-btn {
            background-color: #3e4042;
            color: var(--dark-text);
        }
        
        .secondary-btn:hover {
            background-color: #d8dadf;
        }
        
        .dark-mode .secondary-btn:hover {
            background-color: #4e5052;
        }
        
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            background-color: var(--secondary-color);
            display: none;
            width: 100%;
        }
        
        .dark-mode .result {
            background-color: #3e4042;
        }
        
        .error {
            color: var(--error-color);
            margin-top: 10px;
            font-size: 14px;
            display: none;
        }
        
        .group-item {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .dark-mode .group-item {
            border-bottom: 1px solid #3e4042;
        }
        
        .group-item:last-child {
            border-bottom: none;
        }
        
        .search-container {
            margin-bottom: 15px;
        }
        
        .search-container input {
            width: 100%;
            padding: 10px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .dark-mode .search-container input {
            background-color: #3e4042;
            color: var(--dark-text);
            border-color: #3e4042;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .controls button {
            width: auto;
            flex: 1;
        }
        
        /* Mobile Styles */
        @media (max-width: 600px) {
            .container {
                padding: 10px;
            }
            
            .card {
                padding: 15px;
                margin: 10px auto;
                border-radius: 0;
                box-shadow: none;
            }
            
            h1 {
                font-size: 20px;
            }
            
            input[type="text"], button {
                padding: 14px;
            }
        }
        
        /* Desktop Styles */
        @media (min-width: 601px) {
            .card {
                animation: fadeIn 0.5s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        }
        
        /* Loading spinner */
        .loader {
            display: none;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        .dark-mode .loader {
            border: 4px solid #3e4042;
            border-top: 4px solid var(--primary-color);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .token-info {
            font-size: 12px;
            color: #65676b;
            margin-top: 5px;
        }
        
        .dark-mode .token-info {
            color: #b0b3b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Messenger Group UID Extractor</h1>
            
            <div class="form-group">
                <label for="access-token">Facebook Access Token:</label>
                <input type="text" id="access-token" placeholder="EAAD... (your access token)">
                <div id="token-info" class="token-info"></div>
            </div>
            
            <button onclick="extractGroups()">Extract Group UIDs</button>
            
            <div id="loader" class="loader"></div>
            <div id="error" class="error"></div>
            
            <div id="result" class="result"></div>
        </div>
    </div>

    <script>
        // Check for dark mode preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }
        
        // Toggle dark mode
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        }
        
        // Check localStorage for dark mode setting
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
        
        function validateToken(token) {
            if (!token) return false;
            
            // Simple pattern check for FB token
            return /^[EAa][A-Za-z0-9]{100,}$/.test(token);
        }
        
        function showTokenInfo(valid) {
            const infoDiv = document.getElementById('token-info');
            if (valid) {
                infoDiv.textContent = '✔ Token format appears valid';
                infoDiv.style.color = 'green';
            } else {
                infoDiv.textContent = '⚠ Check token format';
                infoDiv.style.color = 'orange';
            }
        }
        
        // Token input validation
        document.getElementById('access-token').addEventListener('input', function(e) {
            showTokenInfo(validateToken(e.target.value));
        });
        
        function extractGroups() {
            const token = document.getElementById('access-token').value.trim();
            const loader = document.getElementById('loader');
            const errorDiv = document.getElementById('error');
            const resultDiv = document.getElementById('result');
            
            if (!token) {
                showError('Please enter your access token');
                return;
            }
            
            // Clear previous results and show loader
            showError('');
            resultDiv.style.display = 'none';
            loader.style.display = 'block';
            
            fetch('/extract-groups', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ access_token: token })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Network response was not ok');
                    });
                }
                return response.json();
            })
            .then(data => {
                loader.style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data.groups, data.token_info);
                }
            })
            .catch(error => {
                loader.style.display = 'none';
                showError('An error occurred: ' + error.message);
            });
        }
        
        function displayResults(groups, tokenInfo) {
            const resultDiv = document.getElementById('result');
            
            if (!groups || groups.length === 0) {
                resultDiv.innerHTML = '<p>No Messenger groups found</p>';
                resultDiv.style.display = 'block';
                return;
            }
            
            let html = `
                <h3>Your Messenger Groups (${groups.length})</h3>
                <div class="search-container">
                    <input type="text" id="groupSearch" placeholder="Search groups..." oninput="searchGroups()">
                </div>
            `;
            
            groups.forEach(group => {
                html += `
                    <div class="group-item">
                        <p><strong>Group ID:</strong> ${group.id}</p>
                        <p><strong>Name:</strong> ${group.name || 'No Name'}</p>
                        ${group.updated_time ? `<p><strong>Last Active:</strong> ${new Date(group.updated_time).toLocaleString()}</p>` : ''}
                        ${group.participants ? `<p><strong>Participants:</strong> ${group.participants.data.length}</p>` : ''}
                    </div>
                `;
            });
            
            html += `
                <div class="controls">
                    <button class="export-btn" onclick="exportToJSON()">Export as JSON</button>
                    <button class="export-btn secondary-btn" onclick="exportToCSV()">Export as CSV</button>
                </div>
                <button class="secondary-btn" onclick="toggleDarkMode()">Toggle Dark Mode</button>
            `;
            
            if (tokenInfo) {
                html += `
                    <div class="token-info" style="margin-top: 20px;">
                        <p><strong>Token Info:</strong></p>
                        <p>App ID: ${tokenInfo.app_id}</p>
                        <p>Valid until: ${new Date(tokenInfo.expires_at * 1000).toLocaleString()}</p>
                        <p>Scopes: ${tokenInfo.scopes.join(', ')}</p>
                    </div>
                `;
            }
            
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }
        
        function searchGroups() {
            const searchTerm = document.getElementById('groupSearch').value.toLowerCase();
            const groups = document.querySelectorAll('.group-item');
            
            groups.forEach(group => {
                const text = group.textContent.toLowerCase();
                group.style.display = text.includes(searchTerm) ? 'block' : 'none';
            });
        }
        
        function exportToJSON() {
            const token = document.getElementById('access-token').value.trim();
            const groups = document.querySelectorAll('.group-item');
            const data = [];
            
            groups.forEach(group => {
                if (group.style.display !== 'none') {
                    const id = group.querySelector('p:nth-child(1)').textContent.replace('Group ID:', '').trim();
                    const name = group.querySelector('p:nth-child(2)').textContent.replace('Name:', '').trim();
                    data.push({ id, name });
                }
            });
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `fb_groups_${new Date().toISOString().slice(0,10)}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function exportToCSV() {
            const token = document.getElementById('access-token').value.trim();
            const groups = document.querySelectorAll('.group-item');
            let csv = 'Group ID,Group Name\n';
            
            groups.forEach(group => {
                if (group.style.display !== 'none') {
                    const id = group.querySelector('p:nth-child(1)').textContent.replace('Group ID:', '').trim();
                    const name = group.querySelector('p:nth-child(2)').textContent.replace('Name:', '').trim();
                    csv += `"${id}","${name}"\n`;
                }
            });
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `fb_groups_${new Date().toISOString().slice(0,10)}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
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
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract-groups', methods=['POST'])
@limiter.limit("10 per minute")
def extract_groups():
    token = request.json.get('access_token')
    
    if not token:
        return jsonify({"error": "Token required!"}), 400

    try:
        # Step 1: Validate token and get debug info
        debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
        debug_info = requests.get(debug_url).json()
        
        if "error" in debug_info:
            return jsonify({"error": f"Invalid Token: {debug_info['error']['message']}"}), 401
        
        token_data = debug_info.get('data', {})
        token_info = {
            "app_id": token_data.get('app_id'),
            "expires_at": token_data.get('expires_at'),
            "scopes": token_data.get('scopes', [])
        }
        
        # Step 2: Fetch user info to verify token works
        user_info = requests.get(f"https://graph.facebook.com/v12.0/me?access_token={token}").json()
        if "error" in user_info:
            return jsonify({"error": f"Token Error: {user_info['error']['message']}"}), 401

        # Step 3: Fetch Messenger Conversations (Groups) with pagination
        groups = []
        groups_url = f"https://graph.facebook.com/v12.0/me/conversations?fields=id,name,updated_time,participants&access_token={token}"
        
        while True:
            groups_data = requests.get(groups_url).json()
            
            if "error" in groups_data:
                error_msg = groups_data['error']['message']
                if 'permission' in error_msg.lower():
                    return jsonify({"error": "Missing permissions. Required: user_managed_groups, pages_messaging"}), 403
                return jsonify({"error": error_msg}), 400
            
            groups.extend(groups_data.get("data", []))
            
            if "paging" not in groups_data or "next" not in groups_data["paging"]:
                break
                
            groups_url = groups_data["paging"]["next"]

        return jsonify({
            "groups": groups,
            "token_info": token_info
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

@app.route('/export/json', methods=['POST'])
@login_required
def export_json():
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    si = StringIO()
    json.dump(data, si)
    output = si.getvalue()
    si.close()
    
    return send_file(
        StringIO(output),
        mimetype='application/json',
        as_attachment=True,
        download_name=f"fb_groups_{datetime.now().date()}.json"
    )

@app.route('/export/csv', methods=['POST'])
@login_required
def export_csv():
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Group ID', 'Group Name'])
    
    for group in data:
        writer.writerow([group.get('id', ''), group.get('name', '')])
    
    output = si.getvalue()
    si.close()
    
    return send_file(
        StringIO(output),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"fb_groups_{datetime.now().date()}.csv"
    )

if __name__ == '__main__':
    app.run(debug=True)
