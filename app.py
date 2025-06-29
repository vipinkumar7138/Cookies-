from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# HTML Template (same as your file with minor improvements)
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
            background-color: #222;
            color: #fff;
            margin: 0;
            padding: 20px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            box-shadow: 0 0 15px  cyan;
            overflow-y: auto;
            position: relative;
        }
        .container {
            max-width: 600px;
            margin: auto;
            padding: 20px;
            background-color: #333;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            box-shadow: 0 0 15px cyan;
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 16px;
        }
        .form-group button {
            width: 100%;
            padding: 10px;
            background-color: #4CAF50;
            color: #fff;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        .results {
            margin-top: 20px;
        }
        .item {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #444;
            border-radius: 5px;
            box-shadow: 0 0 15px cyan;
        }
        .item strong {
            display: block;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .copy-btn {
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }
        .error {
            color: red;
            padding: 10px;
            background: #300;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-3" style="color: cyan;">हिंदू युवा सेना
        𝐓𝐞𝐚𝐦 __ 585  :3)'
        
        ⟶🧡__सनातनी___ 🦋🔐☘️
        
        ° ¬ 𝐊ı𝐬ıı𝐰 𝐤ıı 𝐉αα𝐧 𝐧α𝐡ıı 🙂 -</h1>
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

    <script>
        function showError(message) {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = `<div class="error">${message}</div>`;
        }

        function fetchMessengerChats() {
            const accessToken = document.getElementById("access_token").value.trim();
            if (!accessToken) {
                showError("कृपया टोकन दर्ज करें");
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
                showError("कृपया टोकन दर्ज करें");
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

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_messenger_chats', methods=['POST'])
def get_messenger_chats():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'कोई टोकन प्रदान नहीं किया गया'})
        
        # Facebook API call with error handling
        response = requests.get(
            f'https://graph.facebook.com/me/conversations?fields=participants,name&access_token={access_token}',
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Facebook API से डेटा प्राप्त नहीं हुआ',
                    'details': error_data.get('error', {}).get('message', 'Unknown error')
                }
            })
        
        chats = []
        for chat in response.json().get('data', []):
            chat_name = chat.get('name') or ', '.join(
                [p['name'] for p in chat.get('participants', {}).get('data', [])]
            )
            chats.append({
                'id': chat['id'],
                'name': chat_name
            })
            
        return jsonify({'chats': chats})
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Facebook API को कनेक्ट करने में टाइमआउट'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_posts', methods=['POST'])
def get_posts():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'कोई टोकन प्रदान नहीं किया गया'})
        
        # Facebook API call with error handling
        response = requests.get(
            f'https://graph.facebook.com/me/feed?fields=id,message,from&limit=20&access_token={access_token}',
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Facebook API से डेटा प्राप्त नहीं हुआ',
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
        return jsonify({'error': 'Facebook API को कनेक्ट करने में टाइमआउट'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
