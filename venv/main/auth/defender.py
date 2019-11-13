import bcrypt

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

from uuid import getnode as get_mac

class Defender():

    def __init__(self, key = None):
        if key is not None:
            self.bs = 32
            self.key = hashlib.sha256(Defender.str_to_bytes(key)).digest()
        else:
            secret = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOiJ0ZXN0In0.9l5enKJWg8RetbakZGiKe7P8Bci4Bthp6ODLOv-eikw"
            self.bs = 32
            self.key = hashlib.sha256(Defender.str_to_bytes(secret)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * Defender.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self._pad(Defender.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def genSalt(self):
        return bcrypt.gensalt()

    def genHash(self, str , salt):
        hash = bcrypt.hashpw(str,salt)
        return hash

    def genHashAndSalt(self , str):
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(str,salt)

        return hash.decode('utf-8') , salt.decode('utf-8')

    def get_mac(self):
        mac = get_mac()
        return mac
