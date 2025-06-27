# app.py - Updated and Tested for Render
from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MonokaiToolkit से Facebook टोकन एक्सट्रैक्टर</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 200px; margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>MonokaiToolkit Cookie से Facebook टोकन निकालें</h2>
        <form method="POST">
            <textarea name="cookies" placeholder="MonokaiToolkit की कुकीज़ यहाँ पेस्ट करें..."></textarea>
            <button type="submit">टोकन निकालें</button>
        </form>
        {% if result %}
        <div class="result">
            <h3>परिणाम:</h3>
            <pre>{{ result }}</pre>
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
        token_pattern = r'(EAAd\w+|EAA\d\w+)'
        matches = re.findall(token_pattern, cookies)
        result = "\n".join(set(matches)) if matches else "कोई Facebook टोकन नहीं मिला"

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
