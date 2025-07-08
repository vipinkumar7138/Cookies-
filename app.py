from flask import Flask, request, jsonify, render_template_string, make_response
import requests
import os
from threading import Thread, Event
import time
import random
import string
import json
import datetime
from io import StringIO
import csv

app = Flask(__name__)
app.debug = True

# Global Variables
headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
}
stop_events = {}
threads = {}
report_stop_events = {}
report_threads = {}
auto_replies = {}
auto_reply_settings = {
    'active': False,
    'stop_event': Event()
}
logs = []

# Combined HTML Template
COMBINED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Triple VIP Tools</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        :root {
            --primary-color: #6c5ce7;
            --secondary-color: #a29bfe;
            --dark-color: #2d3436;
            --light-color: #f5f6fa;
            --success-color: #00b894;
            --danger-color: #d63031;
            --warning-color: #fdcb6e;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1e1e2f, #2d2d44);
            color: var(--light-color);
            min-height: 100vh;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Tab Styling */
        .tab-header {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--primary-color);
            flex-wrap: wrap;
        }
        
        .tab-btn {
            padding: 12px 25px;
            background: transparent;
            border: none;
            color: var(--light-color);
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            margin: 0 10px;
        }
        
        .tab-btn.active {
            color: var(--primary-color);
        }
        
        .tab-btn.active::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--primary-color);
            border-radius: 3px 3px 0 0;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Card Styling */
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card-title {
            font-size: 22px;
            margin-bottom: 20px;
            color: var(--primary-color);
            display: flex;
            align-items: center;
        }
        
        .card-title i {
            margin-right: 10px;
        }
        
        /* Form Styling */
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: var(--secondary-color);
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: var(--light-color);
            font-size: 15px;
            transition: all 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2);
        }
        
        /* Button Styling */
        .btn {
            display: inline-block;
            padding: 12px 25px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        
        .btn:hover {
            background: #5649d6;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
        }
        
        .btn-block {
            display: block;
            width: 100%;
        }
        
        .btn-danger {
            background: var(--danger-color);
        }
        
        .btn-danger:hover {
            background: #c0392b;
            box-shadow: 0 5px 15px rgba(214, 48, 49, 0.4);
        }
        
        .btn-warning {
            background: var(--warning-color);
            color: var(--dark-color);
        }
        
        .btn-warning:hover {
            background: #e6a336;
            box-shadow: 0 5px 15px rgba(253, 203, 110, 0.4);
        }
        
        /* Results Area */
        .results {
            margin-top: 20px;
        }
        
        .result-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 3px solid var(--primary-color);
        }
        
        .result-item h4 {
            margin-bottom: 10px;
            color: var(--secondary-color);
        }
        
        .copy-btn {
            background: var(--dark-color);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 13px;
            margin-top: 8px;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
        }
        
        .copy-btn i {
            margin-right: 5px;
        }
        
        .copy-btn:hover {
            background: var(--primary-color);
        }
        
        /* Notification */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            display: none;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-container {
                padding: 15px;
            }
            
            .card {
                padding: 20px;
            }
            
            .tab-btn {
                padding: 10px 15px;
                font-size: 14px;
                margin: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="tab-header">
            <button class="tab-btn active" onclick="openTool('tool1')">
                <i class="fas fa-id-card"></i> UID Extractor
            </button>
            <button class="tab-btn" onclick="openTool('tool2')">
                <i class="fas fa-paper-plane"></i> Message Sender
            </button>
            <button class="tab-btn" onclick="openTool('tool3')">
                <i class="fas fa-flag"></i> Auto Reporter
            </button>
            <button class="tab-btn" onclick="openTool('tool4')">
                <i class="fas fa-robot"></i> Auto Reply
            </button>
            <button class="tab-btn" onclick="openTool('tool5')">
                <i class="fas fa-clipboard-list"></i> VIP Logs
            </button>
        </div>
        
        <!-- UID Extractor Tool -->
        <div id="tool1" class="tab-content active">
            <div class="card">
                <h2 class="card-title"><i class="fas fa-id-card"></i> Facebook UID Extractor</h2>
                
                <div class="form-group">
                    <label class="form-label" for="access_token">Access Token</label>
                    <input type="text" id="access_token" class="form-control" placeholder="Enter your Facebook access token">
                </div>
                
                <div class="form-group">
                    <button class="btn btn-block" onclick="validateToken()">
                        <i class="fas fa-check-circle"></i> Validate Token
                    </button>
                </div>
                
                <div class="form-group">
                    <button class="btn btn-block" onclick="fetchMessengerChats()">
                        <i class="fas fa-comments"></i> Get Messenger Chats
                    </button>
                </div>
                
                <div class="form-group">
                    <button class="btn btn-block" onclick="fetchPosts()">
                        <i class="fas fa-newspaper"></i> Get Posts
                    </button>
                </div>
                
                <div id="tokenValidationResult" class="results"></div>
                <div id="results" class="results"></div>
            </div>
        </div>
        
        <!-- Message Sender Tool -->
        <div id="tool2" class="tab-content">
            <div class="card">
                <h2 class="card-title"><i class="fas fa-paper-plane"></i> Message Sender</h2>
                
                <form method="post" enctype="multipart/form-data" action="/send_message">
                    <div class="form-group">
                        <label class="form-label" for="tokenOption">Token Option</label>
                        <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
                            <option value="single">Single Token</option>
                            <option value="multiple">Token File</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="singleTokenInput">
                        <label class="form-label" for="singleToken">Facebook Token</label>
                        <input type="text" class="form-control" id="singleToken" name="singleToken">
                    </div>
                    
                    <div class="form-group" id="tokenFileInput" style="display: none;">
                        <label class="form-label" for="tokenFile">Token File</label>
                        <input type="file" class="form-control" id="tokenFile" name="tokenFile">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="uidOption">UID Option</label>
                        <select class="form-control" id="uidOption" name="uidOption" onchange="toggleUidInput()" required>
                            <option value="single">Single UID</option>
                            <option value="multiple">Multiple UIDs (File)</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="singleUidInput">
                        <label class="form-label" for="threadId">Conversation ID</label>
                        <input type="text" class="form-control" id="threadId" name="threadId">
                    </div>
                    
                    <div class="form-group" id="multipleUidInput" style="display: none;">
                        <label class="form-label" for="uidFile">UIDs File (CSV/TXT)</label>
                        <input type="file" class="form-control" id="uidFile" name="uidFile">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="kidx">Sender Name</label>
                        <input type="text" class="form-control" id="kidx" name="kidx" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="time">Time Interval (seconds)</label>
                        <input type="number" class="form-control" id="time" name="time" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="txtFile">Messages File</label>
                        <input type="file" class="form-control" id="txtFile" name="txtFile" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="mmm">Security Key</label>
                        <input type="text" class="form-control" id="mmm" name="mmm" required>
                    </div>
                    
                    <button type="submit" class="btn btn-block">
                        <i class="fas fa-play"></i> Start Sending
                    </button>
                </form>
                
                <form method="post" action="/stop" style="margin-top: 20px;">
                    <div class="form-group">
                        <label class="form-label" for="taskId">Task ID to Stop</label>
                        <input type="text" class="form-control" id="taskId" name="taskId" required>
                    </div>
                    <button type="submit" class="btn btn-block btn-danger">
                        <i class="fas fa-stop"></i> Stop Task
                    </button>
                </form>
            </div>
        </div>
        
        <!-- Auto Reporter Tool -->
        <div id="tool3" class="tab-content">
            <div class="card">
                <h2 class="card-title"><i class="fas fa-flag"></i> Auto Reporter</h2>
                
                <form method="post" enctype="multipart/form-data" action="/start_reporting">
                    <div class="form-group">
                        <label class="form-label" for="reportTokenOption">Token Option</label>
                        <select class="form-control" id="reportTokenOption" name="tokenOption" onchange="toggleReportTokenInput()" required>
                            <option value="single">Single Token</option>
                            <option value="multiple">Token File</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="reportSingleTokenInput">
                        <label class="form-label" for="reportSingleToken">Facebook Token</label>
                        <input type="text" class="form-control" id="reportSingleToken" name="singleToken">
                    </div>
                    
                    <div class="form-group" id="reportTokenFileInput" style="display: none;">
                        <label class="form-label" for="reportTokenFile">Token File</label>
                        <input type="file" class="form-control" id="reportTokenFile" name="tokenFile">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="targetId">Target ID/URL</label>
                        <input type="text" class="form-control" id="targetId" name="targetId" required placeholder="Post ID or Facebook URL">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reportReason">Report Reason</label>
                        <select class="form-control" id="reportReason" name="reportReason" required>
                            <option value="SPAM">Spam</option>
                            <option value="HATE_SPEECH">Hate Speech</option>
                            <option value="HARASSMENT">Harassment</option>
                            <option value="FALSE_NEWS">False Information</option>
                            <option value="VIOLENCE">Violence</option>
                            <option value="NUDITY">Nudity/Adult Content</option>
                            <option value="UNAUTHORIZED_SALE">Unauthorized Sale</option>
                            <option value="INFRINGEMENT">Intellectual Property Violation</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reportInterval">Time Interval (seconds)</label>
                        <input type="number" class="form-control" id="reportInterval" name="time" required min="5" value="10">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reportCount">Number of Reports</label>
                        <input type="number" class="form-control" id="reportCount" name="reportCount" required min="1" value="10">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reportSecurityKey">Security Key</label>
                        <input type="text" class="form-control" id="reportSecurityKey" name="mmm" required>
                    </div>
                    
                    <button type="submit" class="btn btn-block btn-warning">
                        <i class="fas fa-play"></i> Start Reporting
                    </button>
                </form>
                
                <form method="post" action="/stop_reporting" style="margin-top: 20px;">
                    <div class="form-group">
                        <label class="form-label" for="reportTaskId">Task ID to Stop</label>
                        <input type="text" class="form-control" id="reportTaskId" name="taskId" required>
                    </div>
                    <button type="submit" class="btn btn-block btn-danger">
                        <i class="fas fa-stop"></i> Stop Reporting Task
                    </button>
                </form>
            </div>
        </div>
        
        <!-- Auto Reply Tool (Updated) -->
        <div id="tool4" class="tab-content">
            <div class="card">
                <h2 class="card-title"><i class="fas fa-robot"></i> Auto Reply</h2>
                
                <form method="post" enctype="multipart/form-data" action="/set_auto_reply">
                    <div class="form-group">
                        <label class="form-label" for="auto_reply_token">Facebook Token</label>
                        <input type="text" class="form-control" id="auto_reply_token" name="auto_reply_token" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="messages_file">Messages File (TXT)</label>
                        <input type="file" class="form-control" id="messages_file" name="messages_file" required>
                        <small class="text-muted">Each line will be treated as a separate reply message</small>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="reply_mode">Reply Mode</label>
                        <select class="form-control" id="reply_mode" name="reply_mode" onchange="toggleGroupOptions()">
                            <option value="all">All Groups</option>
                            <option value="exclude">Exclude Specific Groups</option>
                            <option value="include">Include Specific Groups Only</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="group_ids_section" style="display: none;">
                        <label class="form-label" for="group_ids">Group IDs (Comma Separated)</label>
                        <input type="text" class="form-control" id="group_ids" name="group_ids" placeholder="e.g., 123456789,987654321">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="keyword">Trigger Keyword</label>
                        <input type="text" class="form-control" id="keyword" name="keyword" placeholder="e.g., 'hello' or 'help'" required>
                    </div>
                    
                    <button type="submit" class="btn btn-block">
                        <i class="fas fa-save"></i> Save Auto Reply Settings
                    </button>
                </form>
                
                <form method="post" action="/start_auto_reply" style="margin-top: 20px;">
                    <button type="submit" class="btn btn-block">
                        <i class="fas fa-play"></i> Start Auto Reply
                    </button>
                </form>
                
                <form method="post" action="/stop_auto_reply" style="margin-top: 20px;">
                    <button type="submit" class="btn btn-block btn-danger">
                        <i class="fas fa-stop"></i> Stop Auto Reply
                    </button>
                </form>
                
                <div id="autoReplyStatus" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <!-- VIP Logs Tool -->
        <div id="tool5" class="tab-content">
            <div class="card">
                <h2 class="card-title"><i class="fas fa-clipboard-list"></i> VIP Logs</h2>
                
                <div class="form-group">
                    <button class="btn btn-block" onclick="loadLogs()">
                        <i class="fas fa-sync-alt"></i> Refresh Logs
                    </button>
                </div>
                
                <div class="form-group">
                    <button class="btn btn-block btn-warning" onclick="downloadLogs()">
                        <i class="fas fa-download"></i> Download Logs (CSV)
                    </button>
                </div>
                
                <div id="logsContainer" class="results"></div>
            </div>
        </div>
    </div>
    
    <!-- Notification Div -->
    <div id="notification" class="notification">
        <i class="fas fa-check-circle"></i> <span id="notification-text">Copied to clipboard!</span>
    </div>
    
    <script>
    // Tab switching function
    function openTool(toolId) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Deactivate all tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(toolId).classList.add('active');
        
        // Activate selected button
        event.currentTarget.classList.add('active');
    }
    
    // Show notification function
    function showNotification(message) {
        const notification = document.getElementById('notification');
        const notificationText = document.getElementById('notification-text');
        
        notificationText.textContent = message;
        notification.style.display = 'flex';
        
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    // Token validation function
    function validateToken() {
        const accessToken = document.getElementById("access_token").value.trim();
        if (!accessToken) {
            showError("Please enter a valid access token");
            return;
        }

        fetch('/validate_token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: accessToken })
        })
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById("tokenValidationResult");
            if (data.error) {
                resultDiv.innerHTML = `
                    <div class="result-item" style="border-left-color: var(--danger-color);">
                        <h4 style="color: var(--danger-color);">Invalid Token ❌</h4>
                        <p>${data.error.message || "This token is invalid or expired."}</p>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = `
                    <div class="result-item" style="border-left-color: var(--success-color);">
                        <h4 style="color: var(--success-color);">Valid Token ✅</h4>
                        <p><strong>Profile Name:</strong> ${data.name}</p>
                        <p><strong>Facebook ID:</strong> ${data.id}</p>
                        <button class="copy-btn" onclick="copyToClipboard('${data.id}', 'Facebook ID copied!')">
                            <i class="fas fa-copy"></i> Copy ID
                        </button>
                    </div>
                `;
            }
        })
        .catch(error => {
            showError("Error validating token. Please try again.");
        });
    }

    // UID Extractor Functions
    function fetchMessengerChats() {
        const accessToken = document.getElementById("access_token").value.trim();
        if (!accessToken) {
            showError("Please enter a valid access token");
            return;
        }

        fetch('/get_messenger_chats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: accessToken })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = '';
            
            if (data.error) {
                showError(`Error: ${data.error.message || data.error}`);
            } else {
                if (data.chats && data.chats.length > 0) {
                    data.chats.forEach(chat => {
                        const chatDiv = document.createElement("div");
                        chatDiv.className = "result-item";
                        chatDiv.innerHTML = `
                            <h4>${chat.name || 'Unnamed Chat'}</h4>
                            <p><strong>Chat UID:</strong> ${chat.id}</p>
                            <button class="copy-btn" onclick="copyToClipboard('${chat.id.replace(/'/g, "\\'")}', 'Chat UID copied!')">
                                <i class="fas fa-copy"></i> Copy UID
                            </button>
                        `;
                        resultsDiv.appendChild(chatDiv);
                    });
                } else {
                    showError("No chats found");
                }
            }
        })
        .catch(error => {
            showError(`Error: ${error.message}`);
            console.error('Error:', error);
        });
    }

    function fetchPosts() {
        const accessToken = document.getElementById("access_token").value.trim();
        if (!accessToken) {
            showError("Please enter a valid access token");
            return;
        }

        fetch('/get_posts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_token: accessToken })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = '';
            
            if (data.error) {
                showError(`Error: ${data.error.message || data.error}`);
            } else {
                if (data.posts && data.posts.length > 0) {
                    data.posts.forEach(post => {
                        const postDiv = document.createElement("div");
                        postDiv.className = "result-item";
                        postDiv.innerHTML = `
                            <h4>${post.name || 'Unnamed Post'}</h4>
                            <p><strong>Post UID:</strong> ${post.id}</p>
                            <p><strong>Profile:</strong> ${post.profile_name}</p>
                            <button class="copy-btn" onclick="copyToClipboard('${post.id.replace(/'/g, "\\'")}', 'Post UID copied!')">
                                <i class="fas fa-copy"></i> Copy UID
                            </button>
                        `;
                        resultsDiv.appendChild(postDiv);
                    });
                } else {
                    showError("No posts found");
                }
            }
        })
        .catch(error => {
            showError(`Error: ${error.message}`);
            console.error('Error:', error);
        });
    }

    // Clipboard function
    function copyToClipboard(text, message) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showNotification(message || "Copied to clipboard!");
            } else {
                showNotification("Failed to copy!");
            }
        } catch (err) {
            console.error('Could not copy text: ', err);
            showNotification("Failed to copy!");
        }
        
        document.body.removeChild(textarea);
    }

    function showError(message) {
        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = `
            <div class="result-item" style="border-left-color: var(--danger-color);">
                <h4 style="color: var(--danger-color);">Error</h4>
                <p>${message}</p>
            </div>
        `;
    }

    // Message Sender Functions
    function toggleTokenInput() {
        const tokenOption = document.getElementById('tokenOption').value;
        if (tokenOption === 'single') {
            document.getElementById('singleTokenInput').style.display = 'block';
            document.getElementById('tokenFileInput').style.display = 'none';
        } else {
            document.getElementById('singleTokenInput').style.display = 'none';
            document.getElementById('tokenFileInput').style.display = 'block';
        }
    }

    // UID Input Toggle Function
    function toggleUidInput() {
        const uidOption = document.getElementById('uidOption').value;
        if (uidOption === 'single') {
            document.getElementById('singleUidInput').style.display = 'block';
            document.getElementById('multipleUidInput').style.display = 'none';
        } else {
            document.getElementById('singleUidInput').style.display = 'none';
            document.getElementById('multipleUidInput').style.display = 'block';
        }
    }

    // Auto Reporter Functions
    function toggleReportTokenInput() {
        const tokenOption = document.getElementById('reportTokenOption').value;
        if (tokenOption === 'single') {
            document.getElementById('reportSingleTokenInput').style.display = 'block';
            document.getElementById('reportTokenFileInput').style.display = 'none';
        } else {
            document.getElementById('reportSingleTokenInput').style.display = 'none';
            document.getElementById('reportTokenFileInput').style.display = 'block';
        }
    }

    // Auto Reply Functions
    function toggleGroupOptions() {
        const replyMode = document.getElementById('reply_mode').value;
        const groupIdsSection = document.getElementById('group_ids_section');
        
        if (replyMode === 'all') {
            groupIdsSection.style.display = 'none';
        } else {
            groupIdsSection.style.display = 'block';
        }
    }

    // Load Logs Function
    function loadLogs() {
        fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logsContainer');
            logsContainer.innerHTML = '';
            
            if (data.logs.length === 0) {
                logsContainer.innerHTML = '<div class="result-item">No logs found.</div>';
                return;
            }
            
            data.logs.forEach(log => {
                const logDiv = document.createElement('div');
                logDiv.className = 'result-item';
                logDiv.innerHTML = `
                    <h4>${log.action} (${log.status})</h4>
                    <p><strong>Time:</strong> ${log.timestamp}</p>
                    <p><strong>Details:</strong> ${log.details}</p>
                `;
                logsContainer.appendChild(logDiv);
            });
        });
    }

    // Download Logs Function
    function downloadLogs() {
        fetch('/download_logs')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'vip_logs.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }

    // Load logs when page loads if on logs tab
    window.onload = function() {
        if (window.location.hash === '#tool5') {
            loadLogs();
        }
    };
    </script>
</body>
</html>
"""

# ---------------------- Flask Routes ----------------------
@app.route('/')
def home():
    return render_template_string(COMBINED_HTML)

# Token Validator Route
@app.route('/validate_token', methods=['POST'])
def validate_token():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': {'message': 'No token provided'}})
        
        response = requests.get(
            f'https://graph.facebook.com/me?fields=name,id&access_token={access_token}',
            timeout=10
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Invalid or expired token',
                    'details': error_data.get('error', {}).get('message', 'Unknown error')
                }
            })
        
        return jsonify(response.json())
        
    except requests.exceptions.Timeout:
        return jsonify({'error': {'message': 'Request timed out. Try again.'}})
    except Exception as e:
        return jsonify({'error': {'message': str(e)}})

# UID Extractor Routes
@app.route('/get_messenger_chats', methods=['POST'])
def get_messenger_chats():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'No access token provided'})
        
        response = requests.get(
            f'https://graph.facebook.com/me/conversations?fields=participants,name&access_token={access_token}',
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Invalid access token',
                    'details': error_data.get('error', {}).get('message', 'Unknown error')
                }
            })
        
        chats = []
        for chat in response.json().get('data', []):
            chat_name = chat.get('name') or ', '.join(
                [p['name'] for p in chat.get('participants', {}).get('data', [])]
            )
            chats.append({
                'id': chat['id'],
                'name': chat_name
            })
            
        return jsonify({'chats': chats})
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_posts', methods=['POST'])
def get_posts():
    try:
        access_token = request.json.get('access_token')
        if not access_token:
            return jsonify({'error': 'No access token provided'})
        
        response = requests.get(
            f'https://graph.facebook.com/me/feed?fields=id,message,from&limit=20&access_token={access_token}',
            timeout=30
        )
        
        if response.status_code != 200:
            error_data = response.json()
            return jsonify({
                'error': {
                    'message': 'Invalid access token',
                    'details': error_data.get('error', {}).get('message', 'Unknown error')
                }
            })
        
        posts = []
        for post in response.json().get('data', []):
            posts.append({
                'id': post['id'],
                'name': post.get('message', 'No text content'),
                'profile_name': post.get('from', {}).get('name', 'Unknown')
            })
            
        return jsonify({'posts': posts})
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Message Sender Routes
@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        uid_option = request.form.get('uidOption')

        # Load tokens
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        # Load UIDs
        if uid_option == 'single':
            thread_ids = [request.form.get('threadId')]
        else:
            uid_file = request.files['uidFile']
            thread_ids = uid_file.read().decode().strip().splitlines()

        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        password = request.form.get('mmm')
        mmm = requests.get('https://pastebin.com/raw/tn5e8Ub9').text.strip()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_ids, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        add_log("Message Task Started", "Success", f"Task ID: {task_id}, UIDs: {len(thread_ids)}")
        return f'Task started with ID: {task_id}'

def send_messages(access_tokens, thread_ids, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                for thread_id in thread_ids:
                    api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                    message = str(mn) + ' ' + message1
                    parameters = {'access_token': access_token, 'message': message}
                    try:
                        response = requests.post(api_url, data=parameters, headers=headers)
                        if response.status_code == 200:
                            add_log("Message Sent", "Success", f"Token: {access_token}, UID: {thread_id}")
                        else:
                            add_log("Message Failed", "Failed", f"Token: {access_token}, UID: {thread_id}, Error: {response.text}")
                    except Exception as e:
                        add_log("Message Error", "Error", str(e))
                    time.sleep(time_interval)

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

# Auto Reporter Routes
@app.route('/start_reporting', methods=['POST'])
def start_reporting():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')

        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        target_id = request.form.get('targetId')
        report_reason = request.form.get('reportReason')
        time_interval = int(request.form.get('time'))
        report_count = int(request.form.get('reportCount'))

        password = request.form.get('mmm')
        mmm = requests.get('https://pastebin.com/raw/tn5e8Ub9').text.strip()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        report_stop_events[task_id] = Event()
        thread = Thread(target=send_reports, args=(access_tokens, target_id, report_reason, time_interval, report_count, task_id))
        report_threads[task_id] = thread
        thread.start()

        add_log("Reporting Task Started", "Success", f"Task ID: {task_id}, Target: {target_id}")
        return f'Reporting task started with ID: {task_id}'

@app.route('/stop_reporting', methods=['POST'])
def stop_reporting():
    task_id = request.form.get('taskId')
    if task_id in report_stop_events:
        report_stop_events[task_id].set()
        return f'Reporting task with ID {task_id} has been stopped.'
    else:
        return f'No reporting task found with ID {task_id}.'

def send_reports(access_tokens, target_id, report_reason, time_interval, report_count, task_id):
    stop_event = report_stop_events[task_id]
    reports_sent = 0
    
    while not stop_event.is_set() and reports_sent < report_count:
        for access_token in access_tokens:
            if stop_event.is_set() or reports_sent >= report_count:
                break
                
            try:
                object_id = target_id
                if 'facebook.com' in target_id:
                    object_id = target_id.split('/')[-1].split('?')[0]
                
                api_url = f'https://graph.facebook.com/v15.0/{object_id}/reports'
                parameters = {
                    'access_token': access_token,
                    'reason': report_reason
                }
                
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    add_log("Report Sent", "Success", f"Token: {access_token}, Target: {target_id}")
                    reports_sent += 1
                else:
                    add_log("Report Failed", "Failed", f"Token: {access_token}, Target: {target_id}, Error: {response.text}")
                
                time.sleep(time_interval)
                
            except Exception as e:
                add_log("Report Error", "Error", str(e))
                continue

# Auto Reply Routes (Updated)
@app.route('/set_auto_reply', methods=['POST'])
def set_auto_reply():
    try:
        access_token = request.form.get('auto_reply_token')
        keyword = request.form.get('keyword')
        reply_mode = request.form.get('reply_mode')
        group_ids = request.form.get('group_ids', '').split(',') if request.form.get('group_ids') else []
        
        # Process messages file
        messages_file = request.files['messages_file']
        messages = messages_file.read().decode().splitlines()
        
        # Save settings
        auto_reply_settings.update({
            'access_token': access_token,
            'keyword': keyword,
            'messages': messages,
            'reply_mode': reply_mode,
            'group_ids': [gid.strip() for gid in group_ids if gid.strip()],
            'active': False,
            'stop_event': Event()
        })
        
        add_log("Auto Reply Settings Saved", "Success", 
               f"Mode: {reply_mode}, Groups: {group_ids if group_ids else 'All'}")
        
        return "Auto Reply Settings Saved Successfully!"
    
    except Exception as e:
        add_log("Auto Reply Settings Error", "Error", str(e))
        return f"Error: {str(e)}", 400

@app.route('/start_auto_reply', methods=['POST'])
def start_auto_reply():
    if not auto_reply_settings or 'access_token' not in auto_reply_settings:
        return "Auto reply settings not configured", 400
    
    if auto_reply_settings.get('active', False):
        return "Auto reply is already running", 200
    
    auto_reply_settings['active'] = True
    auto_reply_settings['stop_event'].clear()
    
    thread = Thread(target=run_auto_reply, args=(auto_reply_settings,))
    thread.start()
    
    add_log("Auto Reply Started", "Success", 
           f"Mode: {auto_reply_settings['reply_mode']}, Groups: {auto_reply_settings['group_ids']}")
    
    return "Auto reply started successfully"

@app.route('/stop_auto_reply', methods=['POST'])
def stop_auto_reply():
    if not auto_reply_settings:
        return "Auto reply settings not configured", 400
    
    if not auto_reply_settings.get('active', False):
        return "Auto reply is not running", 200
    
    auto_reply_settings['active'] = False
    auto_reply_settings['stop_event'].set()
    
    add_log("Auto Reply Stopped", "Success", "Auto reply service stopped")
    return "Auto reply stopped successfully"

def run_auto_reply(settings):
    access_token = settings['access_token']
    keyword = settings['keyword']
    messages = settings['messages']
    reply_mode = settings['reply_mode']
    group_ids = settings['group_ids']
    stop_event = settings['stop_event']
    
    while not stop_event.is_set() and settings['active']:
        try:
            # Get all conversations
            response = requests.get(
                f'https://graph.facebook.com/me/conversations?fields=participants,messages{{message}}&access_token={access_token}',
                timeout=30
            )
            
            if response.status_code != 200:
                add_log("Auto Reply Error", "Error", f"Failed to fetch conversations: {response.text}")
                time.sleep(60)
                continue
            
            conversations = response.json().get('data', [])
            
            for conv in conversations:
                if stop_event.is_set() or not settings['active']:
                    break
                
                conv_id = conv['id']
                
                # Check group inclusion/exclusion
                if reply_mode == 'exclude' and conv_id in group_ids:
                    continue
                if reply_mode == 'include' and conv_id not in group_ids:
                    continue
                
                # Check last message for keyword
                messages_data = conv.get('messages', {}).get('data', [])
                if not messages_data:
                    continue
                
                last_message = messages_data[0].get('message', '')
                if keyword.lower() in last_message.lower():
                    # Send random reply
                    reply_msg = random.choice(messages)
                    api_url = f'https://graph.facebook.com/v15.0/t_{conv_id}/'
                    parameters = {'access_token': access_token, 'message': reply_msg}
                    
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        add_log("Auto Reply Sent", "Success", f"Group: {conv_id}, Message: {reply_msg[:50]}...")
                    else:
                        add_log("Auto Reply Failed", "Error", f"Group: {conv_id}, Error: {response.text}")
                    
                    time.sleep(5)  # Small delay between replies
            
            time.sleep(30)  # Check for new messages every 30 seconds
            
        except Exception as e:
            add_log("Auto Reply Error", "Error", str(e))
            time.sleep(60)

# Logging System
def add_log(action, status, details):
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "action": action,
        "status": status,
        "details": details
    }
    logs.append(log_entry)
    # Save to file (optional)
    with open("logs.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": logs})

@app.route('/download_logs')
def download_logs():
    # Create CSV data
    csv_data = StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(["Timestamp", "Action", "Status", "Details"])
    
    for log in logs:
        writer.writerow([log['timestamp'], log['action'], log['status'], log['details']])
    
    response = make_response(csv_data.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=vip_logs.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
