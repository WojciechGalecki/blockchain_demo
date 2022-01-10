from flask import Flask, jsonify, request
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

wallet = Wallet()
blockchain = Blockchain(wallet.public_key)


@app.route('/', methods=['GET'])
def home():
    return 'work'


@app.route('/wallet', methods=['POST'])
def set_up_wallet():
    wallet.create_keys()
    if wallet.save_keys():
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed!'
        }
        return jsonify(response), 500


# @app.route('/wallet', methods=['GET'])
# def load_keys():
# wallet.load_keys()


@app.route('/wallet/balance', methods=['GET'])
def get_wallet_balance():
    balance = blockchain.get_wallet_balance()
    if balance is not None:
        response = {
            'wallet balance': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Calculating wallet balance failed!',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {
            'message': 'No wallet set up'
        }
        return jsonify(response), 400

    body = request.get_json()
    #  todo body validation { recipient, amount }
    #  todo balance validation error msg
    if not body:
        response = {
            'message': 'Missing required body!'
        }
        return jsonify(response), 400

    sender = wallet.public_key
    recipient = body['recipient']
    amount = body['amount']
    signature = wallet.sign_transaction(sender, recipient, amount)
    success = blockchain.add_transaction(sender, recipient, amount, signature)

    if success:
        response = {
            'message': 'Successfully added transaction'
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a transaction failed!'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine_block():
    mined_block = blockchain.mine_block()
    if mined_block is not None:
        response = {
            'message': 'Successfully added a new block',
            'block': mined_block.to_serializable_block(),
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Adding a block failed!',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    return jsonify([block.to_serializable_block() for block in blockchain.get_chain()]), 200


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    return jsonify([tx.__dict__.copy() for tx in blockchain.get_open_transactions()]), 200


if __name__ == '__main__':
    app.run(host='localhost', port=5000)

    # 1. blockchain.p file MUST EXIST
    # 2. change log messages
    # 3. refactor - structure, names (blog app github)
