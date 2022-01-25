from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii


class CryptoService:

    @classmethod
    def generate_keys(cls):
        private_key = RSA.generate(1024)
        public_key = private_key.publickey()
        return (cls.stringify_binary_key(private_key),
                cls.stringify_binary_key(public_key))

    @staticmethod
    def stringify_binary_key(key) -> str:
        return binascii.hexlify(key.exportKey(format='DER')).decode('ascii')

    @staticmethod
    def generate_signature(private_key, payload) -> str:  # payload = sender + recipient + amount
        print('Signature generation...')
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(private_key)))
        payload_hash = SHA256.new(payload.encode('utf8'))
        signature = signer.sign(payload_hash)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_signature(public_key, payload, signature):  # public, private ?
        print('Signature verification...')
        public_key = RSA.importKey(binascii.unhexlify(public_key))
        payload_hash = SHA256.new(payload.encode('utf8'))
        return PKCS1_v1_5.new(public_key).verify(payload_hash, binascii.unhexlify(signature))
