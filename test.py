import sqlite3
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

# a = datetime.datetime.strptime("2018-01-31", "%Y-%m-%d")
# a = datetime.datetime.today()
# b = a + relativedelta(months=1)
# print(a)
# print(b)

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cur = conn.cursor()
exe = cur.execute("select MAX(PeriodNumber) from LOAN_PERIOD where ProjectNumber = 1;")
row = dict(cur.fetchone())
for key in row:
    row = row[key]
    break
print(row)


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