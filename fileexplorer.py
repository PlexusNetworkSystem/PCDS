import json, configparser, time, os, datetime, psutil, requests, subprocess
from flask import Flask, send_file, render_template, jsonify, request, redirect
from lib.functions import allowed_file
from datetime import timedelta
from werkzeug.utils import secure_filename
# Config
config = configparser.ConfigParser()
config.read('config.ini')
endpoint = config.get('Settings', 'endpoint')


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(config.get('Settings', 'max_content_size'))
app.secret_key = f'{config.get("Settings", "secret_key")}'  # Make sure to set a secure secret key
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
app.permanent_session_lifetime = timedelta(hours=24)


@app.route('/')
def root():
    with open('status.log', 'r') as f:
        if f.read().strip() == 'suspend':
            return render_template("suspend.html"), 503
    return render_template("welcome.html")


if __name__ == '__main__':
    app.run(debug=True, port=int(config.get('Settings', 'fileexplorerport')))