import asyncio, shutil, re, aiosqlite, aiohttp, sqlite3, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from database import db


def create_xdxf_table():
    tree = ET.parse('idioms.xml')
    root = tree.getroot()

    session = db.get_conn()
    session.cur.executescript(open('database/create_xdxf_idoms.sql', encoding='utf-8').read())
    session.cur.executemany("INSERT INTO xdxf_idioms(name) VALUES (?);", [[child.text] for child in root.iter('k')])
    session.conn.commit()
    db.close_conn(session)


def create_wiki_table():
    def join_strings(main_domain, link):
        return f'{main_domain}{link}'

    async def insert_idiom(idiom):
        async with conn.execute('INSERT INTO idiom(name) VALUES(?) RETURNING *;', (idiom,)) as cur:
            return await cur.fetchone()

    async def insert_form_idiom(form_idiom, idiom_id):
        async with conn.execute('INSERT INTO form_idiom(name, idiom_id) VALUES(?, ?) RETURNING *;',
                                (form_idiom, idiom_id)) as cur:
            return await cur.fetchone()

    async def main():
        global conn

        domain = 'https://en.wiktionary.org'
        next_page = join_strings(domain, '/w/index.php?title=Category:English_idioms')

        async with aiohttp.ClientSession() as client, aiosqlite.connect('database.sqlite3') as conn:
            conn.row_factory = aiosqlite.Row

            await conn.executescript(open('database/init_db.sql', encoding='utf-8').read())

            while next_page:
                async with client.get(next_page) as response:
                    html = await response.text()

                soup = BeautifulSoup(html, 'lxml')
                page = soup.find('div', id='mw-pages')

                next_body = soup.find('a', title='Category:English idioms', string=re.compile("next page"))
                if next_body:
                    next_page = join_strings(domain, next_body.get('href'))
                else:
                    next_page = None
                page_idioms = page.find_all('li')

                for element in page_idioms:

                    async with client.get(join_strings(domain, element.a.get('href'))) as sub_response:
                        sub_html = await sub_response.text()

                    sub_soup = BeautifulSoup(sub_html, 'lxml')
                    another_words = sub_soup.find_all('b', class_=re.compile('Latn form-of lang-en'))
                    idiom = element.a.get('title')

                    return_idiom = await insert_idiom(idiom)

                    for w in another_words:
                        form_idiom = w.text
                        print(form_idiom)
                        await insert_form_idiom(form_idiom, return_idiom['id'])
                    # print(idiom)

            await conn.executescript(open('database/create_wiki_idioms.sql', encoding='utf-8').read())
            await conn.commit()

    asyncio.run(main())
    print('exit')


def create_all_idioms():
    session = db.get_conn()
    session.cur.executescript(open('database/create_all_idoms.sql', encoding='utf-8').read())
    session.conn.commit()
    db.close_conn(session)


def extend_pronouns():
    with (open('database/pronouns.txt', encoding='utf-8') as pr_file,
          open('database/indefinite-pronouns.txt', encoding='utf-8') as in_pr_file,
          ):
        session = db.get_conn()
        results = session.get_all()

        pr = pr_file.read().splitlines(keepends=False)
        in_pr = in_pr_file.read().splitlines()

        for r in results:
            for s2 in in_pr:
                line = s2.strip()
                if not line:
                    continue
                if line.lower() in r['name'].lower():
                    for s1 in pr:
                        line2 = s1.strip()
                        if not line2:
                            continue
                        session.insert(r['name'].replace(line.lower(), line2.lower()))
        session.conn.commit()
        db.close_conn(session)
        print('extend pronouns completed')


def create_default_db():
    shutil.copyfile('database/database.sqlite3', 'database/database_default.sqlite3')


if __name__ == '__main__':
    ...
    # create_xdxf_table()
    # create_wiki_table()
    # create_all_idioms()
    # extend_pronouns()
    # create_default_db()
