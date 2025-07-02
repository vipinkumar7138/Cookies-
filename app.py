#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template_string
import pytube
from instaloader import Instaloader, Post
from facebook_scraper import get_posts
import os
import re

app = Flask(__name__)

# HTML टेम्पलेट
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>सोशल मीडिया डाउनलोडर</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 16px;
            transition: 0.3s;
            font-size: 16px;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px 0;
            border-top: none;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            display: inline-block;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #e8f5e9;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #4CAF50;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .video-info {
            margin-top: 15px;
        }
        .thumbnail {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
        .download-btn {
            background-color: #2196F3;
            margin-top: 10px;
        }
        .download-btn:hover {
            background-color: #0b7dda;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>सोशल मीडिया डाउनलोडर</h1>
        
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'youtube')">YouTube</button>
            <button class="tablinks" onclick="openTab(event, 'instagram')">Instagram</button>
            <button class="tablinks" onclick="openTab(event, 'facebook')">Facebook</button>
        </div>
        
        <div id="youtube" class="tabcontent" style="display: block;">
            <h2>YouTube वीडियो डाउनलोडर</h2>
            <form action="/download/youtube" method="post">
                <input type="text" name="url" placeholder="YouTube वीडियो URL डालें..." required>
                <select name="format" style="width: 100%; padding: 12px; margin: 8px 0;">
                    <option value="mp4">वीडियो (MP4 - उच्च गुणवत्ता)</option>
                    <option value="mp3">केवल ऑडियो (MP3)</option>
                    <option value="360">वीडियो (360p)</option>
                    <option value="720">वीडियो (720p)</option>
                </select>
                <button type="submit">डाउनलोड करें</button>
            </form>
            
            {% if youtube_result %}
            <div class="result">
                <div class="video-info">
                    <h3>{{ youtube_result.title }}</h3>
                    <img src="{{ youtube_result.thumbnail }}" class="thumbnail" alt="थंबनेल">
                    <p>अवधि: {{ youtube_result.duration }} सेकंड</p>
                    <a href="{{ youtube_result.download_url }}" class="download-btn">डाउनलोड करें</a>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div id="instagram" class="tabcontent">
            <h2>Instagram Reels डाउनलोडर</h2>
            <form action="/download/instagram" method="post">
                <input type="text" name="url" placeholder="Instagram Reels URL डालें..." required>
                <button type="submit">डाउनलोड करें</button>
            </form>
            
            {% if instagram_result %}
            <div class="result">
                <div class="video-info">
                    <h3>Instagram Reels</h3>
                    <video controls width="100%" style="max-height: 500px;">
                        <source src="{{ instagram_result.video_url }}" type="video/mp4">
                        आपका ब्राउज़र वीडियो सपोर्ट नहीं करता।
                    </video>
                    <a href="{{ instagram_result.download_url }}" class="download-btn">डाउनलोड करें</a>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div id="facebook" class="tabcontent">
            <h2>Facebook वीडियो डाउनलोडर</h2>
            <form action="/download/facebook" method="post">
                <input type="text" name="url" placeholder="Facebook वीडियो URL डालें..." required>
                <button type="submit">डाउनलोड करें</button>
            </form>
            
            {% if facebook_result %}
            <div class="result">
                <div class="video-info">
                    <h3>Facebook Video</h3>
                    <video controls width="100%" style="max-height: 500px;">
                        <source src="{{ facebook_result.video_url }}" type="video/mp4">
                        आपका ब्राउज़र वीडियो सपोर्ट नहीं करता।
                    </video>
                    <a href="{{ facebook_result.download_url }}" class="download-btn">डाउनलोड करें</a>
                </div>
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
    </script>
</body>
</html>
"""

# होमपेज
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# YouTube डाउनलोडर
@app.route('/download/youtube', methods=['POST'])
def youtube_download():
    url = request.form.get('url')
    format = request.form.get('format', 'mp4')
    
    try:
        yt = pytube.YouTube(url)
        
        if format == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
        elif format == '360':
            stream = yt.streams.filter(res="360p").first()
        elif format == '720':
            stream = yt.streams.filter(res="720p").first()
        else:
            stream = yt.streams.get_highest_resolution()
        
        return render_template_string(HTML_TEMPLATE,
            youtube_result={
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'duration': yt.length,
                'download_url': stream.url
            }
        )
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
            youtube_error=str(e)
        )

# Instagram डाउनलोडर
@app.route('/download/instagram', methods=['POST'])
def instagram_download():
    url = request.form.get('url')
    
    try:
        L = Instaloader()
        shortcode = re.search(r'/reel/([^/?]+)', url).group(1)
        post = Post.from_shortcode(L.context, shortcode)
        
        return render_template_string(HTML_TEMPLATE,
            instagram_result={
                'video_url': post.video_url,
                'download_url': post.video_url
            }
        )
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
            instagram_error=str(e)
        )

# Facebook डाउनलोडर
@app.route('/download/facebook', methods=['POST'])
def facebook_download():
    url = request.form.get('url')
    
    try:
        post = next(get_posts(post_urls=[url], cookies="cookies.txt"))
        
        return render_template_string(HTML_TEMPLATE,
            facebook_result={
                'video_url': post['video'],
                'download_url': post['video']
            }
        )
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
            facebook_error=str(e)
        )

if __name__ == '__main__':
    app.run(debug=True)
