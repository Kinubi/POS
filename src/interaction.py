from wallet.wallet import Wallet
from utils.blockchainutils import BlockchainUtils
import requests

if __name__ == '__main__':
    bob = Wallet()
    alice = Wallet()
    exchange = Wallet()

    transaction = exchange.createTransaction(
        alice.publicKeyString(), 10, 'EXCHANGE')

    url = 'http://localhost:3000/api/transaction'
    package = {"transaction": BlockchainUtils.encode(transaction)}
    request = requests.request("POST", url, json=package)

    print(request.text)
