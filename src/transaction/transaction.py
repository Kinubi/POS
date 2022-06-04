from uuid import uuid4
from datetime import datetime
import copy

class Transaction:


    def __init__(self, senderPublicKey, receiverPublicKey, amount, type):
        self.senderPublicKey = senderPublicKey
        self.receiverPublicKey = receiverPublicKey
        self.amount = amount
        self.type = type
        self.id = uuid4().hex
        self.timestamp = datetime.now().timestamp()
        self.signature = ''

    def toJson(self):
        return self.__dict__
        
    def sign(self, signature):
        self.signature = signature

    def payload(self):
        jsonRepresentation = copy.deepcopy(self.toJson())
        jsonRepresentation["signature"] = ""
        return jsonRepresentation

    def equals(self, transaction):
        if self.id == transaction.id:
            return True
        return False


        