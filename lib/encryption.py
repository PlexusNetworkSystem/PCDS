import hmac, hashlib, os, struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

def encrypt_data(data, password):
    salt = get_random_bytes(16)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=1000000)  # Fixed bug: Password should be encoded before passing to PBKDF2
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    encrypted_data = struct.pack('<Q', len(data))
    encrypted_data += salt
    encrypted_data += iv
    
    chunk_size = 1024
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) % 16 != 0:
            chunk = pad(chunk, 16)
        encrypted_data += cipher.encrypt(chunk)

    return encrypted_data

def decrypt_data(encrypted_data, password):
    filesize = struct.unpack('<Q', encrypted_data[:8])[0]
    salt = encrypted_data[8:24]
    iv = encrypted_data[24:40]
    key = PBKDF2(password.encode(), salt, dkLen=32, count=1000000)  # Fixed bug: Password should be encoded before passing to PBKDF2
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    decrypted_data = b''
    chunk_size = 1024
    for i in range(40, len(encrypted_data), chunk_size):
        chunk = encrypted_data[i:i+chunk_size]
        decrypted_data += unpad(cipher.decrypt(chunk), 16)

    return decrypted_data[:filesize]

def encrypt_file(input_filename, password):
    output_filename = input_filename 
    salt = get_random_bytes(16)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=1000000)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(input_filename, 'rb') as f_in:
        encrypted_data = b''
        while True:
            chunk = f_in.read(1024)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk = pad(chunk, 16)
            encrypted_data += cipher.encrypt(chunk)

    # Save salt, iv, and encrypted data to the output file
    with open(output_filename, 'wb') as f_out:
        f_out.write(salt)
        f_out.write(iv)
        f_out.write(encrypted_data)


def decrypt_file(input_filename, password):
    output_filename = input_filename
    with open(input_filename, 'rb') as f_in:
        salt = f_in.read(16)
        iv = f_in.read(16)
        key = PBKDF2(password.encode(), salt, dkLen=32, count=1000000)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = b''
        while True:
            chunk = f_in.read(16)
            if len(chunk) == 0:
                break
            decrypted_data += cipher.decrypt(chunk)

        # Remove padding before writing to the output file
        decrypted_data = unpad(decrypted_data, AES.block_size)

        # Save the decrypted data to the output file
        with open(output_filename, 'wb') as f_out:
            f_out.write(decrypted_data)

def secure_compare(a, b):
    return hmac.compare_digest(a, b)


def generate_sha512_hash(file_path):
    sha512_hash = hashlib.sha512()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha512_hash.update(chunk)
    return sha512_hash.hexdigest()

def generate_sha256_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


# Example usage data
#password = "123456"
#plaintext_data = b"123456"
#encrypted_data = encrypt_data(plaintext_data, password)
#decrypted_data = decrypt_data(encrypted_data, password)
#encrypted_file_data = encrypt_file(filename, password)
#decrypted_file_data = decrypt_file(filename, password)
#
#print(decrypted_file_data)
#print(decrypted_data)
#
#is_match = secure_compare(decrypted_data, decrypted_file_data) 
#print("Match:", is_match) #True/False