import sqlite3
import pandas as pd
import datetime

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cur = conn.cursor()
exe = cur.execute("select * from LOAN_PERIOD;")

rows = cur.fetchall()
conn.close()

x = datetime.date.today()
print(f'{x.year}/{x.month}/{x.day}')

# d = {}
# for row in rows:
#     temp = dict(row)
#     for key in temp:
#         if key in d:
#             d[key].append(temp[key])
#         else:
#             d[key] = [temp[key]]

# df = pd.DataFrame(d)
# print(df)