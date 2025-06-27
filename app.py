#!/usr/bin/env python
from flask import Flask, request, render_template_string, jsonify
import requests
import re
import json
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Token Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f6f7;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1877f2;
            text-align: center;
        }
        textarea, input, button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            box-sizing: border-box;
        }
        button {
            background-color: #1877f2;
            color: white;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }
        button:hover {
            background-color: #166fe5;
        }
        .result {
            padding: 15px;
            background-color: #f0f2f5;
            border-radius: 6px;
            margin-top: 10px;
            word-break: break-all;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 6px 6px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            color: black;
            width: auto;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #1877f2;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 6px 6px;
            background-color: white;
        }
        .info {
            font-size: 14px;
            color: #65676b;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Extractor</h1>
        
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'extractTab')">Extract Token</button>
            <button class="tablinks" onclick="openTab(event, 'sendTab')">Send Message</button>
        </div>
        
        <div id="extractTab" class="tabcontent" style="display: block;">
            <p class="info">Paste your Facebook cookies below to extract the access token.</p>
            <textarea id="cookies" rows="10" placeholder="Paste Facebook cookies here (e.g., c_user=12345; xs=abcde...)"></textarea>
            <button onclick="extractToken()">Extract Token</button>
            <div class="result" id="tokenResult"></div>
        </div>
        
        <div id="sendTab" class="tabcontent">
            <p class="info">Enter the recipient's Facebook ID and your message below.</p>
            <input type="text" id="recipientId" placeholder="Recipient Facebook ID">
            <input type="text" id="accessToken" placeholder="Facebook Access Token">
            <textarea id="message" rows="5" placeholder="Your message"></textarea>
            <button onclick="sendMessage()">Send Message</button>
            <div class="result" id="sendResult"></div>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        function extractToken() {
            const cookies = document.getElementById('cookies').value.trim();
            if (!cookies) {
                document.getElementById('tokenResult').innerText = 'Please paste your cookies first';
                return;
            }
            
            fetch('/extract_token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({cookies: cookies}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('tokenResult').innerText = 'Error: ' + data.error;
                } else {
                    document.getElementById('tokenResult').innerText = 'Access Token: ' + data.token;
                    document.getElementById('accessToken').value = data.token;
                }
            })
            .catch(error => {
                document.getElementById('tokenResult').innerText = 'Error: ' + error;
            });
        }
        
        function sendMessage() {
            const recipientId = document.getElementById('recipientId').value.trim();
            const accessToken = document.getElementById('accessToken').value.trim();
            const message = document.getElementById('message').value.trim();
            
            if (!recipientId || !accessToken || !message) {
                document.getElementById('sendResult').innerText = 'Please fill all fields';
                return;
            }
            
            fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipient_id: recipientId,
                    access_token: accessToken,
                    message: message
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('sendResult').innerText = 'Error: ' + data.error;
                if (data.error_description) {
                    document.getElementById('sendResult').innerText += '\n' + data.error_description;
                }
                if (data.fb_error) {
                    document.getElementById('sendResult').innerText += '\nFacebook Error: ' + data.fb_error;
                }
                if (data.fb_error_description) {
                    document.getElementById('sendResult').innerText += '\n' + data.fb_error_description;
                }
                if (data.fb_error_code) {
                    document.getElementById('sendResult').innerText += '\nError Code: ' + data.fb_error_code;
                }
                if (data.fb_error_subcode) {
                    document.getElementById('sendResult').innerText += '\nError Subcode: ' + data.fb_error_subcode;
                }
                if (data.fb_error_user_msg) {
                    document.getElementById('sendResult').innerText += '\n' + data.fb_error_user_msg;
                }
                if (data.fb_error_user_title) {
                    document.getElementById('sendResult').innerText += '\n' + data.fb_error_user_title;
                }
                if (data.fb_error_is_transient) {
                    document.getElementById('sendResult').innerText += '\nIs Transient: ' + data.fb_error_is_transient;
                }
                if (data.fb_error_blame_field_specs) {
                    document.getElementById('sendResult').innerText += '\nBlame Field Specs: ' + JSON.stringify(data.fb_error_blame_field_specs);
                }
                if (data.fb_error_trace_id) {
                    document.getElementById('sendResult').innerText += '\nTrace ID: ' + data.fb_error_trace_id;
                }
                if (data.fb_error_fbtrace_id) {
                    document.getElementById('sendResult').innerText += '\nFB Trace ID: ' + data.fb_error_fbtrace_id;
                }
                if (data.fb_error_type) {
                    document.getElementById('sendResult').innerText += '\nError Type: ' + data.fb_error_type;
                }
                if (data.fb_error_code) {
                    document.getElementById('sendResult').innerText += '\nError Code: ' + data.fb_error_code;
                }
                if (data.fb_error_subcode) {
                    document.getElementById('sendResult').innerText += '\nError Subcode: ' + data.fb_error_subcode;
                }
                if (data.fb_error_user_msg) {
                    document.getElementById('sendResult').innerText += '\nUser Message: ' + data.fb_error_user_msg;
                }
                if (data.fb_error_user_title) {
                    document.getElementById('sendResult').innerText += '\nUser Title: ' + data.fb_error_user_title;
                }
                if (data.fb_error_is_transient) {
                    document.getElementById('sendResult').innerText += '\nIs Transient: ' + data.fb_error_is_transient;
                }
                if (data.fb_error_blame_field_specs) {
                    document.getElementById('sendResult').innerText += '\nBlame Field Specs: ' + JSON.stringify(data.fb_error_blame_field_specs);
                }
                if (data.fb_error_trace_id) {
                    document.getElementById('sendResult').innerText += '\nTrace ID: ' + data.fb_error_trace_id;
                }
                if (data.fb_error_fbtrace_id) {
                    document.getElementById('sendResult').innerText += '\nFB Trace ID: ' + data.fb_error_fbtrace_id;
                }
                if (data.fb_error_type) {
                    document.getElementById('sendResult').innerText += '\nError Type: ' + data.fb_error_type;
                }
                if (data.fb_error_code) {
                    document.getElementById('sendResult').innerText += '\nError Code: ' + data.fb_error_code;
                }
                if (data.fb_error_subcode) {
                    document.getElementById('sendResult').innerText += '\nError Subcode: ' + data.fb_error_subcode;
                }
                if (data.fb_error_user_msg) {
                    document.getElementById('sendResult').innerText += '\nUser Message: ' + data.fb_error_user_msg;
                }
                if (data.fb_error_user_title) {
                    document.getElementById('sendResult').innerText += '\nUser Title: ' + data.fb_error_user_title;
                }
                if (data.fb_error_is_transient) {
                    document.getElementById('sendResult').innerText += '\nIs Transient: ' + data.fb_error_is_transient;
                }
                if (data.fb_error_blame_field_specs) {
                    document.getElementById('sendResult').innerText += '\nBlame Field Specs: ' + JSON.stringify(data.fb_error_blame_field_specs);
                }
                if (data.fb_error_trace_id) {
                    document.getElementById('sendResult').innerText += '\nTrace ID: ' + data.fb_error_trace_id;
                }
                if (data.fb_error_fbtrace_id) {
                    document.getElementById('sendResult').innerText += '\nFB Trace ID: ' + data.fb_error_fbtrace_id;
                }
                if (data.fb_error_type) {
                    document.getElementById('sendResult').innerText += '\nError Type: ' + data.fb_error_type;
                }
            } else {
                document.getElementById('sendResult').innerText = 'Message sent successfully! Response: ' + JSON.stringify(data);
            }
            })
            .catch(error => {
                document.getElementById('sendResult').innerText = 'Error: ' + error;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract_token', methods=['POST'])
def extract_token():
    try:
        data = request.get_json()
        cookies = data.get('cookies', '')
        
        # Extract c_user and xs from cookies
        c_user_match = re.search(r'c_user=(\d+)', cookies)
        xs_match = re.search(r'xs=([^;]+)', cookies)
        
        if not c_user_match or not xs_match:
            return jsonify({'error': 'Required cookies (c_user and xs) not found'})
        
        c_user = c_user_match.group(1)
        xs_token = xs_match.group(1)
        
        # Construct token
        token = f"EAA{c_user}|{xs_token}"
        
        return jsonify({'token': token})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        access_token = data.get('access_token')
        message = data.get('message')
        
        if not all([recipient_id, access_token, message]):
            return jsonify({'error': 'Missing required parameters'})
        
        # Facebook Graph API endpoint
        url = f"https://graph.facebook.com/v19.0/me/messages"
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message},
            'access_token': access_token
        }
        
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to send message',
                'fb_error': response_data.get('error', {}).get('message'),
                'fb_error_description': response_data.get('error', {}).get('error_user_msg'),
                'fb_error_code': response_data.get('error', {}).get('code'),
                'fb_error_subcode': response_data.get('error', {}).get('error_subcode'),
                'fb_error_user_msg': response_data.get('error', {}).get('error_user_msg'),
                'fb_error_user_title': response_data.get('error', {}).get('error_user_title'),
                'fb_error_is_transient': response_data.get('error', {}).get('is_transient'),
                'fb_error_blame_field_specs': response_data.get('error', {}).get('blame_field_specs'),
                'fb_error_trace_id': response_data.get('error', {}).get('trace_id'),
                'fb_error_fbtrace_id': response_data.get('error', {}).get('fbtrace_id'),
                'fb_error_type': response_data.get('error', {}).get('type')
            })
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
