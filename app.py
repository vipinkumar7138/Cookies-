from flask import Flask, request, jsonify, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# HTML और JavaScript कोड
HTML = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook कुकी एक्सट्रैक्टर</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f2f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #1877f2;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 16px;
        }
        button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 12px;
            width: 100%;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #166fe5;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            background-color: #f0f2f5;
            display: none;
        }
        .success {
            color: green;
        }
        .error {
            color: red;
        }
        textarea {
            width: 100%;
            height: 150px;
            margin-top: 10px;
            padding: 10px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook कुकी एक्सट्रैक्टर</h1>
        <div class="form-group">
            <label for="email">ईमेल या फोन नंबर</label>
            <input type="text" id="email" placeholder="अपना ईमेल या फोन नंबर डालें">
        </div>
        <div class="form-group">
            <label for="password">पासवर्ड</label>
            <input type="password" id="password" placeholder="अपना पासवर्ड डालें">
        </div>
        <button id="extract-btn">कुकीज़ निकालें</button>
        
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('extract-btn').addEventListener('click', function() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showResult('error', 'कृपया ईमेल और पासवर्ड दोनों डालें');
                return;
            }
            
            const formData = new FormData();
            formData.append('email', email);
            formData.append('password', password);
            
            fetch('/extract_cookies', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const resultDiv = document.getElementById('result');
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'success';
                    
                    let html = '<h3>कुकीज़ सफलतापूर्वक निकाली गई!</h3>';
                    html += '<h4>कुकी स्ट्रिंग:</h4>';
                    html += `<textarea readonly>${data.cookie_string}</textarea>`;
                    html += '<h4>अलग-अलग कुकीज़:</h4>';
                    html += `<textarea readonly>${JSON.stringify(data.cookies, null, 2)}</textarea>`;
                    
                    resultDiv.innerHTML = html;
                } else {
                    showResult('error', data.message);
                }
            })
            .catch(error => {
                showResult('error', 'एरर आया: ' + error.message);
            });
        });
        
        function showResult(type, message) {
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.className = type;
            resultDiv.innerHTML = message;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/extract_cookies', methods=['POST'])
def extract_cookies():
    try:
        email = request.form['email']
        password = request.form['password']
        
        # Chrome सेटिंग
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Chrome ड्राइवर शुरू करें
        driver = webdriver.Chrome(options=chrome_options)
        
        # Facebook खोलें
        driver.get("https://www.facebook.com")
        
        # लॉगिन फॉर्म भरें
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.ID, "pass")
        password_field.send_keys(password)
        
        # लॉगिन बटन दबाएं
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        
        # लॉगिन होने का इंतजार करें
        time.sleep(5)
        
        # चेक करें कि लॉगिन हुआ या नहीं
        if "login" in driver.current_url.lower():
            driver.quit()
            return jsonify({"status": "error", "message": "लॉगिन असफल। कृपया अपना ईमेल और पासवर्ड चेक करें।"})
        
        # कुकीज़ प्राप्त करें
        cookies = driver.get_cookies()
        
        # कुकीज़ फॉर्मेट करें
        formatted_cookies = {}
        for cookie in cookies:
            formatted_cookies[cookie['name']] = cookie['value']
        
        driver.quit()
        
        return jsonify({
            "status": "success",
            "cookies": formatted_cookies,
            "cookie_string": "; ".join([f"{k}={v}" for k, v in formatted_cookies.items()])
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
