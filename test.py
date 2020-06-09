import sqlite3
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

# a = pd.DataFrame({'a': [1,2,3]})
# print(a['a'].sum())

# a = datetime.datetime.strptime("2018-01-31", "%Y-%m-%d")
# a = datetime.datetime.today()
# b = a + relativedelta(months=1)
# print(a.strftime("%Y-%m-%d"))
# print(b.strftime("%Y-%m-%d"))

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cur = conn.cursor()
exe = cur.execute("select * from LOAN_PERIOD")
rows = cur.fetchall()
for row in rows:
    temp = dict(row)
    print(list(temp.values()))


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