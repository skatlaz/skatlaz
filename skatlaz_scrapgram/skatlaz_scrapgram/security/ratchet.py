import hashlib
import os

class Ratchet:
    def __init__(self, root_key=None):
        self.root_key = root_key or os.urandom(32)

    def kdf(self, key):
        return hashlib.sha256(key).digest()

    def next_key(self):
        self.root_key = self.kdf(self.root_key)
        return self.root_key

    def encrypt_key(self):
        return self.root_key[:32]
