import sqlite3
import pandas as pd

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cur = conn.cursor()
exe = cur.execute("select * from LOAN_PERIOD;")

rows = cur.fetchall()
conn.close()


d = {}
for row in rows:
    temp = dict(row)
    for key in temp:
        if key in d:
            d[key].append(temp[key])
        else:
            d[key] = [temp[key]]

df = pd.DataFrame(d)
print(df)