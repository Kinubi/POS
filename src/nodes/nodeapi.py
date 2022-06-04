from flask import Flask, jsonify, request
from flask_classful import FlaskView, route
from utils.blockchainutils import BlockchainUtils

node = None


class NodeAPI(FlaskView):

    def __init__(self):
        self.app = Flask(__name__)

    def start(self, apiPort):
        NodeAPI.register(self.app, route_base='/api')
        self.app.run(host='localhost', port=apiPort)

    def injectNode(self, injectedNode):
        global node
        node = injectedNode

    @route('/info', methods=["GET"])
    def info(self):
        return 'This is a communication interface to a node''s blockchain', 200

    @route('/blockchain', methods=["GET"])
    def blockchain(self):
        return node.blockchain.toJson(), 200

    @route('/transactionpool', methods=["GET"])
    def transactionpool(self):
        return jsonify({i: x.toJson() for i, x in enumerate(node.transactionPool.transactions)}), 200

    @route('/transaction', methods=["POST"])
    def transaction(self):
        values = request.get_json()
        if not 'transaction' in values:
            return 'Missing transaction value', 400
        transaction = BlockchainUtils.decode(values["transaction"])
        node.handleTransactions(transaction)
        response = {"message": 'Received transaction'}
        return jsonify(response), 201
