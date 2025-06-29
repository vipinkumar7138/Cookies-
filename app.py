from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Render पर PORT environment variable का उपयोग करें
port = int(os.environ.get("PORT", 5000))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f2f5; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1877f2; text-align: center; }
        .form-group { margin-bottom: 15px; }
        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
        button { background: #1877f2; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #166fe5; }
        .result { margin-top: 20px; padding: 15px; background: #f7f8fa; border-radius: 4px; }
        .permission { display: inline-block; background: #e7f3ff; color: #1877f2; padding: 3px 8px; margin: 3px; border-radius: 3px; font-size: 0.9em; }
        .error { color: #ff4d4d; background: #fff0f0; padding: 10px; border-radius: 4px; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }
        .loading { display: none; text-align: center; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Token Analyzer</h1>
        <div class="form-group">
            <label for="token">अपना Facebook टोकन पेस्ट करें:</label>
            <textarea id="token" rows="3" placeholder="EAAY..."></textarea>
        </div>
        <button onclick="analyzeToken()" id="analyzeBtn">टोकन एनालाइज़ करें</button>
        <div id="loading" class="loading">
            <p>कृपया प्रतीक्षा करें...</p>
        </div>
        
        <div id="result" class="result" style="display:none;">
            <h3>टोकन जानकारी:</h3>
            <div id="tokenInfo"></div>
            
            <h3>परमिशन्स:</h3>
            <div id="permissions"></div>
            
            <h3>डेटा:</h3>
            <div id="data"></div>
        </div>
    </div>

    <script>
        function analyzeToken() {
            const token = document.getElementById('token').value.trim();
            if(!token) {
                alert('कृपया टोकन दर्ज करें');
                return;
            }

            // लोडिंग दिखाएं
            document.getElementById('analyzeBtn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';

            fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token })
            })
            .then(response => {
                if(!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                
                if(data.error) {
                    document.getElementById('tokenInfo').innerHTML = 
                        `<div class="error">त्रुटि: ${data.error.message || data.error}</div>`;
                    return;
                }
                
                // टोकन जानकारी दिखाएं
                document.getElementById('tokenInfo').innerHTML = `
                    <p><strong>टोकन प्रकार:</strong> ${data.token_type || 'अज्ञात'}</p>
                    <p><strong>एप्प ID:</strong> ${data.app_id || 'अज्ञात'}</p>
                    <p><strong>यूजर ID:</strong> ${data.user_id || 'अज्ञात'}</p>
                    <p><strong>वैधता:</strong> ${data.is_valid ? '✅ वैध' : '❌ अवैध'}</p>
                    <p><strong>समाप्ति तिथि:</strong> ${data.expires_at ? new Date(data.expires_at*1000).toLocaleString() : 'अज्ञात'}</p>
                `;
                
                // परमिशन्स दिखाएं
                const permsDiv = document.getElementById('permissions');
                permsDiv.innerHTML = data.permissions && data.permissions.length > 0 ? 
                    data.permissions.map(p => `<span class="permission">${p}</span>`).join('') :
                    '<p>कोई परमिशन नहीं मिली</p>';
                
                // डेटा दिखाएं
                document.getElementById('data').innerHTML = data.data ? 
                    `<pre>${JSON.stringify(data.data, null, 2)}</pre>` :
                    '<p>कोई डेटा नहीं मिला</p>';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('tokenInfo').innerHTML = 
                    `<div class="error">त्रुटि: ${error.message || 'अज्ञात त्रुटि'}</div>`;
            })
            .finally(() => {
                document.getElementById('analyzeBtn').disabled = false;
                document.getElementById('loading').style.display = 'none';
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({'error': {'message': 'कोई टोकन प्रदान नहीं किया गया'}})
        
        # 1. टोकन डीबग करें
        debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
        debug_resp = requests.get(debug_url, timeout=10)
        
        if debug_resp.status_code != 200:
            return jsonify({
                'error': {
                    'message': 'Facebook API से कनेक्ट नहीं हो पाया',
                    'details': debug_resp.json()
                }
            })
            
        debug_data = debug_resp.json().get('data', {})
        
        if not debug_data.get('is_valid'):
            return jsonify({
                'error': {
                    'message': 'अवैध टोकन',
                    'details': debug_data.get('error_message', 'अज्ञात कारण')
                },
                'is_valid': False
            })
        
        # 2. परमिशन्स प्राप्त करें
        perm_url = f"https://graph.facebook.com/me/permissions?access_token={token}"
        perm_resp = requests.get(perm_url, timeout=10)
        permissions = []
        
        if perm_resp.status_code == 200:
            permissions = [
                p['permission'] for p in perm_resp.json().get('data', []) 
                if p['status'] == 'granted'
            ]
        
        # 3. बेसिक यूजर इन्फो
        user_url = f"https://graph.facebook.com/me?fields=id,name&access_token={token}"
        user_resp = requests.get(user_url, timeout=10)
        user_data = user_resp.json() if user_resp.status_code == 200 else {}
        
        # 4. अन्य डेटा (सावधानी से)
        data = {'user': user_data}
        
        # पोस्ट्स (अगर परमिशन है)
        if 'user_posts' in permissions:
            try:
                posts_url = f"https://graph.facebook.com/me/feed?fields=id,message,created_time&limit=3&access_token={token}"
                posts_resp = requests.get(posts_url, timeout=10)
                if posts_resp.status_code == 200:
                    data['posts'] = posts_resp.json().get('data', [])
            except:
                pass
        
        # फोटोज (अगर परमिशन है)
        if 'user_photos' in permissions:
            try:
                photos_url = f"https://graph.facebook.com/me/photos?fields=id,images,name&limit=3&access_token={token}"
                photos_resp = requests.get(photos_url, timeout=10)
                if photos_resp.status_code == 200:
                    data['photos'] = photos_resp.json().get('data', [])
            except:
                pass
        
        return jsonify({
            'token_type': debug_data.get('type'),
            'app_id': debug_data.get('app_id'),
            'user_id': debug_data.get('user_id'),
            'is_valid': debug_data.get('is_valid'),
            'expires_at': debug_data.get('expires_at'),
            'permissions': permissions,
            'data': data
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': {'message': 'Facebook API को कनेक्ट करने में टाइमआउट'}})
    except Exception as e:
        return jsonify({'error': {'message': str(e)}})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
