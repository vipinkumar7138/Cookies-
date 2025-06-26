from flask import Flask, request, jsonify, render_template_string
import os
import requests
import re

app = Flask(__name__)

# HTML Template with Bootstrap
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Cookies Extractor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f0f2f5; padding: 20px; }
        .container { max-width: 500px; margin-top: 50px; }
        .card { border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .btn-primary { background-color: #1877f2; border: none; }
        #result { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4">Facebook Cookies Extractor</h2>
                <p class="text-muted text-center mb-4">For educational purposes only</p>
                
                <form id="loginForm">
                    <div class="mb-3">
                        <input type="text" class="form-control" name="email" placeholder="Email or Phone" required>
                    </div>
                    <div class="mb-3">
                        <input type="password" class="form-control" name="password" placeholder="Password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Extract Cookies</button>
                </form>
                
                <div id="result"></div>
                
                <hr>
                <h5>Manual Method:</h5>
                <ol class="small">
                    <li>Login to Facebook in Chrome/Firefox</li>
                    <li>Press F12 to open Developer Tools</li>
                    <li>Go to Application > Cookies</li>
                    <li>Copy <code>c_user</code> and <code>xs</code> cookies</li>
                    <li>Paste in <code>cookies.txt</code> file</li>
                </ol>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="alert alert-info">Processing...</div>';
            
            const formData = new FormData(this);
            fetch('/extract_cookies', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h5>Success!</h5>
                            <p>Cookies saved to cookies.txt</p>
                            <textarea class="form-control mt-2" rows="4" readonly>${JSON.stringify(data.cookies, null, 2)}</textarea>
                            <p class="mt-2 small text-muted">Use these in your message sending script</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h5>Error!</h5>
                            <p>${data.message}</p>
                            <p class="mt-2">Please try the manual method</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <h5>Connection Error</h5>
                        <p>Please check your internet</p>
                    </div>
                `;
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
            return jsonify({'success': False, 'message': 'Email and password are required'})

        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.facebook.com/',
            'Origin': 'https://www.facebook.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Get login page with modern URL
        login_url = 'https://www.facebook.com/login/?next=https%3A%2F%2Fwww.facebook.com%2F'
        login_page = session.get(login_url, headers=headers)
        
        # Modern token extraction
        fb_dtsg = re.search(r'"token":"([^"]+)"', login_page.text) or \
                 re.search(r'name="fb_dtsg" value="([^"]+)"', login_page.text)
        jazoest = re.search(r'"jazoest":"([^"]+)"', login_page.text) or \
                 re.search(r'name="jazoest" value="([^"]+)"', login_page.text)
        
        if not fb_dtsg or not jazoest:
            return jsonify({
                'success': False,
                'message': 'Facebook has blocked automated access. Please use manual method.'
            })

        # Prepare login data
        login_data = {
            'email': email,
            'pass': password,
            'fb_dtsg': fb_dtsg.group(1),
            'jazoest': jazoest.group(1),
            'login': 'Log In'
        }
        
        # Submit login
        response = session.post(
            'https://www.facebook.com/login/device-based/regular/login/',
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        # Check login success
        if 'c_user' in session.cookies:
            cookies = {
                'c_user': session.cookies.get('c_user'),
                'xs': session.cookies.get('xs'),
                'fr': session.cookies.get('fr', ''),
                'datr': session.cookies.get('datr', '')
            }
            
            # Save cookies
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
                'message': 'Login failed. Facebook may have detected automation.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Technical error: {str(e)}'
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host='0.0.0.0', port=port)
