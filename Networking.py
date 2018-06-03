import SocketServer
import bencode
import binascii
from DbApi import Session

db_writer = Session()

class KRPCRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        global db_writer
        try:
            rpc_message = bencode.bdecode(self.request[0].strip())
            rpc_message_type = rpc_message["y"]
        except Exception as e:
            return

        if rpc_message_type == "r":
            if rpc_message["r"].has_key("nodes"):
                node_store = []
                for node_id, node_ip, node_port in self.server.dht_node._decode_nodes(rpc_message["r"]['nodes']):
                    node_store.append((node_id, node_ip, node_port))
                    self.server.dht_node.bootstrap((node_ip, node_port))
                # Persist discovered nodes
                with self.server.dht_node.lock:
                    db_writer.save_nodes(node_store)

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
        global db_writer
        with self.server.dht_node.lock:
            db_writer.save_infohash([rpc_message["a"]["info_hash"]])
            print "Discovered info hash: ", rpc_message["a"]["info_hash"]
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