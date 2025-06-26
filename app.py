import re
import json
from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML इंटरफेस
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cookie Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        textarea { width: 100%; height: 200px; margin: 10px 0; }
        button { padding: 10px 15px; background: #4CAF50; color: white; border: none; }
    </style>
</head>
<body>
    <h2>Facebook Cookie Extractor</h2>
    <p>Monokai टूलकिट स्टाइल</p>
    
    <form method="POST">
        <textarea name="cookies" placeholder="यहाँ कुकीज पेस्ट करें..."></textarea><br>
        <button type="submit">कुकीज सेव करें</button>
    </form>
    
    {% if message %}
    <div style="color: {% if success %}green{% else %}red{% endif %}; margin-top: 20px;">
        {{ message }}
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    message = None
    success = False
    
    if request.method == 'POST':
        cookies = request.form.get('cookies', '')
        
        # कुकीज पार्स करना
        required_cookies = {
            'c_user': re.search(r'c_user=([^;]+)', cookies),
            'xs': re.search(r'xs=([^;]+)', cookies),
            'fr': re.search(r'fr=([^;]+)', cookies),
            'datr': re.search(r'datr=([^;]+)', cookies)
        }
        
        if all(required_cookies.values()):
            with open('cookies.txt', 'w') as f:
                f.write(f"c_user={required_cookies['c_user'].group(1)}; ")
                f.write(f"xs={required_cookies['xs'].group(1)}; ")
                f.write(f"fr={required_cookies['fr'].group(1)}; ")
                f.write(f"datr={required_cookies['datr'].group(1)}")
            
            message = "कुकीज सफलतापूर्वक सेव हो गईं!"
            success = True
        else:
            message = "त्रुटि: सभी आवश्यक कुकीज नहीं मिलीं (c_user, xs, fr, datr)"
    
    return render_template_string(HTML, message=message, success=success)

if __name__ == '__main__':
    app.run(port=4000)
