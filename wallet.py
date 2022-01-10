from crypto import crypto

KEYS_FILENAME = 'wallet_keys.txt'


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        print('Creating public and private wallet keys...')
        self.private_key, self.public_key = crypto.generate_keys()
        #  save keys in this method
        #  new endpoint for getting keys?

    def save_keys(self):
        try:
            print('Saving wallet keys to a file...')
            with open(KEYS_FILENAME, mode='w') as file:
                file.write(self.private_key)
                file.write('\n')
                file.write(self.public_key)
                print('Successfully saved wallet keys to a file')
            return True
        except (IOError, IndexError):
            print('Saving wallet keys failed!')
            return False

    def load_keys(self):
        try:
            print('Loading wallet keys from a file...')
            with open(KEYS_FILENAME, mode='r') as file:
                keys = file.readlines()
                self.private_key = keys[0][:-1]  # exclude \n
                self.public_key = keys[1]
        except (IOError, IndexError):
            print('Loading wallet keys failed!')

    def sign_transaction(self, sender, recipient, amount):
        print(f'Signing new transaction from {sender} to {recipient}...')
        payload = f'{sender}{recipient}{amount}'
        return crypto.generate_signature(self.private_key, payload)

    @staticmethod
    def verify_transaction(transaction):
        payload = f'{transaction.sender}{transaction.recipient}{transaction.amount}'
        return crypto.verify_signature(transaction.sender, payload, transaction.signature)
