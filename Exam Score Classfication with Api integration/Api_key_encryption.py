import hashlib

def sha256(Api_key):
    return hashlib.sha256(Api_key.encode()).hexdigest()

