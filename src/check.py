import sqlite3

def query_wrestlers(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM wrestlers")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    query_wrestlers("wrestling.db")