import hashlib

import hash_util


class Utils:
	def verify_chain(self, blockchain):
		for (index, block) in enumerate(blockchain):
			if index == 0:
				continue
			if block.previous_hash != hash_util.hash_block(blockchain[index - 1]):
				return False
			if not self.validate_proof(block.transactions[:-1], block.previous_hash, block.proof):
				print("Proof of work is invalid")
				return False
		return True

	def verify_transaction(self, transaction, get_balance):
		sender_balance = get_balance()
		return sender_balance >= transaction.amount > 0

	def verify_transactions(self, open_transactions, get_balance):
		return all([self.verify_transaction(tx, get_balance) for tx in open_transactions])

	def validate_proof(self, transactions, last_hash, proof):
		guess = (str([tx.convert_to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[0:2] == "00"
