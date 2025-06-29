from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# VIP PINK THEME (Text: White | BG: Black | Buttons: Blue)
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
            background-color: #000000; /* Pure Black */
            color: #ffffff; /* White Text */
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            padding: 20px;
            background-color: #33001a; /* Dark Pink */
            border-radius: 10px;
            box-shadow: 0 0 20px #ff0099; /* Pink Glow */
        }
        h1 {
            color: #ff0099; /* Bright Pink */
            text-align: center;
            text-shadow: 0 0 10px rgba(255, 0, 153, 0.5);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #ffffff;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ff0099;
            border-radius: 4px;
            font-size: 16px;
            background: #111;
            color: white;
        }
        .form-group button {
            width: 100%;
            padding: 10px;
            background-color: #3366ff; /* Royal Blue */
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.3s;
        }
        .form-group button:hover {
            background: #0044ff; /* Darker Blue on Hover */
            transform: scale(1.02);
        }
        .results {
            margin-top: 20px;
        }
        .item {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #1a001a;
            border-radius: 5px;
            border-left: 3px solid #ff0099;
        }
        .item strong {
            display: block;
            font-size: 14px;
            margin-bottom: 5px;
            color: #ff99cc; /* Light Pink */
        }
        .copy-btn {
            background-color: #3366ff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }
        .error {
            color: #ff3333;
            padding: 10px;
            background: #330000;
            border-radius: 4px;
            border: 1px solid #ff0066;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-3" style="color: #ff0099;">VARUN DHAWAL</h1>
        <h1>ᴀᴄᴄᴇꜱꜱ ᴄʜᴀᴛ ᴀɴᴅ ᴘᴏꜱᴛ ᴜɪᴅ</h1>
        <div class="form-group">
            <label for="access_token">ᴀᴄᴄᴇꜱꜱ ᴛᴏᴋᴇɴ : </label>
            <input type="text" id="access_token" placeholder="ᴇɴʏᴇʀ ʏᴏᴜʀ ꜰᴀᴄᴇʙᴏᴏᴋ ᴀᴄᴄᴇꜱꜱ ᴛᴏᴋᴇɴ ">
        </div>
        <div class="form-group">
            <button onclick="fetchMessengerChats()">ɢᴇᴛ ᴄʜᴀᴛꜱ</button>
        </div>
        <div class="form-group">
            <button onclick="fetchPosts()">ɢᴇᴛ ᴘᴏꜱᴛꜱ</button>
        </div>
        <div id="results" class="results"></div>
    </div>

    <!-- Rest of your JavaScript remains the same -->
    <script>
        function showError(message) {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = `<div class="error">${message}</div>`;
        }

        function fetchMessengerChats() {
            const accessToken = document.getElementById("access_token").value.trim();
            if (!accessToken) {
                showError("Please enter correct token");
                return;
            }

            fetch('/get_messenger_chats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ access_token: accessToken })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const resultsDiv = document.getElementById("results");
                resultsDiv.innerHTML = '';
                
                if (data.error) {
                    showError(`त्रुटि: ${data.error.message || data.error}`);
                } else {
                    data.chats.forEach(chat => {
                        const chatDiv = document.createElement("div");
                        chatDiv.className = "item";
                        chatDiv.innerHTML = `
                            <strong>ᴄʜᴀᴛ ɴᴀᴍᴇ : </strong> ${chat.name}<br>
                            <strong>ᴄʜᴀᴛ ᴜɪᴅ : </strong> ${chat.id}<br>
                            <button class="copy-btn" onclick="copyToClipboard('${chat.id}')">ᴄᴏᴘʏ ᴄʜᴀᴛ ᴜɪᴅ</button>
                        `;
                        resultsDiv.appendChild(chatDiv);
                    });
                }
            })
            .catch(error => {
                showError(`त्रुटि: ${error.message}`);
                console.error('Error:', error);
            });
        }

        function fetchPosts() {
            const accessToken = document.getElementById("access_token").value.trim();
            if (!accessToken) {
                showError("Please enter correct token");
                return;
            }

            fetch('/get_posts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ access_token: accessToken })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const resultsDiv = document.getElementById("results");
                resultsDiv.innerHTML = '';
                
                if (data.error) {
                    showError(`त्रुटि: ${data.error.message || data.error}`);
                } else {
                    data.posts.forEach(post => {
                        const postDiv = document.createElement("div");
                        postDiv.className = "item";
                        postDiv.innerHTML = `
                            <strong>ᴘᴏꜱᴛ ɴᴀᴍᴇ :  </strong> ${post.name || 'Unnamed Post'}<br>
                            <strong>ᴘᴏꜱᴛ ᴜɪᴅ :</strong> ${post.id}<br>
                            <strong>ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ : </strong> ${post.profile_name}<br>
                            <button class="copy-btn" onclick="copyToClipboard('${post.id}')">ᴄᴏᴘʏ ᴘᴏꜱᴛ ᴜɪᴅ</button>
                        `;
                        resultsDiv.appendChild(postDiv);
                    });
                }
            })
            .catch(error => {
                showError(`त्रुटि: ${error.message}`);
                console.error('Error:', error);
            });
        }

        function copyToClipboard(uid) {
            navigator.clipboard.writeText(uid).then(() => {
                alert("UID copied to clipboard!");
            });
        }
    </script>
</body>
</html>
"""

# REST OF YOUR FLASK CODE REMAINS THE SAME
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_messenger_chats', methods=['POST'])
def get_messenger_chats():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'No provided token'})
        
        response = requests.get(
            f'https://graph.facebook.com/me/conversations?fields=participants,name&access_token={access_token}',
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Please enter correct token',
                    'details': error_data.get('error', {}).get('message', 'Unknown error')
                }
            })
        
        chats = []
        for chat in response.json().get('data', []):
            chat_name = chat.get('name') or ', '.join(
                [p['name'] for p in chat.get('participants', {}).get('data', [])
            )
            chats.append({
                'id': chat['id'],
                'name': chat_name
            })
            
        return jsonify({'chats': chats})
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Please try again'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_posts', methods=['POST'])
def get_posts():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'Please enter the token'})
        
        response = requests.get(
            f'https://graph.facebook.com/me/feed?fields=id,message,from&limit=20&access_token={access_token}',
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Please enter correct token',
                    'details': error_data.get('error', {}).get('message', 'Unknown error')
                }
            })
        
        posts = []
        for post in response.json().get('data', []):
            posts.append({
                'id': post['id'],
                'name': post.get('message', 'No text content'),
                'profile_name': post.get('from', {}).get('name', 'Unknown')
            })
            
        return jsonify({'posts': posts})
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Plesse try again'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
