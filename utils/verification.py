import hashlib

from utils import hash_util


class Verification:
	@classmethod
	def verify_chain(cls, blockchain):
		for (index, block) in enumerate(blockchain):
			if index == 0:
				continue
			if block.previous_hash != hash_util.hash_block(blockchain[index - 1]):
				return False
			if not cls.validate_proof(block.transactions[:-1], block.previous_hash, block.proof):
				print("Proof of work is invalid")
				return False
		return True

	@staticmethod
	def verify_transaction(transaction, get_balance):
		sender_balance = get_balance()
		return sender_balance >= transaction.amount > 0

	@classmethod
	def verify_transactions(cls, open_transactions, get_balance):
		return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions])

	@staticmethod
	def validate_proof(transactions, last_hash, proof):
		guess = (str([tx.convert_to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[0:2] == "00"
