from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def check_facebook_token(token):
    """Check if a Facebook token is valid"""
    try:
        # Basic token check using Graph API
        url = f"https://graph.facebook.com/v19.0/me?access_token={token}"
        response = requests.get(url)
        data = response.json()
        
        if 'error' in data:
            return {
                'valid': False,
                'error': data['error']['message'],
                'type': data['error'].get('type', 'Unknown')
            }
        else:
            return {
                'valid': True,
                'user_id': data.get('id'),
                'name': data.get('name')
            }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'type': 'Request Error'
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        if token:
            result = check_facebook_token(token)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
