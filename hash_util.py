import hashlib
import json


def hash_string_256(string):
	return hashlib.sha256(string).hexdigest()


def hash_block(block):
	return hash_string_256(json.dumps(block.__dict__.copy(), sort_keys=True).encode())