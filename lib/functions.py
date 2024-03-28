import os, subprocess, re, requests

def log(token, content):
    with open(f'box/{token}/delivery.log', 'a') as file:
        file.write(content + '\n')  # Add a new line after writing content
def totalLog(token):
    with open(f'box/{token}/total.log', 'r+') as file:  # Open file in read/write mode
        value = int(file.read() or 0)  # Read value or default to 0 if file is empty
        value += 1
        file.seek(0)  # Move cursor to the beginning of the file
        file.write(str(value))  # Write the updated value
        file.truncate()  # Truncate the file to remove any extra content
        file.close()
        
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'webm', 'lock'}

def get_distro_info():
    distro_info = {}
    with open('/etc/os-release', 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                # Remove quotes from value if present
                value = value.strip('"')
                distro_info[key.lower()] = value
    return distro_info


def get_cpu_model_linux():
    try:
        # Execute lscpu and get the output
        output = subprocess.check_output("lscpu", shell=True).decode('utf-8')
        # Find the line that contains the CPU model
        for line in output.split('\n'):
            if "Model name" in line:
                cpu_model = line.split(':')[1].strip()
                # Define a pattern to match the substrings to remove
                pattern = r"Intel\(R\)|Core\(TM\)|Intel Xeon|CPU"
                # Use re.sub to replace the matched substrings with an empty string
                cleaned_cpu_model = re.sub(pattern, "", cpu_model)
                return cleaned_cpu_model
    except Exception as e:
        print(f"Error: {e}")
        return "Unknown"

def get_ip():
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    public_ip = requests.get('https://api64.ipify.org').text
    return f"{local_ip} | {public_ip}"


def get_gpu_model_linux():
    try:
        output = subprocess.check_output("lspci | grep -i vga", shell=True).decode('utf-8')
        for line in output.split('\n'):
            if "VGA compatible controller" in line:
                gpu_model = line.split(':')[-1].strip()
                gpu_model = ' '.join(gpu_model.split()[0:1] + gpu_model.split()[4:7])
                return gpu_model
    except Exception as e:
        print(f"Error: {e}")
        return "Unknown"
<<<<<<< HEAD

=======
    
>>>>>>> 2d98eeb432e4bb64cc2a9a1cffc697ad771247a3
