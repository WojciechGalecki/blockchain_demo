from services.crypto_service import CryptoService

KEYS_FILENAME = 'local_data/wallet_keys_{}.txt'


class WalletService:
    def __init__(self, wallet):
        self.wallet = wallet

    def create_keys(self):
        print('Creating public and private wallet keys...')
        self.wallet.private_key, self.wallet.public_key = CryptoService.generate_keys()
        return {
            'private_key': self.wallet.private_key,
            'public_key': self.wallet.public_key
        }

    def save_keys(self) -> bool:
        try:
            print('Saving wallet keys to a file...')
            with open(KEYS_FILENAME.format(self.wallet.node_id), mode='w') as file:
                file.write(self.wallet.private_key)
                file.write('\n')
                file.write(self.wallet.public_key)
                print('Successfully saved wallet keys to a file')
                return True
        except (IOError, IndexError):
            print('Saving wallet keys failed!')
            return False

    def load_keys(self):
        try:
            print('Loading wallet keys from a file...')
            with open(KEYS_FILENAME.format(self.wallet.node_id), mode='r') as file:
                keys = file.readlines()
                self.wallet.private_key = keys[0][:-1]  # exclude \n
                self.wallet.public_key = keys[1]
        except (IOError, IndexError):
            print('Loading wallet keys failed!')

    def sign_transaction(self, sender, recipient, amount):
        print(f'Signing new transaction from {sender} to {recipient}...')
        payload = f'{sender}{recipient}{amount}'
        return CryptoService.generate_signature(self.wallet.private_key, payload)

    @staticmethod
    def verify_transaction_signature(transaction):
        payload = f'{transaction.sender}{transaction.recipient}{transaction.amount}'

        return CryptoService.verify_signature(transaction.sender, payload, transaction.signature)
