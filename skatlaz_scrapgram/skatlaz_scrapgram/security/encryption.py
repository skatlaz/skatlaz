from cryptography.fernet import Fernet

def gen():
    return Fernet.generate_key()

def encrypt(msg, key):
    return Fernet(key).encrypt(msg.encode())

def decrypt(msg, key):
    return Fernet(key).decrypt(msg).decode()
