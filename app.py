from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# HTML इंटरफेस
HTML = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Facebook Cookie Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #1877f2; text-align: center; }
        .form-group { margin-bottom: 15px; }
        input, button { width: 100%; padding: 10px; margin-top: 5px; }
        button { background: #1877f2; color: white; border: none; cursor: pointer; }
        #result { margin-top: 20px; display: none; }
        textarea { width: 100%; height: 100px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Cookie Extractor</h1>
        <div class="form-group">
            <label>Email/Phone:</label>
            <input type="text" id="email" placeholder="Enter email/phone">
        </div>
        <div class="form-group">
            <label>Password:</label>
            <input type="password" id="password" placeholder="Enter password">
        </div>
        <button id="extract-btn">Extract Cookies</button>
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('extract-btn').addEventListener('click', async () => {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if(!email || !password) {
                alert('Please enter both email and password');
                return;
            }

            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({email, password})
                });
                const data = await response.json();
                
                if(data.status === 'success') {
                    document.getElementById('result').innerHTML = `
                        <h3>Success!</h3>
                        <textarea readonly>${data.cookies}</textarea>
                    `;
                    document.getElementById('result').style.display = 'block';
                } else {
                    alert('Error: ' + data.message);
                }
            } catch(error) {
                alert('Error: ' + error);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML

@app.route('/extract', methods=['POST'])
def extract_cookies():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        # Chrome सेटअप
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        # Facebook लॉगिन
        driver.get("https://facebook.com")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)

        # कुकीज एक्सट्रेक्ट
        cookies = driver.get_cookies()
        driver.quit()

        # फॉर्मेट करें
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        return jsonify({
            "status": "success",
            "cookies": cookie_str
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
