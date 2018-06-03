import sqlite3
import constants

def create_db(db_name = constants.DB_NAME):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE infohash
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 hash TEXT UNIQUE NOT NULL,
                 created_timestamp datetime default current_timestamp)''')
    c.execute('''CREATE TABLE node
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 node_id TEXT UNIQUE NOT NULL,
                 ip_addr TEXT NOT NULL,
                 port INTEGER NOT NULL,
                 created_timestamp datetime default current_timestamp)''')
    conn.commit()
    conn.close()

class Session:
    def __init__(self, db_name = constants.DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def save_nodes(self, nodes):
        prepared_statement = 'INSERT INTO node (node_id, ip_addr, port) VALUES (?, ?, ?)'
        for node in nodes:
            try:
                self.c.execute(prepared_statement, node)
                print "{} saved".format(node)
            except sqlite3.IntegrityError:
                print "{} already present".format(node)
                continue
        self.conn.commit()

    def save_infohash(self, info_hashes):
        prepared_statement = 'INSERT INTO infohash (hash) VALUES (?)'
        for info_hash in info_hashes:
            try:
                self.c.execute(prepared_statement, info_hash)
                print "{} saved".format(info_hash)
            except sqlite3.IntegrityError:
                print "{} already present".format(info_hash)
                continue
        self.conn.commit()

    def close(self):
        self.conn.close()

