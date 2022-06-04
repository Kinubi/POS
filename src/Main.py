import sys
from pprint import pprint

from account.accountmodel import AccountModel
from blockchain.blockchain import Blockchain
from blocks.block import Block
from nodes.node import Node
from transaction.transaction import Transaction
from transaction.transactionpool import TransactionPool
from utils.blockchainutils import BlockchainUtils
from wallet.wallet import Wallet

if __name__ == "__main__":

    args = sys.argv
    ip = args[1]
    port = int(args[2])
    apiPort = int(args[3])

    node = Node(ip, port)

    node.startP2P()
    node.startAPI(apiPort)

    