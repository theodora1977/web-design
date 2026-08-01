import sqlite3

conn = sqlite3.connect('tailor.db')
cur = conn.cursor()
try:
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print('tables:', tables)
    for t in tables:
        try:
            cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception as e:
            cnt = f'error: {e}'
        print(t, 'rows:', cnt)
finally:
    conn.close()
