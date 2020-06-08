from flask import Flask, request, render_template
import pandas as pd
import sqlite3
import datetime

app = Flask(__name__)

INPUT_DICT = {
    'DEBTER': ['ID', 'Name', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber'],
    'CREDITOR': ['Name', 'PhoneNumber'],
    'LOAN_PROJECT_TYPE': ['TypeName', 'PrinciplePerPeriod', 'InterestPerPeriod', 'NumberOfPeriod', 'TotalPrinciple', 'Remark'],
    'LOAN_PROJECT': ['TypeNumber', 'DebterID', 'CreditorNumber', 'StartDate'],
    'LOAN_PERIOD': ['ProjectNumber', 'DueDate', 'RepaymentDate', 'GetPrinciple', 'GetInterest', 'RepaymentMethod', 'Remark'],
    'OWE': ['DebterID', 'CreditorNumber', 'TotalOutstanding']
}

DB_DICT = {
    'DEBTER': ['ID', 'Name', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber', 'EditDate'],
    'CREDITOR': ['CreditorNumber', 'Name', 'PhoneNumber'],
    'LOAN_PROJECT_TYPE': ['TypeNumber', 'TypeName', 'PrinciplePerPeriod', 'InterestPerPeriod', 'NumberOfPeriod', 'TotalPrinciple', 'Remark'],
    'LOAN_PROJECT': ['ProjectNumber', 'TypeNumber', 'DebterID', 'CreditorNumber', 'StartDate', 'OutstandingAmount'],
    'LOAN_PERIOD': ['ProjectNumber', 'PeriodNumber', 'DueDate', 'RepaymentDate', 'GetPrinciple', 'GetInterest', 'RepaymentMethod', 'Remark'],
    'OWE': ['DebterID', 'CreditorNumber', 'TotalOutstanding']
}

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


def insert_data(table):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cols = INPUT_DICT[table]
    values = [request.values[col] for col in cols]
    if table == 'DEBTER':
        values.append(datetime.date.today())
        cols.append('EditDate')

    elif table == 'LOAN_PROJECT':
        exe = cur.execute("select TotalPrinciple from LOAN_PROJECT_TYPE where TypeNumber = {};".format(request.values['TypeNumber']))
        temp = dict(cur.fetchone())
        for k in temp:
            temp = temp[key]
            break
        print(temp)
        values.append(temp)
        cols.append('OutstandingAmount')
        

    query = 'INSERT INTO ' + table + '(' + ','.join(cols) + ')' + ' VALUES(' + ','.join(['?' for col in cols]) + ')'
    print(query)
    cur.execute(query, values)
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
        # insert_data('DEBTER', ['ID', 'Name', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber', 'DateCreate'])
        insert_data('DEBTER')
    df = get_query("select * from DEBTER;")
    return render_template('new_debter.html', tables=[df.to_html(classes='data')])


##### New Creditor
@app.route('/new_creditor', methods=['GET', 'POST'])
def new_creditor():
    if request.method == 'POST':
        # insert_data('CREDITOR', ['Name', 'PhoneNumber'])
        insert_data('CREDITOR')
    df = get_query("select * from CREDITOR;")
    return render_template('new_creditor.html', tables=[df.to_html(classes='data')])


##### New Project Type
@app.route('/new_project_type', methods=['GET', 'POST'])
def new_project_type():
    if request.method == 'POST':
        # insert_data('LOAN_PROJECT_TYPE', ['TypeName', 'PrinciplePerPeriod', 'InterestPerPeriod', 'NumberOfPeriod', 'TotalPrinciple', 'Remark'])
        insert_data('LOAN_PROJECT_TYPE')
    df = get_query("select * from LOAN_PROJECT_TYPE;")
    return render_template('new_project_type.html', tables=[df.to_html(classes='data')])

@app.route('/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        # insert_data('LOAN_PROJECT_TYPE', ['TypeName', 'PrinciplePerPeriod', 'InterestPerPeriod', 'NumberOfPeriod', 'TotalPrinciple', 'Remark'])
        insert_data('LOAN_PROJECT')
    
    types = get_query("select TypeNumber,TypeName from LOAN_PROJECT_TYPE;")
    table = get_query("select * from LOAN_PROJECT;")
    print(types.values.tolist())

    return render_template(
                'new_project.html',
                types=types.values.tolist(),
                tables=[table.to_html(classes='data')]
            )


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
