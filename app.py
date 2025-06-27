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
        :root {
            --primary-color: #1877f2;
            --secondary-color: #f0f2f5;
            --text-color: #1c1e21;
            --card-bg: #ffffff;
            --error-color: #ff4d4f;
            --success-color: #52c41a;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        body {
            background-color: var(--secondary-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 0;
            margin: 0;
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
        }
        
        input[type="text"]:focus {
            border-color: var(--primary-color);
            outline: none;
        }
        
        button {
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
        
        button:hover {
            background-color: #166fe5;
        }
        
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            background-color: var(--secondary-color);
            display: none;
            width: 100%;
        }
        
        .error {
            color: var(--error-color);
            margin-top: 10px;
            font-size: 14px;
            display: none;
        }
        
        .success {
            color: var(--success-color);
            margin-top: 10px;
            font-size: 14px;
            display: none;
        }
        
        .group-item {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            margin-bottom: 15px;
        }
        
        .group-item:last-child {
            border-bottom: none;
        }
        
        .member-item {
            padding: 5px;
            margin: 5px 0;
            background-color: white;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .copy-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        .copy-btn:hover {
            background-color: #45a049;
        }
        
        .toggle-members {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            margin-top: 5px;
        }
        
        .toggle-members:hover {
            background-color: #166fe5;
        }
        
        .members-container {
            margin-top: 10px;
            display: none;
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
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
            </div>
            
            <button onclick="extractGroups()">Extract Group UIDs</button>
            
            <div id="loader" class="loader"></div>
            <div id="error" class="error"></div>
            <div id="success" class="success"></div>
            
            <div id="result" class="result"></div>
        </div>
    </div>

    <script>
        function extractGroups() {
            const token = document.getElementById('access-token').value.trim();
            const loader = document.getElementById('loader');
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            const resultDiv = document.getElementById('result');
            
            if (!token) {
                showError('Please enter your access token');
                return;
            }
            
            // Clear previous results and show loader
            showError('');
            showSuccess('');
            resultDiv.style.display = 'none';
            loader.style.display = 'block';
            
            fetch('/extract-groups', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ access_token: token })
            })
            .then(response => response.json())
            .then(data => {
                loader.style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data.groups, data.members);
                }
            })
            .catch(error => {
                loader.style.display = 'none';
                showError('An error occurred: ' + error.message);
            });
        }
        
        function displayResults(groups, membersData) {
            const resultDiv = document.getElementById('result');
            
            if (!groups || groups.length === 0) {
                resultDiv.innerHTML = '<p>No Messenger groups found</p>';
                resultDiv.style.display = 'block';
                return;
            }
            
            let html = '<h3>Your Messenger Groups:</h3>';
            
            groups.forEach((group, index) => {
                const groupMembers = membersData && membersData[index] ? membersData[index] : [];
                const memberCount = groupMembers.length;
                
                html += `
                    <div class="group-item">
                        <p><strong>Group ID:</strong> ${group.id} <button class="copy-btn" onclick="copyToClipboard('${group.id}')">Copy ID</button></p>
                        <p><strong>Name:</strong> ${group.name || 'No Name'}</p>
                        <p><strong>Members:</strong> ${memberCount} <button class="toggle-members" onclick="toggleMembers('members-${index}')">Show Members</button></p>
                        
                        <div id="members-${index}" class="members-container">
                            ${groupMembers.map(member => `
                                <div class="member-item">
                                    <p><strong>ID:</strong> ${member.id} <button class="copy-btn" onclick="copyToClipboard('${member.id}')">Copy</button></p>
                                    <p><strong>Name:</strong> ${member.name || 'No Name'}</p>
                                </div>
                            `).join('')}
                            
                            ${memberCount > 0 ? `<button class="copy-btn" onclick="copyAllMembers('${index}')">Copy All Member IDs</button>` : ''}
                        </div>
                    </div>
                `;
            });
            
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }
        
        function toggleMembers(id) {
            const container = document.getElementById(id);
            const button = container.previousElementSibling.querySelector('.toggle-members');
            
            if (container.style.display === 'block') {
                container.style.display = 'none';
                button.textContent = 'Show Members';
            } else {
                container.style.display = 'block';
                button.textContent = 'Hide Members';
            }
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text)
                .then(() => showSuccess('Copied to clipboard!'))
                .catch(err => showError('Failed to copy: ' + err));
        }
        
        function copyAllMembers(groupIndex) {
            const memberElements = document.querySelectorAll(`#members-${groupIndex} .member-item p:nth-child(1)`);
            const memberIds = Array.from(memberElements).map(el => {
                return el.textContent.replace('ID:', '').trim().split(' ')[0];
            });
            
            navigator.clipboard.writeText(memberIds.join('\n'))
                .then(() => showSuccess('All member IDs copied to clipboard!'))
                .catch(err => showError('Failed to copy: ' + err));
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            errorDiv.textContent = message;
            errorDiv.style.display = message ? 'block' : 'none';
            successDiv.style.display = 'none';
        }
        
        function showSuccess(message) {
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            successDiv.textContent = message;
            successDiv.style.display = message ? 'block' : 'none';
            errorDiv.style.display = 'none';
            
            // Hide success message after 3 seconds
            if (message) {
                setTimeout(() => {
                    successDiv.style.display = 'none';
                }, 3000);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract-groups', methods=['POST'])
def extract_groups():
    token = request.json.get('access_token')
    
    if not token:
        return jsonify({"error": "Token required!"})

    try:
        # Step 1: Check if token is valid
        user_info = requests.get(f"https://graph.facebook.com/v12.0/me?access_token={token}").json()
        if "error" in user_info:
            return jsonify({"error": f"Invalid Token: {user_info['error']['message']}"})

        # Step 2: Fetch Messenger Conversations (Groups)
        groups_url = f"https://graph.facebook.com/v12.0/me/conversations?fields=id,name&access_token={token}"
        groups_data = requests.get(groups_url).json()

        if "error" in groups_data:
            error_msg = groups_data['error']['message']
            if 'permission' in error_msg.lower():
                return jsonify({"error": "Missing permissions. Required: user_managed_groups, pages_messaging"})
            return jsonify({"error": error_msg})

        # Step 3: Fetch members for each group
        members_data = []
        for group in groups_data.get("data", []):
            try:
                members_url = f"https://graph.facebook.com/v12.0/{group['id']}/participants?fields=id,name&access_token={token}"
                members_response = requests.get(members_url).json()
                members_data.append(members_response.get("data", []))
            except Exception as e:
                members_data.append([])
                continue

        return jsonify({
            "groups": groups_data.get("data", []),
            "members": members_data
        })

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
