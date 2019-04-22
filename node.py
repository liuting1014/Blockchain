from flask import Flask, jsonify
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/wallet', methods=['POST'])
def create_keys():
	wallet.create_keys()
	if wallet.save_keys():
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		response = {
			'public_key': wallet.public_key,
			'private_key': wallet.private_key,
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Failed to save the keys'
		}
		return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
	if wallet.load_keys():
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		response = {
			'public_key': wallet.public_key,
			'private_key': wallet.private_key,
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Failed to load the keys'
		}
		return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
	balance = blockchain.get_balance()
	if balance is not None:
		response = {
			'message': 'Successfully fetched balance',
			'balance': balance
		}
		return jsonify(response), 200
	else:
		response = {
			'message': 'Failed to load balance',
			'wallet_set_up': wallet.public_key is not None
		}
		return jsonify(response), 500

@app.route('/', methods=['GET'])
def get_ui():
	return "This works!"


@app.route('/mine', methods=['POST'])
def mine():
	block = blockchain.mine_block()
	if block is not None:
		dict_block = block.__dict__.copy()
		dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
		response = {
			'message': 'Block added successfully',
			'block': dict_block,
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Failed to mine a block',
			'wallet_set_up': wallet.public_key is not None
		}
		return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
	chain_snapshot = blockchain.chain
	dict_chain = [block.__dict__.copy() for block in chain_snapshot]
	for dict_block in dict_chain:
		dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
	return jsonify(dict_chain), 200


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
