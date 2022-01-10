from time import time


class Block:
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time() if timestamp is None else timestamp

    def to_serializable_block(self):
        serializable_block = self.__dict__.copy()
        serializable_block['transactions'] = [tx.__dict__.copy() for tx in serializable_block['transactions']]
        return serializable_block
