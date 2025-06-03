import sqlite3

def init_db():
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS workouts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 exercise TEXT NOT NULL,
                 duration INTEGER NOT NULL,
                 date TEXT NOT NULL,
                 FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS nutrition (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 food TEXT NOT NULL,
                 calories INTEGER NOT NULL,
                 date TEXT NOT NULL,
                 FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sleep (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 hours REAL NOT NULL,
                 date TEXT NOT NULL,
                 FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS water (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 glasses INTEGER NOT NULL,
                 date TEXT NOT NULL,
                 FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()