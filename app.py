from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# HTML Template with CSS, JavaScript, and Form for Facebook API
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Data Fetcher</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #1877f2; /* Facebook Blue */
            text-align: center;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .error {
            color: red;
        }
        .chat, .post {
            margin: 10px 0;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Data Fetcher</h1>
        
        <div>
            <h2>Get Messenger Chats</h2>
            <input type="text" id="chatToken" placeholder="Enter Facebook Access Token">
            <button onclick="fetchChats()">Fetch Chats</button>
            <div id="chatResult" class="result"></div>
        </div>
        
        <div>
            <h2>Get Facebook Posts</h2>
            <input type="text" id="postToken" placeholder="Enter Facebook Access Token">
            <button onclick="fetchPosts()">Fetch Posts</button>
            <div id="postResult" class="result"></div>
        </div>
    </div>

    <script>
        async function fetchChats() {
            const token = document.getElementById('chatToken').value;
            const resultDiv = document.getElementById('chatResult');
            resultDiv.innerHTML = 'Loading...';
            
            try {
                const response = await fetch('/get_messenger_chats', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const data = await response.json();
                
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">Error: ${data.error.message || data.error}</div>`;
                } else {
                    let html = '<h3>Your Chats:</h3>';
                    data.chats.forEach(chat => {
                        html += `<div class="chat"><strong>${chat.name}</strong> (ID: ${chat.id})</div>`;
                    });
                    resultDiv.innerHTML = html;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function fetchPosts() {
            const token = document.getElementById('postToken').value;
            const resultDiv = document.getElementById('postResult');
            resultDiv.innerHTML = 'Loading...';
            
            try {
                const response = await fetch('/get_posts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const data = await response.json();
                
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">Error: ${data.error.message || data.error}</div>`;
                } else {
                    let html = '<h3>Your Posts:</h3>';
                    data.posts.forEach(post => {
                        html += `
                            <div class="post">
                                <strong>${post.profile_name}</strong>: 
                                ${post.name || "No text content"} (ID: ${post.id})
                            </div>`;
                    });
                    resultDiv.innerHTML = html;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
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
            return jsonify({'error': 'No provided token'})
        
        # Facebook API call with error handling
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
                [p['name'] for p in chat.get('participants', {}).get('data', [])]
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
        
        # Facebook API call with error handling
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
