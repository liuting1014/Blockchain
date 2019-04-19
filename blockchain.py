import pickle
from time import time

import hash_util
from block import Block
from transaction import Transaction
from utils import Utils

MINING_REWARD = 10
blockchain = []
open_transactions = []
owner = "Ting"


def load_data():
	global blockchain
	global open_transactions
	try:
		with open("blockchain.txt", mode="rb") as file:
			file_content = pickle.loads(file.read())
			blockchain = file_content["chain"]
			open_transactions = file_content["open_transactions"]
	except IOError:
		genesis_block = Block(0, "", [], 1014, time())
		blockchain = [genesis_block]
		open_transactions = []


load_data()


def save_data():
	try:
		with open("blockchain.txt", mode="wb") as file:
			data = {
				"chain": blockchain,
				"open_transactions": open_transactions
			}
			file.write(pickle.dumps(data))
	except IOError:
		print('Saving to file failed!')


def get_last_blockchain_value():
	""" Returns the last value of the current blockchain. """
	if len(blockchain) < 1:
		return None
	return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
	transaction = Transaction(sender, recipient, amount)
	verifier = Utils()
	if verifier.verify_transaction(transaction, get_balance):
		open_transactions.append(transaction)
		save_data()
		return True
	return False


def mine_block():
	last_block = blockchain[-1]
	hashed_block = hash_util.hash_block(last_block)
	proof = generate_proof_of_work()
	reward_transaction = Transaction("MINING", owner, MINING_REWARD)
	# shallow copy
	copied_transactions = open_transactions[:]
	copied_transactions.append(reward_transaction)
	block = Block(len(blockchain), hashed_block, copied_transactions, proof, time())
	blockchain.append(block)
	return True


def get_transaction_value():
	tx_recipient = input("Enter the recipient of the transaction:")
	tx_amount = float(input("Your transaction amount please: "))
	return tx_recipient, tx_amount


def get_user_choice():
	user_input = input("Your choice: ")
	return user_input


def print_blockchain_elements():
	# Output the blockchain list to the console
	for block in blockchain:
		print("Outputting Block")
		print(block)


def generate_proof_of_work():
	last_block = blockchain[-1]
	last_hash = hash_util.hash_block(last_block)
	proof = 0
	verifier = Utils()
	while not verifier.validate_proof(open_transactions, last_hash, proof):
		proof += 1
	return proof


def get_balance(participant):
	tx_by_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]
	open_tx_by_sender = [tx.amount for tx in open_transactions if tx.sender == participant]
	tx_by_sender.append(open_tx_by_sender)
	amount_sent = sum([sum(tx) for tx in tx_by_sender])
	tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in blockchain]
	amount_received = sum([sum(tx) for tx in tx_recipient])
	return amount_received - amount_sent


while True:
	print("Please choose")
	print("1: Add a new transaction value")
	print("2: Mine a block")
	print("3: Print blocks")
	print("4: Check validity of all transactions")
	print("q: Quit")
	user_choice = get_user_choice()
	if user_choice == "1":
		tx_data = get_transaction_value()
		recipient, amount = tx_data
		if add_transaction(recipient, amount=amount):
			print("Added transaction")
		else:
			print("Transaction failed")
	elif user_choice == "2":
		mine_block()
		open_transactions = []
		save_data()
	elif user_choice == "3":
		print_blockchain_elements()
	elif user_choice == "4":
		verifier = Utils()
		verifier.verify_transactions(open_transactions, get_balance)
	elif user_choice == "q":
		break
	else:
		print("Input was invalid, please pick a value from the list!")
	verifier = Utils()
	if not verifier.verify_chain(blockchain):
		print("Invalid blockchain!")
		break
	print("Balance of {}: {:*^10.2f}".format(owner, get_balance(owner)))
print("Done!")
