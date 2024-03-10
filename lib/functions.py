import os

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
def check_login(token, secret_key):
    # Check if the user directory exists       
    user_directory = f"box/{token}"
    if not os.path.exists(user_directory):
        return 'invalidToken.html'

    # Check if the secret key matches the one stored in the file
    secret_key_file_path = f"{user_directory}/secret.key"
    with open(secret_key_file_path, 'r') as secret_key_file:
        stored_secret_key = secret_key_file.read()
        if not stored_secret_key == secret_key:
            return 'invalidKey.html'
        else:
            return 'GG'
        
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'webm', 'lock'}



