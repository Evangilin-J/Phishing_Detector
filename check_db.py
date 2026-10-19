import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM scan_history")
rows = cursor.fetchall()

print("--- Scan History Records ---")
for row in rows:
    print(row)

conn.close()