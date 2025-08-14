import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# ایجاد جدول محصولات
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    image TEXT
)
''')

conn.commit()
conn.close()
print("دیتابیس و جدول محصولات ساخته شد!")
