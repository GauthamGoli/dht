import random
import binascii
import threading
import bencode
from Networking import KRPCRequestHandler, DHTServer

class DHTNode:
    def __init__(self, node_id):
        self.id = node_id if node_id else self._generateRandom20Bytes()
        self.lock = threading.Lock()
        self.server = DHTServer(('0.0.0.0', 0), KRPCRequestHandler)
        self.server.dht_node = self
        print "DHT Server listening .."
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # self.server_thread.daemon = True
        self.server_thread.start()
        print "DHT Server thread started.."

    def _generateRandom20Bytes(self):
        list = range(256)
        return ''.join([binascii.hexlify(chr(random.choice(list))) for x in range(20)])

    def generateTransactionId(self):
        return binascii.hexlify(chr(random.choice(range(256))))

    def bootstrap(self, node_details = ('82.221.103.244', 6881)):
        # To bootstrap; send a find_node RPC with our node id as the argument
        MESSAGE = bencode.encode({"t": self.generateTransactionId(),
                                  "y": "q",
                                  "q": "find_node",
                                  "a": {"id": binascii.unhexlify(self.id),
                                        "target": binascii.unhexlify(self.id)}})
        self.server.socket.sendto(MESSAGE, node_details)

    def add_seed_nodes(self, seed_nodes):
        self.seed_nodes = seed_nodes

    def _decode_compact_node_info(self, compact_node_info):
        id_part, ip_part, port_part = compact_node_info[:20], compact_node_info[20:24], compact_node_info[24:]
        node_id = binascii.hexlify(id_part)
        ip_addr = '.'.join([str(x) for x in bytearray.fromhex(binascii.hexlify(ip_part))])
        port_no = int(binascii.hexlify(port_part), 16)
        return [node_id, ip_addr, port_no]

    def _decode_nodes(self, list_compact_node_info):
        decoded = []
        for idx in range(0, len(list_compact_node_info), 26):
            if idx + 26 > len(list_compact_node_info):
                break
            decoded.append(self._decode_compact_node_info(list_compact_node_info[idx:idx + 26]))
        return decoded
