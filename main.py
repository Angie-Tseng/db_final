from flask import Flask, request, render_template
import pandas as pd
import sqlite3

app = Flask(__name__)

# generate dataframe according to the query
def get_query(query):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    exe = cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    d = {}
    for row in rows:
        temp = dict(row)
        for key in temp:
            if key in d:d[key].append(temp[key])
            else:       d[key] = [temp[key]]
    df = pd.DataFrame(d)
    return df


def insert_data(table, cols):
    query = 'INSERT INTO ' + table + '(' + ','.join(cols) + ')' + ' VALUES(' + ','.join(['?' for col in cols]) + ')'
    print(query)
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, [request.values[col] for col in cols])
    conn.commit()
    conn.close()
    return ''

##### Index
@app.route('/')
def index():
    return render_template('index.html')

##### New Debter
@app.route('/new_debter', methods=['GET', 'POST'])
def new_debter():
    if request.method == 'POST':
        insert_data('DEBTER', ['ID', 'Name', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber', 'DateCreate'])
    df = get_query("select * from DEBTER;")
    return render_template('new_debter.html', tables=[df.to_html(classes='data')], titles=df.columns.values)


##### New Creditor
@app.route('/new_creditor', methods=['GET', 'POST'])
def new_creditor():
    if request.method == 'POST':
        insert_data('CREDITOR', ['Name', 'PhoneNumber'])
    df = get_query("select * from CREDITOR;")
    return render_template('new_creditor.html', tables=[df.to_html(classes='data')], titles=df.columns.values)


##### New Project Type
@app.route('/new_project_type', methods=['GET', 'POST'])
def new_project_type():
    if request.method == 'POST':
        insert_data('LOAN_PROJECT_TYPE', ['TypeName', 'PrinciplePerPeriod', 'InterestPerPeriod', 'NumberOfPeriod', 'TotalPrinciple', 'Remark'])
    df = get_query("select * from LOAN_PROJECT_TYPE;")
    return render_template('new_project_type.html', tables=[df.to_html(classes='data')], titles=df.columns.values)


##### SQL Query
@app.route('/sql', methods=['GET', 'POST'])
def sql_query():
    if request.method == 'POST' and request.values['query'] != '':
        df = get_query(request.values['query'])
        return render_template('sql.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

    return render_template('sql.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
