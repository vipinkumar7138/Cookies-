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
        
        .group-item {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            margin-bottom: 15px;
        }
        
        .group-item:last-child {
            border-bottom: none;
        }
        
        .member-item {
            padding: 8px;
            background: #f9f9f9;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .toggle-members {
            color: var(--primary-color);
            cursor: pointer;
            font-size: 14px;
            margin-top: 5px;
            display: inline-block;
        }
        
        .members-container {
            display: none;
            margin-top: 10px;
            padding: 10px;
            background: #f0f2f5;
            border-radius: 4px;
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
                <input type="text" id="access-token" placeholder="EAAD... or EAAG... (your access token)">
            </div>
            
            <button onclick="extractGroups()">Extract Group UIDs</button>
            
            <div id="loader" class="loader"></div>
            <div id="error" class="error"></div>
            
            <div id="result" class="result"></div>
        </div>
    </div>

    <script>
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
            .then(response => response.json())
            .then(data => {
                loader.style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data.groups);
                }
            })
            .catch(error => {
                loader.style.display = 'none';
                showError('An error occurred: ' + error.message);
            });
        }
        
        function displayResults(groups) {
            const resultDiv = document.getElementById('result');
            
            if (!groups || groups.length === 0) {
                resultDiv.innerHTML = '<p>No Messenger groups found</p>';
                resultDiv.style.display = 'block';
                return;
            }
            
            let html = '<h3>Your Messenger Groups:</h3>';
            
            groups.forEach(group => {
                html += `
                    <div class="group-item">
                        <p><strong>Group ID:</strong> ${group.id}</p>
                        <p><strong>Name:</strong> ${group.name || 'No Name'}</p>
                        <span class="toggle-members" onclick="toggleMembers('${group.id}', this)">▼ Show Members</span>
                        <div id="members-${group.id}" class="members-container"></div>
                    </div>
                `;
            });
            
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }
        
        function toggleMembers(groupId, element) {
            const container = document.getElementById(`members-${groupId}`);
            const token = document.getElementById('access-token').value.trim();
            
            if (container.innerHTML === '') {
                // Fetch members if not already loaded
                fetch('/get-members', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        access_token: token,
                        group_id: groupId 
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        container.innerHTML = `<p>${data.error}</p>`;
                    } else {
                        let membersHtml = '<h4>Members:</h4>';
                        if (data.members && data.members.length > 0) {
                            data.members.forEach(member => {
                                membersHtml += `
                                    <div class="member-item">
                                        <p><strong>User ID:</strong> ${member.id}</p>
                                        <p><strong>Name:</strong> ${member.name || 'No Name'}</p>
                                    </div>
                                `;
                            });
                        } else {
                            membersHtml += '<p>No members found or no permission to view members</p>';
                        }
                        container.innerHTML = membersHtml;
                    }
                })
                .catch(error => {
                    container.innerHTML = `<p>Error loading members: ${error.message}</p>`;
                });
            }
            
            if (container.style.display === 'none' || container.style.display === '') {
                container.style.display = 'block';
                element.textContent = '▲ Hide Members';
            } else {
                container.style.display = 'none';
                element.textContent = '▼ Show Members';
            }
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
def extract_groups():
    token = request.json.get('access_token')
    
    if not token:
        return jsonify({"error": "Token required!"})

    try:
        # Check token validity (works for both EAAD and EAAG)
        user_info = requests.get(
            f"https://graph.facebook.com/v19.0/me",
            params={
                'access_token': token,
                'fields': 'id,name'
            }
        ).json()
        
        if "error" in user_info:
            error_msg = user_info['error']['message']
            if "expired" in error_msg.lower():
                return jsonify({"error": "Token expired or invalid. Please generate a new one."})
            return jsonify({"error": f"Invalid Token: {error_msg}"})

        # Fetch Messenger Conversations (Groups)
        groups_data = requests.get(
            "https://graph.facebook.com/v19.0/me/conversations",
            params={
                'access_token': token,
                'fields': 'id,name',
                'limit': '100'
            }
        ).json()

        if "error" in groups_data:
            error_msg = groups_data['error']['message']
            if 'permission' in error_msg.lower():
                return jsonify({"error": "Missing permissions. Required: user_managed_groups, pages_messaging"})
            return jsonify({"error": error_msg})

        return jsonify({"groups": groups_data.get("data", [])})

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"})

@app.route('/get-members', methods=['POST'])
def get_members():
    token = request.json.get('access_token')
    group_id = request.json.get('group_id')
    
    if not token or not group_id:
        return jsonify({"error": "Token and group ID required!"})

    try:
        # Fetch group members (works for both EAAD and EAAG)
        members_data = requests.get(
            f"https://graph.facebook.com/v19.0/{group_id}/participants",
            params={
                'access_token': token,
                'fields': 'id,name',
                'limit': '100'
            }
        ).json()

        if "error" in members_data:
            error_msg = members_data['error']['message']
            return jsonify({"error": error_msg})

        return jsonify({"members": members_data.get("data", [])})

    except Exception as e:
        return jsonify({"error": f"Error fetching members: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
