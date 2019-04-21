from Cryptodome.PublicKey import RSA
from Cryptodome import Random
import binascii


class Wallet:
	def __init__(self):
		self.private_key = None
		self.public_key = None

	def create_keys(self):
		private_key, public_key = self.generate_keys()
		self.private_key = private_key
		self.public_key = public_key

	def load_keys(self):
		try:
			with open('wallet.txt', mode='r') as file:
				keys = file.readlines()
				public_key = keys[0][:-1]
				private_key = keys[1]
				self.public_key = public_key
				self.private_key = private_key
		except (IOError, IndexError):
			print("Failed to load wallet")

	def save_keys(self):
		try:
			with open('wallet.txt', mode='w') as file:
				file.write(self.public_key)
				file.write('\n')
				file.write(self.private_key)
		except IOError:
			print("Failed to save wallet")

	def generate_keys(self):
		private_key = RSA.generate(1024, Random.new().read)
		public_key = private_key.publickey()
		return (
			binascii.hexlify(private_key.export_key(format='DER')).decode('ascii'),
			binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
		)