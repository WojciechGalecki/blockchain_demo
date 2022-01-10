from hashing import hash
from wallet import Wallet


class Validator:
    @classmethod
    def verify_chain(cls, blockchain):  # todo Block class ?
        print('Chain verification...')
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block['previous_hash'] != hash.hash_block(block[index - 1]):
                return False
            if not cls.valid_proof(block['transactions'], block['previous_hash'],
                                   block['proof']):  # exclude reward transaction
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance()
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all([cls.verify_transaction(get_balance, False) for tx in open_transactions])

    @staticmethod
    def valid_proof(transactions, last_hash, proof_number):
        guess = f'{[tx.__dict__.copy() for tx in transactions]}{last_hash}{proof_number}'.encode()
        guess_hash = hash.hash_256(guess)
        is_valid = guess_hash[0:2] == '00'
        if is_valid:
            print(f'Valid proof - hash: {guess_hash}')
            return True
        else:
            print(f'Invalid proof - hash: {guess_hash}')
            return False
