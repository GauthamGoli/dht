import socket
import random
import binascii
import bencode

# Bootstrap with Mainline DHT Node

class DHTNode:
    def __init__(self):
        self.id = self._generateRandom20Bytes()

    def _generateRandom20Bytes(self):
        list = range(256)
        return ''.join([binascii.hexlify(chr(random.choice(list))) for x in range(20)])

    def generateTransactionId(self):
        return binascii.hexlify(chr(random.choice(range(256))))


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

node = DHTNode()

BOOTSTRAP_HOST = "router.utorrent.com"
BOOTSTRAP_PORT = 6881
# To bootstrap; send a find_node RPC with our node id as the argument
MESSAGE = bencode.encode({"t": node.generateTransactionId(),
                          "y": "q",
                          "q": "find_node",
                          "a": {"id": node.id, "target": node.id}})

sock.sendto(MESSAGE, (BOOTSTRAP_HOST, BOOTSTRAP_PORT))

response = bencode.bdecode(sock.recv(4096))
print response['r']['nodes']