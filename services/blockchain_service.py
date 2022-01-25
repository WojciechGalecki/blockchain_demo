import pickle
from functools import reduce
import requests

from models.block import Block
from models.transaction import Transaction
from utils import hash_utils
from services.validation_service import ValidationService
from services.wallet_service import WalletService

BLOCKCHAIN_FILENAME = 'local_data/blockchain_{}.p'


class BlockchainService:
    def __init__(self, blockchain, hosting_node, node_id):
        self.blockchain = blockchain
        self.open_transactions = []
        self.mining_reward = 10
        self.hosting_node = hosting_node
        self.nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.save_data()  # todo handle no file - bootstrap_blockchain - script to create genesis block in file
        self.load_data()

    def get_open_transactions(self):
        print('Getting open transactions...')
        return self.open_transactions[:]

    def save_data(self):
        #  todo error handling
        print('Saving blockchain and open transactions values to a file...')
        with open(BLOCKCHAIN_FILENAME.format(self.node_id), mode='wb') as file:  # .p - pickle, b - binary data
            file.write(pickle.dumps({
                'blockchain': self.blockchain.get_chain(),
                'open_transactions': self.open_transactions,
                'nodes': self.nodes
            }))
            print('Successfully saved blockchain and open transactions values to a file')

    def load_data(self):
        print('Loading blockchain data from a file...')
        with open(BLOCKCHAIN_FILENAME.format(self.node_id), mode='rb') as file:
            file_content = pickle.loads(file.read())
            self.blockchain.chain = file_content['blockchain']
            self.open_transactions = file_content['open_transactions']
            self.nodes = file_content['nodes']

    def get_wallet_balance(self, sender=None):
        print('Calculating founds balance...')
        if sender is None:
            if self.hosting_node is None:
                return None
            participant = self.hosting_node
        else:
            participant = sender

        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in
                     self.blockchain.get_chain()]
        open_tx_sender = [tx.amount for tx in self.open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                        self.blockchain.get_chain()]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum,
                                 tx_recipient, 0)

        return amount_received - amount_sent

    def proof_of_work(self):
        print('Proof of work...')
        last_block = self.blockchain.get_chain()[-1]
        last_hash = hash_utils.hash_block(last_block)
        proof = 0
        while not ValidationService.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def add_transaction(self, sender, recipient, amount, signature) -> bool:
        # if self.hosting_node is None:
        #     return False
        transaction = Transaction(sender, recipient, amount, signature)
        if ValidationService.verify_transaction(transaction, self.get_wallet_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            self.broadcast_transaction_to_all_nodes(transaction)
            return True
        return False

    def broadcast_transaction_to_all_nodes(self, transaction):
        for node in self.nodes:
            url = f'http://{node}/broadcast-transaction'
            try:
                response = requests.post(url, json=transaction.to_ordered_dict())
                if response.status_code != 200:
                    print('Transaction declined!')
                    return False
                print(f'Successfully broadcast new transaction to node: {node}')
                return True
            except requests.exceptions.ConnectionError:
                print(f'Failed to broadcast new transaction to node: {node}')
                continue

    def mine_block(self) -> Block or None:
        print('Mining new block...')
        if self.hosting_node is None:
            return None
        last_block = self.blockchain.get_chain()[-1]
        proof = self.proof_of_work()
        print(f'Proof: {proof}')
        reward_transaction = Transaction('MINING', self.hosting_node, self.mining_reward, '')
        copied_transactions = self.open_transactions[:]
        for tx in copied_transactions:
            if not WalletService.verify_transaction_signature(tx):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.blockchain.chain), hash_utils.hash_block(last_block), copied_transactions, proof)
        self.blockchain.chain.append(block)
        self.open_transactions = []
        self.save_data()
        self.broadcast_block_to_all_nodes(block)
        return block

    def broadcast_block_to_all_nodes(self, block):
        for node in self.nodes:
            url = f'http://{node}/broadcast-block'
            try:
                response = requests.post(url, json=block.serialize_block())
                if response.status_code != 200:
                    print('Block declined!')
                if response.status_code == 409:
                    print('Block conflict!')
                    self.resolve_conflicts = True
                print(f'Successfully broadcast new block to node: {node}')
            except requests.exceptions.ConnectionError:
                print(f'Failed to broadcast new block to node: {node}')
                continue

    # def add_block(self, block) -> bool:
    #     block['transactions'][:-1]  # exclude reward transaction
    #     is_proof_valid = Validator.valid_proof()  # todo
    #     hashes_match = hash.hash_block(self.__chain[-1]) == block['previous_hash']
    #     if not is_proof_valid or not hashes_match:
    #         return False
    #     self.__chain.append(block)
    #     open_transactions = self.__open_transactions[:]
    #     for incoming_tx in block['transactions']:
    #         for open_tx in open_transactions:
    #     # if open_tx == incoming_tx:
    #     # try to - self.__open_transactions.remove(open_tx)
    #     self.save_data()
    #     return True

    def resolve_conflicts(self) -> bool:
        longest_chain = self.blockchain.get_chain()
        for node in self.nodes:
            url = f'http:localhost{node}/blockchain'
            try:
                response = requests.get(url)
                incoming_node_chain = response.json()
                incoming_node_chain_length = len(incoming_node_chain)
                local_chain_length = len(longest_chain)
                if incoming_node_chain_length > local_chain_length and ValidationService.verify_chain(incoming_node_chain):
                    #  todo json vs object
                    longest_chain = incoming_node_chain
            except requests.exceptions.ConnectionError:
                continue

        is_chain_updated = len(longest_chain) > len(self.blockchain.get_chain())
        if is_chain_updated:
            self.open_transactions = []

        self.resolve_conflicts = False
        self.blockchain.chain = longest_chain
        self.save_data()
        return is_chain_updated

    def add_node(self, node):
        self.nodes.add(node)
        self.save_data()

    def remove_node(self, node):
        self.nodes.discard(node)
        self.save_data()

    def get_nodes(self):
        return list(self.nodes)
