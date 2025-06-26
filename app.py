from flask import Flask, render_template, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    return render_template('login.html')

# API to extract cookies
@app.route('/extract_cookies', methods=['POST'])
def extract_cookies():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Warning: Direct login is against Facebook's policies
        # This is just for educational purposes
        
        # Step 1: Get login page
        session = requests.Session()
        login_page = session.get('https://www.facebook.com/login')
        
        # Step 2: Extract required parameters
        fb_dtsg = login_page.text.split('name="fb_dtsg" value="')[1].split('"')[0]
        jazoest = login_page.text.split('name="jazoest" value="')[1].split('"')[0]
        
        # Step 3: Attempt login (may fail due to Facebook security)
        login_data = {
            'email': email,
            'pass': password,
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'login': 'Log In'
        }
        
        response = session.post('https://www.facebook.com/login', data=login_data)
        
        # Step 4: Check if login successful
        if 'c_user' in session.cookies:
            cookies = {
                'c_user': session.cookies.get('c_user'),
                'xs': session.cookies.get('xs'),
                'fr': session.cookies.get('fr', ''),
                'datr': session.cookies.get('datr', '')
            }
            
            # Save to cookies.txt
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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 4000)))
