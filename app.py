# app.py (Flask बैकेंड + HTML फ्रंटेंड)
from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MonokaiToolkit से Facebook टोकन एक्सट्रैक्टर</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 200px;
            margin-bottom: 15px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MonokaiToolkit Cookie से Facebook टोकन निकालें</h1>
        <p>MonokaiToolkit ऐप से कॉपी किए गए कुकीज़ को नीचे पेस्ट करें:</p>
        
        <form method="POST">
            <textarea name="cookies" placeholder="यहां कुकीज़ पेस्ट करें..."></textarea>
            <br>
            <button type="submit">टोकन निकालें</button>
        </form>
        
        {% if result %}
        <div class="result">
            <h3>परिणाम:</h3>
            <p>{{ result }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        cookies = request.form.get('cookies', '')
        # Facebook टोकन निकालने का पैटर्न
        token_pattern = r'(EAAd\w+|EAA\d\w+)'
        matches = re.findall(token_pattern, cookies)
        
        if matches:
            unique_tokens = list(set(matches))  # डुप्लीकेट टोकन हटाएं
            result = "मिले Facebook टोकन:\n\n" + "\n".join(unique_tokens)
        else:
            result = "कोई Facebook टोकन नहीं मिला। कृपया सही कुकीज़ चेक करें।"
    
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
