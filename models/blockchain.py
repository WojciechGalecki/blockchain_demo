from models.block import Block


class Blockchain:
    def __init__(self):
        genesis_block = Block(0, '', [], 1, 0)
        self.chain = [genesis_block]

    def get_chain(self):
        return self.chain[:]
