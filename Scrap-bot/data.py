import datetime
import sqlite3


def create_db():
    conn = sqlite3.connect('steam_links.db')
    cursor = conn.cursor()

    # Создаем таблицу Steam-Links
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Steam_Links (
            link TEXT PRIMARY KEY
        )
    ''')

    # Создаем таблицу Dynamic
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MarketPlace (
            link TEXT,
            date DATE,
            json JSON,
            FOREIGN KEY (link) REFERENCES Steam_Links(link) ON DELETE CASCADE
        )
    ''')

    # Создаем дочернюю таблицу CSMoney
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CSMoney (
            link TEXT,
            date DATE,
            name TEXT NOT NULL,
            count INTEGER,
            price REAL,
            FOREIGN KEY (link) REFERENCES Steam_Links(link) ON DELETE CASCADE
        )
    ''')

    # Сохраняем изменения и закрываем соединение с базой данных
    conn.commit()
    conn.close()


def save_data_CSM(items):
    conn = sqlite3.connect('steam_links.db')
    cursor = conn.cursor()

    for link, name, date, count, price in items:
        existing_count = cursor.execute("SELECT count FROM CSMoney WHERE link = ? AND date = ? AND price = ?", (link, date, price)).fetchone()

        cursor.execute('INSERT OR IGNORE INTO Steam_Links (link) VALUES (?)', (link,))

        if existing_count:
            new_quantity = int(existing_count[0]) + count

            cursor.execute(f"UPDATE CSMoney SET count = ? WHERE link = ? AND date = ? AND price = ?",
                           (new_quantity, link, date, price))
        else:
            cursor.execute(f"DELETE FROM CSMoney WHERE date != ? AND link == ?",(date, link))
            cursor.execute(f"INSERT INTO CSMoney (link, name, date, count, price) VALUES (?, ?, ?, ?, ?)",
                           (link, name, date, count, price))

    conn.commit()
    conn.close()


def steam_links():
    conn = sqlite3.connect('steam_links.db')
    cursor = conn.cursor()

    links = cursor.execute("SELECT link FROM Steam_Links").fetchall()

    conn.close()

    return links


def save_data_SM(link, date, json):
    conn = sqlite3.connect('steam_links.db')
    cursor = conn.cursor()

    cursor.execute("INSERT OR REPLACE INTO MarketPlace (link, date, json) VALUES (?, ?, ?)",
                   (link, date, json))

    conn.commit()
    conn.close()

create_db()