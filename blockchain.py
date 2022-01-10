import pickle
from functools import reduce

from models.block import Block
from models.transaction import Transaction
from hashing import hash
from validation.validator import Validator
from wallet import Wallet

BLOCKCHAIN_FILENAME = 'blockchain.p'


class Blockchain:
    def __init__(self, hosting_node):
        genesis_block = Block(0, '', [], 1, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.__mining_reward = 10
        self.hosting_node = hosting_node
        # self.save_data() todo handle no file - bootstrap_blockchain - script to create genesis block in file
        self.load_data()

    def get_chain(self):
        print('Getting blockchain...')
        return self.__chain[:]  # reference object

    def get_open_transactions(self):
        print('Getting open transactions...')
        return self.__open_transactions[:]

    def save_data(self):
        #  todo error handling
        print('Saving blockchain and open transactions values to a file...')
        with open(BLOCKCHAIN_FILENAME, mode='wb') as file:  # .p - pickle, b - binary data
            file.write(pickle.dumps({
                'blockchain': self.__chain,
                'open_transactions': self.__open_transactions
            }))
            print('Successfully saved blockchain and open transactions values to a file')

    def load_data(self):
        print('Loading blockchain data from a file...')
        with open(BLOCKCHAIN_FILENAME, mode='rb') as file:
            file_content = pickle.loads(file.read())
            self.__chain = file_content['blockchain']
            self.__open_transactions = file_content['open_transactions']

    def get_wallet_balance(self):
        print('Calculating founds balance...')
        if self.hosting_node is None:
            return None
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                        self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum,
                                 tx_recipient, 0)

        return amount_received - amount_sent

    def proof_of_work(self):
        print('Proof of work...')
        last_block = self.__chain[-1]
        last_hash = hash.hash_block(last_block)
        proof = 0
        while not Validator.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def add_transaction(self, sender, recipient, amount, signature):
        if self.hosting_node is None:
            return False
        transaction = Transaction(sender, recipient, amount, signature)
        if Validator.verify_transaction(transaction, self.get_wallet_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        print('Mining new block...')
        if self.hosting_node is None:
            return None
        last_block = self.__chain[-1]
        proof = self.proof_of_work()
        print(f'Proof: {proof}')
        reward_transaction = Transaction('MINING', self.hosting_node, self.__mining_reward, '')
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hash.hash_block(last_block), copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block
