import hashlib
import json


def hash_block(block):
    print('Hashing new block...')
    return hash_256(json.dumps(block.to_serializable_block()).encode())


def hash_256(bytes_arg):
    return hashlib.sha256(bytes_arg).hexdigest()
