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


@app.route("/")
def root():
    return render_template('accessdenied.html'), 403

@app.route("/tkn/<access>", methods=['GET', 'POST'])
def index(access):
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
  
    if client_ip in config.get('LoginBanned', 'IPS'):
        return render_template('accessdenied.html', ip=client_ip), 403
                        
    with open('fm.access', 'r') as fmaccess:
        accessfile = fmaccess.read()
        if not access in accessfile:
            return render_template("accessdenied.html", ip=client_ip), 403
        os.system("echo '' > fm.access")
    return render_template("panel/fm.html", ip=client_ip, token=config.get("Settings", "secret_key")) 


if __name__ == '__main__':
    app.run(debug=True, port=int(config.get('Settings', 'fileexplorerport')))