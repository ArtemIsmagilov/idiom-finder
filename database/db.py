import sqlite3, os


class Idiom:
    def __enter__(self, file='database.sqlite3'):
        self.conn = sqlite3.connect(f'database/{file}')
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()

    def get(self, name: str):
        self.cur.execute('SELECT * FROM all_idioms WHERE name=?;', (name,))
        return self.cur.fetchone()

    def update(self, from_name: str, to_name: str):
        self.cur.execute('UPDATE all_idioms SET name=? WHERE name=?;', (to_name, from_name))
        return self.cur.fetchone()

    def insert(self, name: str):
        self.cur.execute('INSERT OR IGNORE INTO all_idioms(name) VALUES(?);', (name,))
        return self.cur.fetchone()

    def get_all(self):
        self.cur.execute('SELECT * FROM all_idioms;', )
        return self.cur.fetchall()

    def find(self, sentence: str):
        self.cur.execute("SELECT name FROM all_idioms WHERE ? LIKE '%' || name || '%' AND LENGTH(name) > 6;",
                         (sentence,))
        return self.cur.fetchall()

    def like(self, text: str):
        self.cur.execute("SELECT name FROM all_idioms WHERE name LIKE ? ORDER BY name;", (text,))
        return self.cur.fetchall()

    def removes(self, list_text: list[tuple[str], ...]):
        self.cur.executemany('DELETE FROM all_idioms WHERE name=?;', list_text)
        return self.cur.fetchall()
