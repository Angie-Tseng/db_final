import sqlite3
import pandas as pd
import datetime

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cur = conn.cursor()
exe = cur.execute("select TotalPrinciple from LOAN_PROJECT_TYPE where TypeNumber = 1;")

row = dict(cur.fetchone())
for key in row:
    row = row[key]
    break
print(row)

for i, j in range(5), range(5):
    print(i,j)

# rows = cur.fetchall()

# # x = datetime.date.today()
# # print(f'{x.year}/{x.month}/{x.day}')

# d = {}
# for row in rows:
#     temp = dict(row)
#     print(temp)
#     for key in temp:
#         if key in d:
#             d[key].append(temp[key])
#         else:
#             d[key] = [temp[key]]

# df = pd.DataFrame(d)
# print(df)



conn.close()