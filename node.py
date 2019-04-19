from utils.verification import Verification
from blockchain import Blockchain
from wallet import Wallet


class Node:
	def __init__(self):
		# self.wallet.public_key = str(uuid4())
		self.wallet = Wallet()
		self.wallet.create_keys()
		self.blockchain = Blockchain(self.wallet.public_key)

	def prompt_for_input(self):
		while True:
			print("Please choose")
			print("1: Add a new transaction value")
			print("2: Mine a block")
			print("3: Print blocks")
			print("4: Check validity of all transactions")
			print("5: Create wallet, make sure to save too")
			print("6: Load wallet")
			print("7: Save wallet")
			print("q: Quit")
			user_choice = self.get_user_choice()
			if user_choice == "1":
				tx_data = self.get_transaction_value()
				recipient, amount = tx_data
				if self.blockchain.add_transaction(recipient, self.wallet.public_key, amount=amount):
					print("Added transaction")
				else:
					print("Transaction failed")
			elif user_choice == "2":
				if not self.blockchain.mine_block():
					print("No wallet found, mining failed")
			elif user_choice == "3":
				self.print_blockchain_elements()
			elif user_choice == "4":
				if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
					print("All transactions are valid")
				else:
					print("There are invalid transactions")
			elif user_choice == "5":
				self.wallet.create_keys()
				self.blockchain = Blockchain(self.wallet.public_key)
			elif user_choice == "6":
				self.wallet.load_keys()
				self.blockchain = Blockchain(self.wallet.public_key)
			elif user_choice == "7":
				self.wallet.save_keys()
			elif user_choice == "q":
				break
			else:
				print("Input was invalid, please pick a value from the list!")
			if not Verification.verify_chain(self.blockchain.chain):
				print("Invalid blockchain!")
				break
			print("Balance of {}: {:*^10.2f}".format(self.wallet.public_key, self.blockchain.get_balance()))
		print("Done!")

	@staticmethod
	def get_user_choice():
		user_input = input("Your choice: ")
		return user_input

	def print_blockchain_elements(self):
		# Output the blockchain list to the console
		for block in self.blockchain.chain:
			print("Outputting Block")
			print(block)

	@staticmethod
	def get_transaction_value():
		tx_recipient = input("Enter the recipient of the transaction:")
		tx_amount = float(input("Your transaction amount please: "))
		return tx_recipient, tx_amount


if __name__ == '__main__':
	node = Node()
	node.prompt_for_input()
