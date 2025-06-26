from flask import Flask, request, jsonify, render_template_string
import os
import requests
import re

app = Flask(__name__)

# HTML कोड सीधे Python में
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Cookies Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; }
        .container { background: #f0f2f5; padding: 20px; border-radius: 8px; }
        input { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; }
        button { background: #1877f2; color: white; border: none; padding: 10px; width: 100%; border-radius: 4px; }
        #result { margin-top: 20px; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Facebook Cookies Extractor</h2>
        <p><strong>Note:</strong> For educational purposes only</p>
        
        <form id="loginForm">
            <input type="text" name="email" placeholder="Email or Phone" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Extract Cookies</button>
        </form>
        
        <div id="result"></div>
        
        <h3>Manual Method:</h3>
        <ol>
            <li>Facebook पर लॉगिन करें</li>
            <li>Chrome/Firefox में F12 दबाएं</li>
            <li>Application > Cookies पर जाएं</li>
            <li><code>c_user</code> और <code>xs</code> कुकीज कॉपी करें</li>
            <li><code>cookies.txt</code> फाइल में पेस्ट करें</li>
        </ol>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch('/extract_cookies', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                resultDiv.className = data.success ? 'success' : 'error';
                
                if(data.success) {
                    resultDiv.innerHTML = `
                        <h3>Success!</h3>
                        <p>Cookies saved to cookies.txt</p>
                        <textarea style="width:100%; height:100px;">${JSON.stringify(data.cookies, null, 2)}</textarea>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <h3>Error!</h3>
                        <p>${data.message}</p>
                        <p>Manual method try करें</p>
                    `;
                }
            });
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract_cookies', methods=['POST'])
def extract_cookies():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            })

        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        login_page = session.get('https://www.facebook.com/login', headers=headers)
        
        fb_dtsg = re.search(r'name="fb_dtsg" value="([^"]+)"', login_page.text)
        jazoest = re.search(r'name="jazoest" value="([^"]+)"', login_page.text)
        
        if not fb_dtsg or not jazoest:
            return jsonify({
                'success': False,
                'message': 'Failed to extract Facebook tokens'
            })

        login_data = {
            'email': email,
            'pass': password,
            'fb_dtsg': fb_dtsg.group(1),
            'jazoest': jazoest.group(1),
            'login': 'Log In'
        }
        
        response = session.post('https://www.facebook.com/login', data=login_data, headers=headers)
        
        if 'c_user' in session.cookies:
            cookies = {
                'c_user': session.cookies.get('c_user'),
                'xs': session.cookies.get('xs'),
                'fr': session.cookies.get('fr', ''),
                'datr': session.cookies.get('datr', '')
            }
            
            with open('cookies.txt', 'w') as f:
                f.write(f"c_user={cookies['c_user']}; xs={cookies['xs']}; fr={cookies['fr']}; datr={cookies['datr']}")
            
            return jsonify({
                'success': True,
                'cookies': cookies,
                'message': 'Cookies extracted successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Login failed. Check credentials or try manual method.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host='0.0.0.0', port=port)
