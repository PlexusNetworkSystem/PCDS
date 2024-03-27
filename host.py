import json, configparser, time, os, datetime, psutil, requests, subprocess
from flask import Flask, send_file, render_template, jsonify, request, redirect
from lib.functions import log, totalLog, allowed_file, get_distro_info, get_cpu_model_linux, get_ip, get_gpu_model_linux
from datetime import timedelta
from werkzeug.utils import secure_filename
from lib.encryption import encrypt_file, decrypt_file, encrypt_data, decrypt_data, secure_compare, generate_sha512_hash, generate_sha256_hash

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

#--------------------------------------------------------------------------------------------------------------------------------------------------

# Updates checking and auto update side

#--------------------------------------------------------------------------------------------------------------------------------------------------


@app.route('/')
def root():
    with open('status.log', 'r') as f:
        if f.read().strip() == 'suspend':
            return render_template("suspend.html"), 503
    return render_template("welcome.html")

@app.route('/docs')
@app.route('/docs/')
def routetodocs():
    with open('status.log', 'r') as f:
        if f.read().strip() == 'suspend':
            return render_template("suspend.html"), 503
    return redirect('/docs/welcome')

@app.route('/docs/<path:docname>')
def usage_docs(docname):
    with open('status.log', 'r') as f:
        if f.read().strip() == 'suspend':
            return render_template("suspend.html"), 503
    if "media" in docname:
         if not os.path.exists(f'static/docs/{docname}'):
            return render_template("notfound.html")
         else:
            return send_file(f'static/docs/{docname}')
    if not os.path.exists(f'static/docs/{docname}.md'):
        return render_template("notfound.html")
    file = open(f'static/docs/{docname}.md').read().strip()
    return render_template('docs.html', content=file)

@app.route('/anim/<chs>')
def anim(chs):
    with open('status.log', 'r') as f:
        if f.read().strip() == 'suspend':
            return jsonify({'message': '[500] Bad Request | System Suspended'}), 503
    return render_template(f"animation/{chs}.html")

#api
@app.route('/api/<token>', methods=['POST'])
def apisystem(token):
        with open('status.log', 'r') as f:
            if f.read().strip() == 'suspend':
                return jsonify({'message': '[500] Bad Request | System Suspended'}), 503
        start_time = time.time()  # Start time for response time calculation
        if request.headers.getlist("X-Forwarded-For"):
            client_ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            client_ip = request.remote_addr

        if not request.is_json and 'jsonData' not in request.form:
            return jsonify({'error': 'Missing JSON in request'}), 400
        
        json_data_str = request.form.get('jsonData')
        if json_data_str:
            data = json.loads(json_data_str)
        else:
            data = request.get_json()

        recive_secret_key = data.get('secret_key')
        force = data.get('force')  # Use this for uploading file
        subDir = data.get('subDir')
        if not subDir or subDir == '' or subDir == '/':
            subDir = ""
        else:
            if ".." in subDir:
                return jsonify({'message': 'Yay! You found The Flag'}), 500
            if subDir.startswith('/'):
             subDir = subDir[1:]
            if not subDir.endswith('/'):
             subDir += "/"
            if not os.path.exists(f'box/{token}/root/{subDir}'):
                return jsonify({'message': '[404] Directory not found'}), 404
             
        if not os.path.exists(f"box/{token}"):
            return jsonify({'message': 'Invalid API Token!'}), 401
        with open(f"box/{token}/secret.key", "rb") as f:
            secret_key = f.read()

        if secure_compare(decrypt_data(secret_key, recive_secret_key), recive_secret_key.encode()):
            procClass = data.get('procClass')
            # -------------------------------------------------------------Download-----------------------------------------------------
            if procClass == "download":
                totalLog(token)
                file = data.get('file')

                if "/" in file:
                    return jsonify({'message': '[500] You can not set path in filename', 'suggest': 'use "subDir: <path>"'}), 500

                if not file or file == 'null' or file.endswith('.lock'):
                    log(token, f"POST | SUCCESS | {datetime.datetime.now().replace(microsecond=0)} | PingPong | PCDS API Ping Request Success! | 200 | IP {client_ip}")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'message': 'PCDS API Ping Request Success!', 'Api token': f'{token}', 'Secret key': f'{recive_secret_key}', 'response_time': response_time, 'IP': client_ip}), 200

                elif file and os.path.exists(f'box/{token}/root/{subDir}' + file):
                    if os.path.exists(f'box/{token}/root/{subDir}{file}.lock'):
                        return jsonify({'message': '[409] File already in process', 'status': 'Delivery Lock / Decrypted', 'response_time': time.time() - start_time}), 409
                    log(token, f"POST | SUCCESS | {datetime.datetime.now().replace(microsecond=0)} | FILE | {file} | 200 | IP {client_ip}")
                    response_time = time.time() - start_time  # Calculate response time
                    os.system(f'touch box/{token}/root/{subDir}{file}.lock')
                    decrypt_file(f'box/{token}/root/{subDir}' + file, recive_secret_key)
                    return send_file(f'box/{token}/root/{subDir}' + file), 200, {'response_time': response_time, 'IP': client_ip} 
                
                elif file and not os.path.exists(f'box/{token}/root/{subDir}' + file):
                    log(token, f"POST | FAIL | {datetime.datetime.now().replace(microsecond=0)} | FILE | {file} | 404 | IP {client_ip}")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'message': '[404] File Not Found'}), 404
            # -------------------------------------------------------------Download-----------------------------------------------------

            # --------------------------------------------------------------Upload------------------------------------------------------
            elif procClass == "upload":
                totalLog(token)
                if 'file' not in request.files:
                    return jsonify({'error': 'No file part'}), 400

                file = request.files.get('file')  # Use .get() to handle NoneType

                if file is None or "/" in file.filename:
                    return jsonify({'message': '[500] You can not set path in filename', 'suggest': 'use "subDir: <path>"'}), 500

                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400

                if not allowed_file(file.filename):
                    return jsonify({'error': 'File type not allowed'}), 400

                filename = secure_filename(file.filename)

                if os.path.exists(f'box/{token}/root/{subDir}{filename}') and force == False:
                    log(token, f"POST | FAIL | {datetime.datetime.now().replace(microsecond=0)} | UPLOAD | {filename} | 503")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'message': f'File upload failed, ({filename}) is exist', 'file name': f'{filename}', 'suggestion': 'use (force: True) for changing file.', 'response_time': response_time, 'IP': client_ip}), 503
                else:
                    file.save(os.path.join(f'box/{token}/root/{subDir}', filename))
                    encrypt_file(f'box/{token}/root/{subDir}{filename}', recive_secret_key)

                if not os.path.exists(f'box/{token}/root/{subDir}{filename}'):
                    log(token, f"POST | FAIL | {datetime.datetime.now().replace(microsecond=0)} | UPLOAD | {filename} | 400")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'message': 'File upload failed', 'file name': f'{filename}', 'response_time': response_time, 'IP': client_ip}), 400
                else:
                    log(token, f"POST | SUCCESS | {datetime.datetime.now().replace(microsecond=0)} | UPLOAD | {filename} | 200 | IP {client_ip}")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'message': 'File successfully uploaded', 'file name': f'{filename}', 'response_time': response_time, 'IP': client_ip}), 200
            # --------------------------------------------------------------Upload------------------------------------------------------

            # --------------------------------------------------------------Delete------------------------------------------------------
            elif procClass == "delete":
                totalLog(token)
                filename = data.get('file')

                if "/" in filename:
                    return jsonify({'message': '[500] You can not set path in filename', 'suggest': 'use "subDir: <path>"'}), 500

                if not filename:
                    return jsonify({'error': 'No file part'}), 400

                if filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                
                if os.path.exists(f'box/{token}/{filename}') and not filename.endswith('.lock'):
                    os.remove(os.path.join(f'box/{token}/', filename))
                    if os.path.exists(f'box/{token}/{filename}'):
                        log(token, f"POST | FAIL | {datetime.datetime.now().replace(microsecond=0)} | DELETE | {filename} | 500 | IP {client_ip}")
                        response_time = time.time() - start_time  # Calculate response time
                        return jsonify({'message': '[500] File delete failed, server error', 'file name': f'{filename}', 'response_time': response_time, 'IP': client_ip}), 500
                    else:
                        log(token, f"POST | SUCCESS | {datetime.datetime.now().replace(microsecond=0)} | DELETE | {filename} | 200 | IP {client_ip}")
                        response_time = time.time() - start_time  # Calculate response time
                        return jsonify({'message': '[200] File delete success.', 'file name': f'{filename}', 'response_time': response_time, 'IP': client_ip}), 200
                else:
                    log(token, f"POST | FAIL | {datetime.datetime.now().replace(microsecond=0)} | DELETE | {filename} | 404 | IP {client_ip}")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'message': '[404] File delete failed, not found', 'file name': f'{filename}', 'response_time': response_time, 'IP': client_ip}), 404
            # --------------------------------------------------------------Delete------------------------------------------------------

            # ---------------------------------------------------------------List-------------------------------------------------------
            elif procClass == "list":
                totalLog(token)
                
                try:
                    items = []
                    for item in os.listdir(f'box/{token}/root/{subDir}'):
                        print(f"{subDir}{item}")
                        if os.path.exists(f'box/{token}/root/{subDir}{item}.lock'):
                            items.append(item + ' (lock)')
                        else:
                            if not item.endswith('.lock'):
                                items.append(item)
                    if items:
                        response_time = time.time() - start_time  # Calculate response time
                        return jsonify({'message': 'List of files and directories', 'items': items, 'response_time': response_time, 'IP': client_ip}), 200
                    else:
                        response_time = time.time() - start_time  # Calculate response time
                        return jsonify({'message': 'No files or directories found', 'response_time': response_time, 'IP': client_ip}), 404
                except Exception as e:
                    log(token, f"POST | FAIL | {datetime.datetime.now().replace(microsecond=0)} | LIST | Error | 500 | IP {client_ip}")
                    response_time = time.time() - start_time  # Calculate response time
                    return jsonify({'error': f'Failed to list files and directories: {str(e)}', 'response_time': response_time, 'IP': client_ip}), 500
            # ---------------------------------------------------------------List-------------------------------------------------------

            # --------------------------------------------------------------Unlock------------------------------------------------------
            elif procClass == "unlock":
                file = data.get('file')

                if "/" in file:
                    return jsonify({'message': '[500] You can not set path in filename', 'suggest': 'use "subDir: <path>"'}), 500
                
                if not file or file == 'null' or not os.path.exists(f'box/{token}/root/{subDir}{file}') or file.endswith(".lock"):
                    return jsonify({'message': '[404] File not found'}), 404
                
                if not os.path.exists(f'box/{token}/root/{subDir}{file}.lock'):
                    return jsonify({'message': '[409] File not in process'}), 409

                encrypt_file(f'box/{token}/root/{subDir}{file}', recive_secret_key)
                os.system(f'rm box/{token}/root/{subDir}{file}.lock')
                return jsonify({'message': '[200] File unlocked, processable again.'}), 200
            # --------------------------------------------------------------Unlock------------------------------------------------------
            
            elif procClass == "hash":
                totalLog(token)
                file = data.get('file')
                print(file)
                if "/" in file:
                    return jsonify({'message': '[500] You can not set path in filename','suggest': 'use "subDir: <path>"'}), 500
                if not file or file == 'null' or not os.path.exists(f'box/{token}/root/{subDir}{file}') or file.endswith(".lock"):
                    return jsonify({'message': '[404] File not found'}), 404
                if os.path.exists(f'box/{token}/root/{subDir}{file}.lock'):
                    return jsonify({'message': '[409] File already in process', 'status': 'Delivery Lock / Decrypted', 'response_time': time.time() - start_time}), 409
                decrypt_file(f'box/{token}/root/{subDir}' + file, recive_secret_key)
                sha512_hash = generate_sha512_hash(f'box/{token}/root/{subDir}{file}')
                sha256_hash = generate_sha256_hash(f'box/{token}/root/{subDir}{file}')
                encrypt_file(f'box/{token}/root/{subDir}' + file, recive_secret_key)
                response_time = time.time() - start_time  # Calculate response time
                return jsonify({'message': 'File hash values', 'file': file, 'SHA512': sha512_hash, 'SHA256': sha256_hash, 'response_time': response_time, 'IP': client_ip}), 200
            
            else:
                response_time = time.time() - start_time  # Calculate response time
                return jsonify({'message': f'Invalid process class {procClass}', 'debug': 'You Can only use upload/download/list/delete/unlock', 'response_time': response_time, 'IP': client_ip}), 400
            
        else:
            response_time = time.time() - start_time  # Calculate response time
            return jsonify({'message': 'Access denied! Invalid key.', 'response_time': response_time, 'IP': client_ip}), 401
#api end

#Panel

@app.route('/selfdestruct/<tokenv>', methods=['GET', 'POST'])
def selfdestruct(tokenv):
    if not tokenv == config.get('Login', 'token'):
        return jsonify({'error': '[401] Unauthorized', 'message': 'Invalid Token'}), 401
    else:
        return render_template("sd.html", token=tokenv), 200

@app.route('/panel', methods=['GET', 'POST'])
def panel():
    #IP check side
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
  
    if client_ip in config.get('LoginBanned', 'IPS'):
        return render_template('accessdenied.html', ip=client_ip), 403
    
    if request.method == 'GET':
        return render_template("login.html", ip=client_ip, loginfail=False, message="none", token="none"), 200
    else:
        #Is process values exists?
        data = request.form
        if data.get('client') == "panel":
            if not data.get('token') == config.get('Login', 'token'):
                return render_template("login.html", ip=client_ip, loginfail=True, message="Invalid Access Token", token=data.get('token')), 401
            else:
                #panel side | do process directly.
                process = data.get('process')
                if process == 'logout':
                    return render_template("login.html", ip=client_ip, logout=True, message="Logout Sucessfully", token="none"), 401
        else:
            #login side
            username = data.get('username')
            password = data.get('password')
            if username == '' or password == '':
                return render_template("login.html", ip=client_ip, loginfail=True, message="Username and Password can't be an empty", token="none"), 401
            if username == config.get('Login', 'username') and password == config.get('Login', 'password'):
                return render_template('panel/panel.html', ip=client_ip, message="none", token=config.get('Login', 'token'))
            else:
                return render_template("login.html", ip=client_ip, loginfail=True, message="Username or Password incorrect", token="none"), 401
            
@app.route('/panelcmd', methods=['GET', 'POST'])
def panelcmd():
    #IP check side
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
  
    if client_ip in config.get('LoginBanned', 'IPS'):
        return render_template('accessdenied.html', ip=client_ip), 403
    
    if request.method == 'GET':
        return render_template('accessdenied.html', ip=client_ip), 403
    else:
        data = request.get_json()
        if not data or not data.get('token'):
            return jsonify({'error': '[400] Bad Request', 'message': 'No Json part recived'}), 400
        else:
            if not data.get('token') == config.get('Login', 'token'):
                return jsonify({'error': '[401] Unauthorized', 'message': 'Invalid Token'}), 401
            else:
                process = data.get('process')
                if process == 'suspend':
                    with open('status.log', 'w') as file:
                        file.write('suspend')
                        file.close()
                    return jsonify({'message': '[200] System Suspended'}), 200
                elif process == 'wakeup':
                    with open('status.log', 'w') as file:
                        file.write('')
                        file.close()
                    return jsonify({'message': '[200] System Waked Up'}), 200               
                elif process == 'dynamic':
                    ram_info = psutil.virtual_memory()
                    used_ram_percent = round(ram_info.used / ram_info.total, 2) * 100
                    cpu_usage = psutil.cpu_percent(interval=1)
                    with open('status.log', 'r') as file:
                        status = file.read()
                        if "suspend" in status:
                            status = 'suspended'
                        else:
                            status = 'running'
                    return jsonify({"cpu_usage": cpu_usage, "ram_usage": used_ram_percent, "status": status}), 200
                elif process == 'disk':
                    for partition in psutil.disk_partitions():
                        if partition.fstype:
                            usage = psutil.disk_usage(partition.mountpoint)
                            #print(f"Disk: {partition.device}")
                            #print(f"Toplam Alan: {usage.total / (1024 ** 3):.2f} GB")
                            #print(f"Kullanılan Alan: {usage.percent:.2f}%")
                            #print(f"Boş Alan: {usage.free / (1024 ** 3):.2f} GB")
                            #print(f"Kullanım Yüzdesi: {usage.percent:.2f}%\n")
                    return {"used": f"{usage.percent:.2f}", "total": f"{usage.total / (1024 ** 3):.2f} GB"}
                elif process == 'ram':
                    ram_info = psutil.virtual_memory()
                    total_ram_mb = ram_info.total / (1024.0 ** 2)
                    used_ram_mb = ram_info.used / (1024.0 ** 2)
                    return round(jsonify({"total": total_ram_mb, "used": used_ram_mb})), 200
                elif process == 'cpu':
                    cpu_count = psutil.cpu_count(logical=False)
                    cpu_freq = psutil.cpu_freq().current
                    cpu_usage = psutil.cpu_percent(interval=1)
                    return jsonify({"cpu_count": cpu_count, "cpu_freq": cpu_freq, "cpu_usage": cpu_usage}), 200
                elif process == "generic":
                    information_data = {key: value for key, value in config.items('Information')}
                    if os.geteuid() == 0:
                        information_data['user'] = 'Root'
                    else:
                        information_data['user'] = os.getlogin()
                    
                    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
                    usage = ""
                    information_data['ram'] = ram_gb
                    information_data['cpu'] = get_cpu_model_linux()
                    information_data['gpu'] = get_gpu_model_linux()
                    information_data['servername'] = os.getenv('HOSTNAME')
                    information_data['port'] = config.get('Settings', 'port') 
                    information_data['ip'] = get_ip()
                    distro_info = get_distro_info()
                    information_data['os'] =  distro_info.get('name', 'Unknown')
                    for partition in psutil.disk_partitions():
                        if partition.fstype:
                            usage = psutil.disk_usage(partition.mountpoint)
                    information_data['disk'] = f"{usage.total / (1024 ** 3):.2f}"
                    location = requests.get('https://ipinfo.io').json()
                    information_data['location'] = f"{location['country']} {location['region']} {location['postal']}"
                    return jsonify(information_data), 200
                elif process == 'selfdestruct':
                    os.system('rm -rf *')
                    return jsonify({'message': '[200] System destruct'}), 200
                elif process == 'startconsole':
                    os.system("touch console.access")
                    os.system('bash lib/random.sh > console.access')
                    with open('console.access', 'r') as consolefile:
                        access = consolefile.read()
                        consolefile.close()
                    return jsonify({'message': '[200] Console active', 'access': access}), 200 
                else:
                    return jsonify({'error': '[400] Bad Request', 'message': 'No process specified'}), 401




#Panel end

@app.route('/<path:path>')
def content(path):
    with open('status.log', 'r') as f:
        if f.read().strip() == 'suspend':
            return jsonify({'message': '[503] Bad Request | System Suspended'}), 503
    if ".." in path:
        return jsonify({'message': 'Yay! You found The Flag'}), 500
    filename = 'box/public/' + path
    if os.path.exists(filename):
        return send_file(filename)
    else:
        return render_template("notfound.html")

if __name__ == '__main__':
    app.run(debug=True, port=int(config.get('Settings', 'port')))
