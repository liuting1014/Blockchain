import pickle
from time import time

import hash_util
from block import Block
from transaction import Transaction
from utils import Utils

MINING_REWARD = 10


class Blockchain:
	def __init__(self, hosting_node_id):
		genesis_block = Block(0, "", [], 1014, time())
		self.__chain = [genesis_block]
		self.__open_transactions = []
		self.load_data()
		self.hosting_node = hosting_node_id

	def get_chain(self):
		return self.__chain

	def get_open_transactions(self):
		return self.__open_transactions

	def load_data(self):
		try:
			with open("blockchain.txt", mode="rb") as file:
				file_content = pickle.loads(file.read())
				self.__chain = file_content["chain"]
				self.__open_transactions = file_content["open_transactions"]
		except IOError:
			pass

	def save_data(self):
		try:
			with open("blockchain.txt", mode="wb") as file:
				data = {
					"chain": self.__chain,
					"open_transactions": self.__open_transactions
				}
				file.write(pickle.dumps(data))
		except IOError:
			print('Saving to file failed!')

	def generate_proof_of_work(self):
		last_block = self.__chain[-1]
		last_hash = hash_util.hash_block(last_block)
		proof = 0
		while not Utils.validate_proof(self.__open_transactions, last_hash, proof):
			proof += 1
		return proof

	def get_balance(self):
		participant = self.hosting_node
		tx_by_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
		open_tx_by_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
		tx_by_sender.append(open_tx_by_sender)
		amount_sent = sum([sum(tx) for tx in tx_by_sender])
		tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
		amount_received = sum([sum(tx) for tx in tx_recipient])
		return amount_received - amount_sent

	def get_last_blockchain_value(self):
		""" Returns the last value of the current blockchain. """
		if len(self.__chain) < 1:
			return None
		return self.__chain[-1]

	def add_transaction(self, recipient, sender, amount=1.0):
		transaction = Transaction(sender, recipient, amount)
		if Utils.verify_transaction(transaction, self.get_balance):
			self.__open_transactions.append(transaction)
			self.save_data()
			return True
		return False

	def mine_block(self):
		last_block = self.__chain[-1]
		hashed_block = hash_util.hash_block(last_block)
		proof = self.generate_proof_of_work()
		reward_transaction = Transaction("MINING", self.hosting_node, MINING_REWARD)
		# shallow copy
		copied_transactions = self.__open_transactions[:]
		copied_transactions.append(reward_transaction)
		block = Block(len(self.__chain), hashed_block, copied_transactions, proof, time())
		self.__chain.append(block)
		self.__open_transactions = []
		self.save_data()
		return True

