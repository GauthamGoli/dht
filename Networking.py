import SocketServer
import bencode
import binascii

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