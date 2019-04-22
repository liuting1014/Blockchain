from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet

app = Flask(__name__)
CORS(app)


@app.route('/wallet', methods=['POST'])
def create_keys():
	wallet.create_keys()
	if wallet.save_keys():
		global blockchain
		blockchain = Blockchain(wallet.public_key, port)
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
		blockchain = Blockchain(wallet.public_key, port)
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
def get_node_ui():
	return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
	return send_from_directory('ui', 'network.html')


@app.route('/transaction', methods=['POST'])
def add_transaction():
	if wallet.public_key is None:
		response = {
			'message': 'No wallet wet up'
		}
		return jsonify(response), 400
	data = request.get_json()
	if not data:
		response = {
			'message': 'No data found'
		}
		return jsonify(response), 400

	required_fields = ['recipient', 'amount']
	if not all(field in data for field in required_fields):
		response = {
			'message': 'Required data is missing'
		}
		return jsonify(response), 400

	recipient = data['recipient']
	amount = data['amount']
	signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
	success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
	if success:
		response = {
			'message': 'Successfully added transaction',
			'transaction': {
				'sender': wallet.public_key,
				'recipient': recipient,
				'amount': amount,
				'signature': signature
			},
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Failed to create a transaction'
		}
		return jsonify(response), 500


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


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
	transactions = blockchain.get_open_transactions()
	dict_transactions = [tx.__dict__ for tx in transactions ]
	return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
	chain_snapshot = blockchain.chain
	dict_chain = [block.__dict__.copy() for block in chain_snapshot]
	for dict_block in dict_chain:
		dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
	return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
	data = request.get_json()
	if not data:
		response = {
			'message': 'No data attached'
		}
		return jsonify(response), 400
	if 'node' not in data:
		response = {
			'message': 'No node data found'
		}
		return jsonify(response), 400
	node = data['node']
	blockchain.add_peer_node(node)
	response = {
		'message': 'Successfully added new node',
		'all_nodes': blockchain.get_peer_nodes()
	}
	return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
	if node_url == '' or node_url is None:
		response = {
			'message': 'No node found'
		}
		return jsonify(response), 400
	blockchain.remove_peer_node(node_url)
	response = {
		'message': 'Node removed',
		'all_nodes': blockchain.get_peer_nodes()
	}
	return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
	response = {
		'all_nodes': blockchain.get_peer_nodes()
	}
	return jsonify(response), 200


if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-p', '--port', type=int, default=5000)
	args = parser.parse_args()
	port = args.port
	wallet = Wallet(port)
	blockchain = Blockchain(wallet.public_key, port)
	app.run(host='0.0.0.0', port=port)
