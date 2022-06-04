from cryptography.hazmat.primitives.serialization import load_pem_public_key, PublicFormat, Encoding, load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import hashes
from numpy import true_divide
from blocks.block import Block
from transaction.transaction import Transaction
from utils.blockchainutils import BlockchainUtils


class Wallet:

    def __init__(self):
        self.keyPair = rsa.generate_private_key(public_exponent=65537,
                                                key_size=2048)

    def fromKey(self, file):
        with open(file, 'r') as f:
            self.keyPair = load_pem_private_key(f.encode('utf-8'))

    def sign(self, data):
        dataHash = BlockchainUtils.hash(data)
        signature = self.keyPair.sign(dataHash, padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ), utils.Prehashed(hashes.SHA256()))
        return signature.hex()

    def publicKeyString(self):
        publicKey = self.keyPair.public_key()
        publicKeyString = publicKey.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
        return publicKeyString.decode('utf-8')

    def createTransaction(self, receiverPublicKey, amount, type):
        transaction = Transaction(
            self.publicKeyString(), receiverPublicKey, amount, type)
        signature = self.sign(transaction.payload())
        transaction.sign(signature)
        return transaction

    @staticmethod
    def signatureValid(data, signature, publicKeyString):
        signature = bytes.fromhex(signature)
        dataHash = BlockchainUtils.hash(data)
        publicKey = load_pem_public_key(publicKeyString.encode('utf-8'))
        try:
            publicKey.verify(signature, dataHash, padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ), utils.Prehashed(hashes.SHA256()))
            return True
        except:
            return False

    def createBlock(self, transactions, lastHash, blockCount):
        block = Block(transactions, lastHash,
                      self.publicKeyString(), blockCount)
        signature = self.sign(block.payload())
        block.sign(signature)
        return block
