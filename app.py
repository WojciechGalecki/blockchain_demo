from flask import Flask, jsonify, request
from flask_cors import CORS
from argparse import ArgumentParser

from models.wallet import Wallet
from models.blockchain import Blockchain
from services.wallet_service import WalletService
from services.blockchain_service import BlockchainService

app = Flask(__name__)
CORS(app)


@app.route('/wallet', methods=['POST'])
def set_up_wallet():
    keys = wallet_service.create_keys()
    if wallet_service.save_keys():
        blockchain_service.hosting_node = wallet.public_key
        return jsonify(keys), 201
    else:
        return jsonify({'message': 'Saving the keys failed!'}), 500


@app.route('/wallet/balance', methods=['GET'])
def get_wallet_balance():
    balance = blockchain_service.get_wallet_balance()
    if balance is not None:
        return jsonify({'balance': balance}), 200
    else:
        return jsonify({
            'message': 'Balance calculation failed!',
            'walletSetUp': wallet.public_key is not None
        }), 500


@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    return jsonify([block.serialize_block() for block in blockchain.get_chain()]), 200


@app.route('/mine', methods=['POST'])
def mine_block():
    mined_block = blockchain_service.mine_block()
    if mined_block is not None:
        return jsonify({
            'message': 'Successfully added a new block',
            'block': mined_block.serialize_block(),
        }), 200
    else:
        return jsonify({
            'message': 'Adding a block failed!',
            'walletSetUp': wallet.public_key is not None
        }), 500


@app.route('/transactions', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        return jsonify({'message': 'No wallet set up'}), 400

    # body validation


    # #  todo balance validation error msg
    # if not body:
    #     response = {
    #         'message': 'Missing required body!'
    #     }
    #     return jsonify(response), 400
    #
    # sender = wallet.public_key
    # recipient = body['recipient']
    # amount = body['amount']
    # signature = wallet.sign_transaction(sender, recipient, amount)
    # success = blockchain.add_transaction(sender, recipient, amount, signature)
    #
    # if success:
    #     response = {
    #         'message': 'Successfully added transaction'
    #     }
    #     return jsonify(response), 201
    # else:
    #     response = {
    #         'message': 'Adding a transaction failed!'
    #     }
    #     return jsonify(response), 500


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    node_port = parser.parse_args().port

    wallet = Wallet(node_port)
    wallet_service = WalletService(wallet)
    blockchain = Blockchain()
    blockchain_service = BlockchainService(blockchain, wallet.public_key, node_port)

    app.run(host='localhost', port=node_port)
