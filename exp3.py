import random
import binascii
import bencode
import threading
import SocketServer

# Experiment 3, same as experiment 2, but with multiple nodes listening passively for info hashes

info_hashes = []
discovered_nodes_count = 0


class KRPCRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        global discovered_nodes_count
        try:
            rpc_message = bencode.bdecode(self.request[0].strip())
            rpc_message_type = rpc_message["y"]
        except Exception as e:
            return

        if rpc_message_type == "r":
            if rpc_message["r"].has_key("nodes"):
                with self.server.dht_node.lock:
                    discovered_nodes_count += 1
                for node_id, node_ip, node_port in self.server.dht_node._decode_nodes(rpc_message["r"]['nodes']):
                    self.server.dht_node.bootstrap((node_ip, node_port))

        elif rpc_message_type == "q":
            print "Got RPC query.. "
            query_type = rpc_message["q"]
            if query_type == "get_peers":
                self._handle_get_peers(rpc_message)
            if query_type == "ping":
                self._handle_ping(rpc_message)

    def _handle_ping(self, rpc_message):
        response = bencode.encode({"t": rpc_message["t"],
                                   "y": "r",
                                   "r": {"id": binascii.unhexlify(self.server.dht_node.id)}})
        host, port = self.client_address
        self.server.socket.sendto(response, (host, port))

    def _handle_get_peers(self, rpc_message):
        global info_hashes
        with self.server.dht_node.lock:
            if rpc_message["a"]["info_hash"] not in info_hashes:
                print "Discovered info hash: ", rpc_message["a"]["info_hash"]
                info_hashes.append(rpc_message["a"]["info_hash"])
            if len(info_hashes) == 10:
                print "Discovered 10 infohashes :", info_hashes
                print "Number of nodes discovered: ", discovered_nodes_count
                return
        response = bencode.encode({"t": rpc_message["t"],
                                   "y": "r",
                                   "r": {
                                       "nodes": [], # troll
                                       "id": rpc_message["a"]["id"]
                                   }})
        host, port = self.client_address
        self.server.socket.sendto(response, (host, port))


class DHTServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    def __init__(self, host_address, handler_cls):
        SocketServer.UDPServer.__init__(self, host_address, handler_cls)
        # self.send_lock = threading.Lock()


class DHTNode:
    def __init__(self):
        self.id = self._generateRandom20Bytes()
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

node1 = DHTNode()
node2 = DHTNode()

print node1.bootstrap()
print node2.bootstrap()