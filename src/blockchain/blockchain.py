from proofofstake.proofofstake import ProofOfStake
from account.accountmodel import AccountModel
from utils.blockchainutils import BlockchainUtils
from blocks.block import Block


class Blockchain():
    def __init__(self):
        self.blocks = [Block.genesis()]
        self.accountModel = AccountModel()
        self.pos = ProofOfStake()

    def addBlock(self, block):
        self.executeTransactions(block.transactions)
        self.blocks.append(block)

    def toJson(self):
        data = {}
        data["blocks"] = [x.toJson() for x in self.blocks]
        return data

    def blockCountValid(self, block):
        if self.blocks[-1].blockCount == block.blockCount - 1:
            return True
        return False

    def lastBlockHashValid(self, block):
        latestBlockchainBlockHash = BlockchainUtils.hash(
            self.blocks[-1].payload()).hex()
        if latestBlockchainBlockHash == block.lastHash:
            return True
        return False

    def getCoveredTransactionSet(self, transactions):
        coveredTransactions = [
            x for x in transactions if self.transactionCovered(x)]
        return coveredTransactions

    def transactionCovered(self, transaction):
        if transaction.type == 'EXCHANGE':
            return True
        senderBalance = self.accountModel.getBalance(
            transaction.senderPublicKey)
        if senderBalance >= transaction.amount:
            return True
        return False

    def executeTransactions(self, transactions):
        for transaction in transactions:
            self.executeTransaction(transaction)

    def executeTransaction(self, transaction):
        if transaction.type == "STAKE":
            sender = transaction.senderPublicKey
            receiver = transaction.receiverPublicKey
            if sender == receiver:
                amount = transaction.amount
                self.pos.update(sender, amount)
                self.accountModel.updateBalance(sender, -amount)
        else:
            sender = transaction.senderPublicKey
            receiver = transaction.receiverPublicKey
            amount = transaction.amount
            self.accountModel.updateBalance(sender, -amount)
            self.accountModel.updateBalance(receiver, amount)

    def nextForger(self):
        lastBlockHash = BlockchainUtils.hash(self.blocks[-1].payload()).hex()
        nextForger = self.pos.forger(lastBlockHash)
        return nextForger

    def createBlock(self, transactionFromPool, forgerWallet):
        coveredTransactions = self.getCoveredTransactionSet(
            transactionFromPool)
        self.executeTransactions(coveredTransactions)
        newBlock = forgerWallet.createBlock(coveredTransactions, BlockchainUtils.hash(
            self.blocks[-1].payload()).hex(), len(self.blocks))
        self.blocks.append(newBlock)
        return newBlock

    def transactionExists(self, transaction):
        for block in self.blocks:
            for blockTransaction in block.transactions:
                if transaction.equal(blockTransaction):
                    return True
        return False

    def forgerValid(self, block):
        forgerPublicKey = self.pos.forger(block.lastHash)
        proposedBlockForger = block.forger
        if forgerPublicKey == proposedBlockForger:
            return True
        return False

    def transactionValid(self, transactions):
        coveredTransactions = self.getCoveredTransactionSet(transactions)
        if len(coveredTransactions) == len(transactions):
            return True
        return False
