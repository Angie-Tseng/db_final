import sqlite3
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

a = [[1,2,3],[1,2,3],[1,2,3]]
# a = pd.DataFrame({'a': [1,2,3]})
# print(a['a'].sum())

# a = datetime.datetime.strptime("2018-01-31", "%Y-%m-%d")
# a = datetime.datetime.today()
# b = a + relativedelta(months=1)
# print(a.strftime("%Y-%m-%d"))
# print(b.strftime("%Y-%m-%d"))

# temp = 200000
# for i in range(20):
#     p = -np.ppmt(rate=0.2/12, per=1, nper=20-i, pv=temp)
#     q = temp * 0.2/12
#     temp = temp - p
#     print(i, int(p), int(q), int(temp))


# project_type = {
#     'TotalPrinciple': 200000,
#     'InterestRate': 0.2,
#     'NumberOfPeriod': 20
# }

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

cur = conn.cursor()
exe = cur.execute("select * from LOAN_PERIOD")
rows = cur.fetchall()
for row in rows:
    temp = dict(row)
    # print(list(temp.values()))


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