import pickle
from time import time

from utils import hash_util
from block import Block
from transaction import Transaction
from utils.verification import Verification
from wallet import Wallet

MINING_REWARD = 10


class Blockchain:
	def __init__(self, public_key, node_id):
		genesis_block = Block(0, "", [], 1014, time())
		self.chain = [genesis_block]
		self.open_transactions = []
		self.public_key = public_key
		self.__peer_nodes = set()
		self.node_id = node_id
		self.load_data()

	@property
	def chain(self):
		return self.__chain[:]

	@chain.setter
	def chain(self, val):
		self.__chain = val

	@property
	def open_transactions(self):
		return self.__open_transactions[:]

	@open_transactions.setter
	def open_transactions(self, val):
		self.__open_transactions = val

	def get_open_transactions(self):
		return self.__open_transactions

	def load_data(self):
		try:
			with open("blockchain-{}.txt".format(self.node_id), mode="rb") as file:
				file_content = pickle.loads(file.read())
				self.chain = file_content["chain"]
				self.open_transactions = file_content["open_transactions"]
				self.__peer_nodes = set(file_content["peer_nodes"])
		except IOError:
			pass

	def save_data(self):
		try:
			with open("blockchain-{}.txt".format(self.node_id), mode="wb") as file:
				data = {
					"chain": self.__chain,
					"open_transactions": self.__open_transactions,
					"peer_nodes": list(self.__peer_nodes)
				}
				file.write(pickle.dumps(data))
		except IOError:
			print('Saving to file failed!')

	def generate_proof_of_work(self):
		last_block = self.__chain[-1]
		last_hash = hash_util.hash_block(last_block)
		proof = 0
		while not Verification.validate_proof(self.__open_transactions, last_hash, proof):
			proof += 1
		return proof

	def get_balance(self):
		if self.public_key is None:
			return None
		participant = self.public_key
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

	def add_transaction(self, recipient, sender, signature, amount=1.0):
		if self.public_key is None:
			return False
		transaction = Transaction(sender, recipient, signature, amount)
		if Verification.verify_transaction(transaction, self.get_balance):
			self.__open_transactions.append(transaction)
			self.save_data()
			return True
		return False

	def mine_block(self):
		if self.public_key is None:
			return None
		last_block = self.__chain[-1]
		hashed_block = hash_util.hash_block(last_block)
		proof = self.generate_proof_of_work()
		reward_transaction = Transaction("MINING", self.public_key, '', MINING_REWARD)
		# shallow copy
		copied_transactions = self.__open_transactions[:]
		for tx in copied_transactions:
			if not Wallet.verify_transaction(tx):
				return None
		copied_transactions.append(reward_transaction)
		block = Block(len(self.__chain), hashed_block, copied_transactions, proof, time())
		self.__chain.append(block)
		self.__open_transactions = []
		self.save_data()
		return block

	def add_peer_node(self, node):
		self.__peer_nodes.add(node)
		self.save_data()

	def remove_peer_node(self, node):
		self.__peer_nodes.discard(node)
		self.save_data()

	def get_peer_nodes(self):
		return list(self.__peer_nodes)