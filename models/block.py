from time import time


class Block:
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time() if timestamp is None else timestamp

    def serialize_block(self):
        block = self.__dict__.copy()
        block['transactions'] = [tx.__dict__.copy() for tx in block['transactions']]
        return block
