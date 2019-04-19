from uuid import uuid4

from utils import Utils
from blockchain import Blockchain


class Node:
	def __init__(self):
		# self.id = str(uuid4())
		self.id = 'Ting'
		self.blockchain = Blockchain(self.id)

	def prompt_for_input(self):
		while True:
			print("Please choose")
			print("1: Add a new transaction value")
			print("2: Mine a block")
			print("3: Print blocks")
			print("4: Check validity of all transactions")
			print("q: Quit")
			user_choice = self.get_user_choice()
			if user_choice == "1":
				tx_data = self.get_transaction_value()
				recipient, amount = tx_data
				if self.blockchain.add_transaction(recipient, self.id, amount=amount):
					print("Added transaction")
				else:
					print("Transaction failed")
			elif user_choice == "2":
				self.blockchain.mine_block()
			elif user_choice == "3":
				self.print_blockchain_elements()
			elif user_choice == "4":
				verifier = Utils()
				verifier.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance)
			elif user_choice == "q":
				break
			else:
				print("Input was invalid, please pick a value from the list!")
			verifier = Utils()
			if not verifier.verify_chain(self.blockchain.chain):
				print("Invalid blockchain!")
				break
			print("Balance of {}: {:*^10.2f}".format(self.id, self.blockchain.get_balance()))
		print("Done!")

	def get_user_choice(self):
		user_input = input("Your choice: ")
		return user_input

	def print_blockchain_elements(self):
		# Output the blockchain list to the console
		for block in self.blockchain.chain:
			print("Outputting Block")
			print(block)

	def get_transaction_value(self):
		tx_recipient = input("Enter the recipient of the transaction:")
		tx_amount = float(input("Your transaction amount please: "))
		return tx_recipient, tx_amount


node = Node()
node.prompt_for_input()
