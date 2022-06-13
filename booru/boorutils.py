import hashlib

def hash_str(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()