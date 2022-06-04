from cryptography.hazmat.primitives import hashes
import json
import jsonpickle


class BlockchainUtils:

    @staticmethod
    def hash(data):
        dataString = json.dumps(data)
        dataBytes = dataString.encode('utf-8')
        digest = hashes.Hash(hashes.SHA256())
        digest.update(dataBytes)
        dataHash = digest.finalize()
        return dataHash

    @staticmethod
    def encode(objectToEncode):
        return jsonpickle.encode(objectToEncode, unpicklable=True)

    @staticmethod
    def decode(encodedObject):
        return jsonpickle.decode(encodedObject)
