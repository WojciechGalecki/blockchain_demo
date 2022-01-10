from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii


def generate_keys():
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()
    return (stringify_binary_key(private_key),
            stringify_binary_key(public_key))


def stringify_binary_key(key):
    return binascii.hexlify(key.exportKey(format='DER')).decode('ascii')


def generate_signature(private_key, payload):  # payload = sender + recipient + amount
    print('Signature generation...')
    signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(private_key)))
    payload_hash = SHA256.new(payload.encode('utf8'))
    signature = signer.sign(payload_hash)
    return binascii.hexlify(signature).decode('ascii')


def verify_signature(public_key, payload, signature):  # public, private ?
    print('Signature verification...')
    public_key = RSA.importKey(binascii.unhexlify(public_key))
    verifier = PKCS1_v1_5.new(public_key)
    payload_hash = SHA256.new(payload.encode('utf8'))
    return verifier.verify(payload_hash, binascii.unhexlify(signature))
