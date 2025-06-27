from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Messenger Group UID Extractor</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px; }
        input, button { width: 100%; padding: 10px; margin: 5px 0; }
        button { background: #1877f2; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f0f2f5; }
    </style>
</head>
<body>
    <h1>Messenger Group UID Extractor</h1>
    <input type="text" id="access-token" placeholder="EAAD... (Facebook Access Token)">
    <button onclick="extractGroups()">Extract Group UIDs</button>
    <div id="result" class="result"></div>

    <script>
        function extractGroups() {
            const token = document.getElementById('access-token').value.trim();
            fetch('/extract-groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ access_token: token })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('result').innerHTML = `<strong>Error:</strong> ${data.error}`;
                } else {
                    let html = "<strong>Messenger Groups:</strong><br><br>";
                    data.groups.forEach(group => {
                        html += `<strong>Group ID:</strong> ${group.id}<br>`;
                        html += `<strong>Group Name:</strong> ${group.name || 'No Name'}<br><br>`;
                    });
                    document.getElementById('result').innerHTML = html;
                }
            });
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
            return jsonify({"error": f"API Error: {groups_data['error']['message']}"})

        return jsonify({"groups": groups_data.get("data", [])})

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
