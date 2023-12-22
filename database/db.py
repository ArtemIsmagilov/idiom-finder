import sqlite3
from threading import Thread
import re
from sqlite3 import Cursor, Connection, Row


def get_conn(database='database.sqlite3', *args, **kwargs) -> Cursor:
    conn = sqlite3.connect(f'database/{database}', *args, **kwargs)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return cur


def close_conn(cur: Cursor):
    cur.close()
    cur.connection.close()


def get(cur: Cursor, name: str) -> Row | None:
    cur.execute('SELECT * FROM all_idioms WHERE name=?;', (name,))
    return cur.fetchone()


def get_all(cur: Cursor) -> list[Row]:
    cur.execute('SELECT name FROM all_idioms;', )
    return cur.fetchall()


def update(cur: Cursor, from_name: str, to_name: str) -> Row | None:
    cur.execute('UPDATE all_idioms SET name=:to_name WHERE name=:from_name;', {'to_name': to_name, 'from_name': from_name})
    return cur.fetchone()


def insert(cur: Cursor, name: str):
    cur.execute('INSERT INTO all_idioms(name) VALUES(:name);', {'name': name})


def find(cur: Cursor, text: str) -> list[Row | None]:
    data = tuple({'sentence': re.sub(r' {2,}', ' ', l.strip())} for l in re.split(r'[?.!]+', re.sub(r'\n| {2,}|\.{2,}', ' ', text)) if l.strip())
    cur.execute('CREATE TEMP TABLE temp_sentences(sentence PRIMARY KEY);')
    cur.executemany('INSERT OR IGNORE INTO temp_sentences VALUES(:sentence);', data)
    cur.execute("""
    SELECT sentence, GROUP_CONCAT(name) AS names FROM temp_sentences, all_idioms
    WHERE INSTR(sentence, name) > 0 AND LENGTH(name) > 6 GROUP BY sentence;
    """, )
    return cur.fetchall()

def like(cur: Cursor, text: str) -> list[Row | None]:
    cur.execute("SELECT name FROM all_idioms WHERE name LIKE :name ORDER BY name;", {'name': text})
    return cur.fetchall()


def removes(cur: Cursor, container_text: dict[str, str]) -> list[Row | None]:
    cur.execute('DELETE FROM all_idioms WHERE name in (:names)', container_text)
    return cur.fetchall()
