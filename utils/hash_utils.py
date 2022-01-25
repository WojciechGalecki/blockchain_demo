import hashlib
import json


def hash_block(block):
    return hash_256(json.dumps(block.serialize_block()).encode())


def hash_256(bytes_arg):
    return hashlib.sha256(bytes_arg).hexdigest()