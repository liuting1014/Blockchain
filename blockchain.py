import hashlib
import json
from collections import OrderedDict

MINING_REWARD = 10
genesis_block = {
	'previous-hash': '',
	'index': 0,
	'transactions': [],
	'proof': 1014
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Ting'
participants = {'Ting'}


def get_last_blockchain_value():
	""" Returns the last value of the current blockchain. """
	if len(blockchain) < 1:
		return None
	return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
	transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
	if verify_transaction(transaction):
		open_transactions.append(transaction)
		participants.add(sender)
		participants.add(recipient)
		return True
	return False


def verify_transaction(transaction):
	sender_balance = get_balance(transaction['sender'])
	return sender_balance >= transaction['amount'] > 0


def verify_transactions():
	return all([verify_transaction(tx) for tx in open_transactions])


def mine_block():
	last_block = blockchain[-1]
	hashed_block = hash_block(last_block)
	proof = generate_proof_of_work()
	reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
	# shallow copy
	copied_transactions = open_transactions[:]
	copied_transactions.append(reward_transaction)
	block = {
		'previous_hash': hashed_block,
		'index': len(blockchain),
		'transactions': copied_transactions,
		'proof': proof
	}
	blockchain.append(block)
	return True


def get_transaction_value():
	tx_recipient = input('Enter the recipient of the transaction:')
	tx_amount = float(input('Your transaction amount please: '))
	return tx_recipient, tx_amount


def get_user_choice():
	user_input = input('Your choice: ')
	return user_input


def print_blockchain_elements():
	# Output the blockchain list to the console
	for block in blockchain:
		print('Outputting Block')
		print(block)


def hash_block(block):
	return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


def validate_proof(transactions, last_hash, proof):
	guess = (str(transactions) + str(last_hash) + str(proof)).encode()
	guess_hash = hashlib.sha256(guess).hexdigest()
	print(guess_hash)
	return guess_hash[0:2] == '00'


def generate_proof_of_work():
	last_block = blockchain[-1]
	last_hash = hash_block(last_block)
	proof = 0
	while not validate_proof(open_transactions, last_hash, proof):
		proof += 1
	return proof


def verify_chain():
	for (index, block) in enumerate(blockchain):
		if index == 0:
			continue
		if block['previous_hash'] != hash_block(blockchain[index - 1]):
			return False
		if not validate_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
			print('Proof of work is invalid')
			return False
	return True


def get_balance(participant):
	tx_by_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
	open_tx_by_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
	tx_by_sender.append(open_tx_by_sender)
	# amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt[0] if len(tx_amt) > 0 else 0, tx_by_sender, 0)
	amount_sent = sum([sum(tx) for tx in tx_by_sender])
	tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
	amount_received = sum([sum(tx) for tx in tx_recipient])
	# amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + tx_amt[0] if len(tx_amt) > 0 else 0, tx_recipient, 0)
	return amount_received - amount_sent


while True:
	print('Please choose')
	print('1: Add a new transaction value')
	print('2: Mine a block')
	print('3: Print blocks')
	print('4: Check transactions validity')
	print('h: Manipulate the chain')
	print('q: Quit')
	user_choice = get_user_choice()
	if user_choice == '1':
		tx_data = get_transaction_value()
		recipient, amount = tx_data
		if add_transaction(recipient, amount=amount):
			print('Added transaction')
		else:
			print('Transaction failed')
	elif user_choice == '2':
		mine_block()
		open_transactions = []
	elif user_choice == '3':
		print_blockchain_elements()
	elif user_choice == '4':
		verify_transactions()
	elif user_choice == 'h':
		if len(blockchain) >= 1:
			blockchain[0] = {
				'previous_hash': '',
				'index': 0,
				'transactions': [
					{'sender': 'Whoever', 'recipent': 'me', 'amount': 'whatever'}
				]
			}
	elif user_choice == 'q':
		break
	else:
		print('Input was invalid, please pick a value from the list!')
	if not verify_chain():
		print('Invalid blockchain!')
		break
	print('Balance of {}: {:*^10.2f}'.format(owner, get_balance(owner)))
print('Done!')

