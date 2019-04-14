from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Crypto.Random import get_random_bytes
import base64


def Encrypt(data, key):
    data = data.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC)
    ctBytes = cipher.encrypt(pad(data, AES.block_size))
    iv = base64.b64encode(cipher.iv)
    ct = base64.b64encode(ctBytes)
    return ct.decode('utf-8'), iv.decode('utf-8')

def Decrypt(data, key, iv):
    data = base64.b64decode(data)
    iv = base64.b64decode(iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(data), AES.block_size)
    return plaintext

    