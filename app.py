from flask import Flask, render_template_string, request, jsonify
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure rate limiting (200 requests/day, 50/hour)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Template (Improved UI)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Messenger Group UID Extractor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f0f2f5;
            font-family: 'Segoe UI', sans-serif;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .btn-primary {
            background-color: #1877f2;
        }
        #loader {
            display: none;
        }
        .group-item {
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="card p-4 mx-auto" style="max-width: 500px;">
            <h2 class="text-center mb-4">Messenger Group UID Extractor</h2>
            
            <div class="mb-3">
                <label for="access-token" class="form-label">Facebook Access Token:</label>
                <input type="text" class="form-control" id="access-token" placeholder="EAAD...">
                <small class="text-muted">Token must start with <code>EAAD</code></small>
            </div>
            
            <button class="btn btn-primary w-100" onclick="extractGroups()">Extract Group UIDs</button>
            
            <div id="loader" class="text-center my-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p id="progress-text" class="mt-2">0%</p>
            </div>
            
            <div id="error" class="alert alert-danger mt-3" style="display: none;"></div>
            
            <div id="result" class="mt-3"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function extractGroups() {
            const token = document.getElementById('access-token').value.trim();
            const loader = document.getElementById('loader');
            const errorDiv = document.getElementById('error');
            const resultDiv = document.getElementById('result');
            
            if (!token || !token.startsWith('EAAD')) {
                showError('Invalid token format. Must start with EAAD');
                return;
            }
            
            // Reset UI
            errorDiv.style.display = 'none';
            resultDiv.innerHTML = '';
            loader.style.display = 'block';
            
            // Simulate progress (optional)
            let progress = 0;
            const progressText = document.getElementById('progress-text');
            const progressInterval = setInterval(() => {
                progress += 10;
                progressText.textContent = `${progress}%`;
                if (progress >= 100) clearInterval(progressInterval);
            }, 300);
            
            fetch('/extract-groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ access_token: token })
            })
            .then(response => response.json())
            .then(data => {
                clearInterval(progressInterval);
                loader.style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data.groups || []);
                }
            })
            .catch(error => {
                clearInterval(progressInterval);
                loader.style.display = 'none';
                showError('Failed to fetch data. Try again later.');
            });
        }
        
        function displayResults(groups) {
            const resultDiv = document.getElementById('result');
            
            if (groups.length === 0) {
                resultDiv.innerHTML = '<div class="alert alert-info">No groups found.</div>';
                return;
            }
            
            let html = '<h5 class="mb-3">Your Groups:</h5>';
            groups.forEach(group => {
                html += `
                    <div class="group-item">
                        <p><strong>ID:</strong> <code>${group.id}</code></p>
                        <p><strong>Name:</strong> ${group.name || 'N/A'}</p>
                    </div>
                `;
            });
            
            html += `<button class="btn btn-sm btn-success mt-3" onclick="copyToClipboard()">Copy Results</button>`;
            resultDiv.innerHTML = html;
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        function copyToClipboard() {
            const resultDiv = document.getElementById('result');
            const text = resultDiv.innerText;
            navigator.clipboard.writeText(text)
                .then(() => alert('Copied to clipboard!'))
                .catch(() => alert('Failed to copy.'));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/extract-groups', methods=['POST'])
@limiter.limit("10 per minute")  # Prevent API abuse
def extract_groups():
    token = request.json.get('access_token')
    
    if not token or not token.startswith('EAAD'):
        return jsonify({"error": "Invalid token format. Must start with 'EAAD'."})
    
    try:
        # Step 1: Validate token
        user_info = requests.get(
            f"https://graph.facebook.com/v12.0/me?access_token={token}",
            timeout=10  # Avoid hanging requests
        ).json()
        
        if "error" in user_info:
            return jsonify({"error": f"Invalid token: {user_info['error']['message']}"})
        
        # Step 2: Fetch groups (with pagination)
        groups_url = f"https://graph.facebook.com/v12.0/me/conversations?fields=id,name&access_token={token}"
        groups = []
        
        while groups_url:
            response = requests.get(groups_url, timeout=10).json()
            if "error" in response:
                return jsonify({"error": response['error']['message']})
            
            groups.extend(response.get("data", []))
            groups_url = response.get("paging", {}).get("next", None)
        
        return jsonify({"groups": groups})
    
    except requests.Timeout:
        return jsonify({"error": "Facebook API timeout. Try again later."})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Server error. Please try again."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
