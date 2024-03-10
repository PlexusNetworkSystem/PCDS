import json, configparser, time, os, datetime 
from flask import Flask, send_file, render_template, jsonify, request, redirect, session
from flask.sessions import SecureCookieSessionInterface
from lib.functions import log, totalLog, check_login, allowed_file
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

@app.route('/')
def root():
    return render_template("welcome.html")

@app.route('/docs')
@app.route('/docs/')
def routetodocs():
    return redirect('/docs/welcome')

@app.route('/docs/<path:docname>')
def usage_docs(docname):
    if "media" in docname:
         if not os.path.exists(f'static/docs/{docname}'):
            return render_template("notfound.html")
         else:
            return send_file(f'static/docs/{docname}')
    if not os.path.exists(f'static/docs/{docname}.md'):
        return render_template("notfound.html")
    file = open(f'static/docs/{docname}.md').read().strip()
    return render_template('docs.html', content=file)


#api
@app.route('/api/<token>', methods=['POST'])
def apisystem(token):
        start_time = time.time()  # Start time for response time calculation
        if request.headers.getlist("X-Forwarded-For"):
            client_ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            client_ip = request.remote_addr
        if 'json_data' not in request.files:
            return jsonify({'error': 'Missing json_data part'}), 400

        json_data = request.files.get('json_data')  # Use .get() to handle NoneType
        if json_data is None or json_data.filename == '':
            return jsonify({'error': 'No json_data file selected'}), 400

        data = json.load(json_data.stream)
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

@app.route('/<path:path>')
def content(path):
    if ".." in path:
        return jsonify({'message': 'Yay! You found The Flag'}), 500
    filename = 'box/public/' + path
    if os.path.exists(filename):
        return send_file(filename)
    else:
        return render_template("notfound.html")

if __name__ == '__main__':
    app.run(debug=True, port=int(config.get('Settings', 'port')))
