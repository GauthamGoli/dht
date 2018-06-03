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
                (id INTEGER PRIMARY KEY AUTOINCREMENT ,
                 ip_addr TEXT UNIQUE NOT NULL,
                 created_timestamp datetime default current_timestamp)''')
    conn.commit()
    conn.close()

class Session:
    def __init__(self, db_name = constants.DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def save_nodes(self, nodes):
        self.c.executemany('INSERT INTO node (ip_addr) VALUES (?)', nodes)
        self.conn.commit()

    def save_infohash(self, info_hash):
        self.c.executemany('INSERT INTO infohash (hash) VALUES (?)', info_hash)
        self.conn.commit()

    def close(self):
        self.conn.close()

