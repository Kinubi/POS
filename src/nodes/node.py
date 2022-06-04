import copy
from utils.blockchainutils import BlockchainUtils
from nodes.message import Message
from nodes.socketcommunication import SocketCommunication
from transaction.transactionpool import TransactionPool
from wallet.wallet import Wallet
from blockchain.blockchain import Blockchain
from nodes.nodeapi import NodeAPI


class Node:

    def __init__(self, ip, port, key=None):
        self.transactionPool = TransactionPool()
        self.wallet = Wallet()
        self.blockchain = Blockchain()
        self.p2p = None
        self.ip = ip
        self.port = port
        if key is not None:
            self.wallet.fromKey(key)

    def startP2P(self):
        self.p2p = SocketCommunication(self.ip, self.port)
        self.p2p.startSocketCommunication(self)

    def startAPI(self, apiPort):
        self.api = NodeAPI()
        self.api.injectNode(self)
        self.api.start(apiPort)

    def handleTransactions(self, transaction):
        data = transaction.payload()
        signature = transaction.signature
        sendersPublicKey = transaction.senderPublicKey
        signatureValid = Wallet.signatureValid(
            data, signature, sendersPublicKey)
        transactionExists = self.transactionPool.transactionExists(transaction)

        if not transactionExists and signatureValid and not self.blockchain.transactionExists(transaction):
            self.transactionPool.addTransaction(transaction)
            message = Message(self.p2p.socketConnector,
                              'TRANSACTION', transaction)
            encodedMessage = BlockchainUtils.encode(message)
            self.p2p.broadcast(encodedMessage)
            forgerRequired = self.transactionPool.forgerRequired()
            if forgerRequired:
                self.forge()

    def forge(self):
        forger = self.blockchain.nextForget()
        if forger == self.wallet.publicKeyString():
            block = self.blockchain.createBlock(
                self.transactionPool.transactions, self.wallet.publicKeyString())
            self.transactionPool.removeFromPool(block.transactions)
            message = Message(self.p2p.socketConnector, 'BLOCK', block)
            encodedMessage = BlockchainUtils.encode(message)
            self.p2p.broadcast(encodedMessage)
        else:
            print("Not I?")

    def handleBlock(self, block):
        forger = block.forger
        blockHash = block.payload()
        signature = block.signature

        blockCountValid = self.blockchain.blockCountValid(block)
        lastBlockHash = self.blockchain.lastBlockHashValid(block)
        forgerValid = self.blockchain.forgerValid(block)
        transactionsValid = self.blockchain.transactionValid(
            block.transactions)
        signatureValid = Wallet.signatureValid(blockHash, signature, forger)
        if not blockCountValid:
            self.requestChain()
        if lastBlockHash and forgerValid and transactionsValid and blockCountValid and signatureValid:
            self.blockchain.addBlock(block)
            self.transactionPool.removeFromPool(block.transactions)
            message = Message(self.p2p.socketConnector, 'BLOCK', block)
            encodedMessage = BlockchainUtils.encode(message)
            self.p2p.broadcast(encodedMessage)

    def requestChain(self):
        message = Message(self.p2p.socketConnector, "BLOCKCHAINREQUEST", None)
        encodedMessage = BlockchainUtils.encode(message)
        self.p2p.broadcast(encodedMessage)

    def handleBlockchainRequest(self, requestingNode):
        message = Message(self.p2p.socketConnector,
                          "BLOCKCHAIN", self.blockchain)
        encodedMessage = BlockchainUtils.encode(message)
        self.p2p.send_to_node(requestingNode, encodedMessage)

    def handleBlockchain(self, blockchain):
        localBlockchainCopy = copy.deepcopy(self.blockchain)
        localBlockCount = len(localBlockchainCopy.blocks)
        receivedBlockCount = len(blockchain.blocks)
        if localBlockCount < receivedBlockCount:
            for blockNumber, block in enumerate(blockchain.blocks):
                if blockNumber >= localBlockCount:
                    localBlockchainCopy.addBlock(block)
                    self.transactionPool.removeFromPool(block.transactions)
        self.blockchain = localBlockchainCopy
