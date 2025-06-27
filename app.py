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
        /* ... (पहले जैसा ही स्टाइल रखें) ... */
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
            
            // Clear previous results
            showError('');
            showSuccess('');
            resultDiv.style.display = 'none';
            loader.style.display = 'block';
            
            fetch('/extract-groups', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    access_token: token,
                    fields: 'id,name,participants{id,name}'  // सभी जरूरी फील्ड्स रिक्वेस्ट करें
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                loader.style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                } else if (data.groups && data.groups.length > 0) {
                    displayResults(data.groups);
                } else {
                    showError('No groups found or you may not have permission');
                }
            })
            .catch(error => {
                loader.style.display = 'none';
                showError('An error occurred: ' + error.message);
                console.error('Error:', error);
            });
        }
        
        function displayResults(groups) {
            const resultDiv = document.getElementById('result');
            let html = '<h3>Your Messenger Groups:</h3>';
            
            groups.forEach(group => {
                const participants = group.participants?.data || [];
                
                html += `
                    <div class="group-item">
                        <p><strong>Group ID:</strong> ${group.id} 
                            <button class="copy-btn" onclick="copyToClipboard('${group.id}')">Copy ID</button>
                        </p>
                        <p><strong>Name:</strong> ${group.name || 'No Name'}</p>
                        <p><strong>Members:</strong> ${participants.length} 
                            <button class="toggle-members" onclick="toggleMembers('members-${group.id}')">
                                Show Members
                            </button>
                        </p>
                        
                        <div id="members-${group.id}" class="members-container">
                            ${participants.map(member => `
                                <div class="member-item">
                                    <p><strong>ID:</strong> ${member.id} 
                                        <button class="copy-btn" onclick="copyToClipboard('${member.id}')">Copy</button>
                                    </p>
                                    <p><strong>Name:</strong> ${member.name || 'No Name'}</p>
                                </div>
                            `).join('')}
                            
                            ${participants.length > 0 ? `
                                <button class="copy-btn" onclick="copyAllMembers('${group.id}')">
                                    Copy All Member IDs
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }
        
        // ... (बाकी फंक्शन्स पहले जैसे ही रखें) ...
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract-groups', methods=['POST'])
def extract_groups():
    data = request.json
    token = data.get('access_token')
    fields = data.get('fields', 'id,name')
    
    if not token:
        return jsonify({"error": "Token required!"})

    try:
        # Step 1: Validate token
        user_info = requests.get(
            f"https://graph.facebook.com/v12.0/me?access_token={token}"
        ).json()
        
        if "error" in user_info:
            return jsonify({
                "error": f"Invalid Token: {user_info['error']['message']}"
            })

        # Step 2: Fetch groups with participants
        groups_url = f"https://graph.facebook.com/v12.0/me/conversations?fields={fields}&access_token={token}"
        groups_response = requests.get(groups_url)
        groups_data = groups_response.json()

        if "error" in groups_data:
            error_msg = groups_data['error']['message']
            if 'permission' in error_msg.lower():
                return jsonify({
                    "error": "Missing permissions. Required: user_managed_groups, pages_messaging, read_mailbox"
                })
            return jsonify({"error": error_msg})

        return jsonify({
            "groups": groups_data.get("data", [])
        })

    except Exception as e:
        return jsonify({
            "error": f"Server Error: {str(e)}",
            "details": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
