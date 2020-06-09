from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

INPUT_DICT = {
    'DEBTER': ['Name', 'ID', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber'],
    'CREDITOR': ['Name', 'PhoneNumber'],
    'LOAN_PROJECT_TYPE': ['TypeName', 'TotalPrinciple', 'NumberOfPeriod', 'PrinciplePerPeriod', 'InterestPerPeriod', 'Remark'],
    'LOAN_PROJECT': ['TypeNumber', 'DebterID', 'CreditorNumber', 'StartDate', 'OutstandingAmount'],
    'LOAN_PERIOD': ['RepaymentDate', 'GetPrinciple', 'GetInterest', 'RepaymentMethod', 'Remark'],
    'OWE': ['DebterID', 'CreditorNumber', 'TotalOutstanding']
}

PR_KEY = {
    'DEBTER': ['ID'],
    'CREDITOR': ['CreditorNumber'],
    'LOAN_PROJECT_TYPE': ['TypeNumber'],
    'LOAN_PROJECT': ['ProjectNumber'],
    'LOAN_PERIOD': ['ProjectNumber', 'PeriodNumber'],
    'OWE': ['DebterID', 'CreditorNumber']
}

# DB_DICT = {
#     'DEBTER': ['ID', 'Name', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber', 'EditDate'],
#     'CREDITOR': ['CreditorNumber', 'Name', 'PhoneNumber'],
#     'LOAN_PROJECT_TYPE': ['TypeNumber', 'TypeName', 'PrinciplePerPeriod', 'InterestPerPeriod', 'NumberOfPeriod', 'TotalPrinciple', 'Remark'],
#     'LOAN_PROJECT': ['ProjectNumber', 'TypeNumber', 'DebterID', 'CreditorNumber', 'StartDate', 'OutstandingAmount'],
#     'LOAN_PERIOD': ['ProjectNumber', 'PeriodNumber', 'DueDate', 'RepaymentDate', 'GetPrinciple', 'GetInterest', 'RepaymentMethod', 'Remark'],
#     'OWE': ['DebterID', 'CreditorNumber', 'TotalOutstanding']
# }

# generate dataframe according to the query
def get_query(query):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    exe = cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    output = []
    for row in rows:
        temp = dict(row)
        output.append(list(temp.values()))
    return output

def edit_data(table, add_values = None, edit=False, delete=False, pr_key=[]):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if delete:
        query = f'DELETE FROM {table} WHERE ' + ','.join([f'{PR_KEY[table][i]} = {pr_key[i]}' for i in range(len(pr_key))])
        cur.execute(query)
        conn.commit()
        conn.close()
        return ''
        
    cols = INPUT_DICT[table].copy()
    if table == 'LOAN_PROJECT':
        exe = cur.execute("select TotalPrinciple from LOAN_PROJECT_TYPE where TypeNumber = {};".format(add_values[0]))
        temp = dict(cur.fetchone())
        for key in temp:
            temp = temp[key]
            break
        add_values.append(temp)
        values = add_values.copy()
    
    else:
        values = [request.values[col] for col in cols]
        if table == 'DEBTER':
            values.append(datetime.date.today().strftime("%Y-%m-%d"))
            cols.append('EditDate')
        elif table == 'LOAN_PERIOD':
            # add ProjectNumber
            values.append(add_values[0])
            cols.append('ProjectNumber')

            # add PeriodNumber
            exe = cur.execute("select MAX(PeriodNumber) from LOAN_PERIOD where ProjectNumber = {}".format(add_values[0]))
            temp = dict(cur.fetchone())
            for key in temp:
                temp = temp[key]
                break
            if temp == None: period_number = 1
            else: period_number = temp+1
            values.append(period_number)
            cols.append('PeriodNumber')

            # Add DueDate
            exe = cur.execute("select StartDate from LOAN_PROJECT where ProjectNumber = {}".format(add_values[0]))
            temp = dict(cur.fetchone())
            for key in temp:
                temp = temp[key]
                break
            due = datetime.datetime.strptime(temp, "%Y-%m-%d") + relativedelta(months=period_number)
            values.append(due.strftime("%Y-%m-%d"))
            cols.append('DueDate')

    if edit:
        query = f'UPDATE {table} SET ' + ','.join([f'{col}=?' for col in cols]) + ' WHERE ' + ','.join([f'{PR_KEY[table][i]} = {pr_key[i]}' for i in range(len(pr_key))])
    else:
        query = 'INSERT INTO ' + table + '(' + ','.join(cols) + ')' + ' VALUES(' + ','.join(['?' for col in cols]) + ')'
    cur.execute(query, values)
    conn.commit()
    conn.close()
    return ''

##### Index
@app.route('/')
def index():
    return render_template('index.html')
############################################### Debter ###############################################
##### New Debter
@app.route('/debter', methods=['GET', 'POST'])
def debter():
    if request.method == 'POST':
        edit_data('DEBTER')
    table = get_query("select * from DEBTER;")
    return render_template(
                'debter.html',
                columns=['身份證字號','姓名','公司名稱','戶籍地址','通訊地址','家用電話','行動電話','公司電話','修改日期'],
                table=table
            )

##### Edit Debter
@app.route('/debter/edit/<ID>', methods=['GET', 'POST'])
def debter_edit(ID):
    ID = f"\"{ID}\""
    if request.method == 'POST':
        edit_data('DEBTER', edit=True, pr_key=[ID])
        return redirect(url_for('debter'))
    table = get_query("select * from DEBTER;")
    data = get_query("select {} from DEBTER where ID = {}".format(','.join(INPUT_DICT['DEBTER']), ID))
    print(data)
    return render_template(
                'debter.html',
                columns=['身份證字號','姓名','公司名稱','戶籍地址','通訊地址','家用電話','行動電話','公司電話','修改日期'],
                table=table,
                edit=True,
                data=data[0]
            )

##### Delete Debter
@app.route('/debter/delete/<ID>')
def debter_delete(ID):
    edit_data('DEBTER', delete=True, pr_key=[f"\"{ID}\""])
    return redirect(url_for('debter'))

############################################### Creditor ###############################################
##### New Creditor
@app.route('/creditor', methods=['GET', 'POST'])
def creditor():
    if request.method == 'POST':
        edit_data('CREDITOR')
    table = get_query("select * from CREDITOR;")
    return render_template(
                'creditor.html',
                columns=['編號','姓名','聯絡電話'],
                table=table,
                edit=False
            )

##### Edit Creditor
@app.route('/creditor/edit/<NUMBER>', methods=['GET', 'POST'])
def creditor_edit(NUMBER):
    if request.method == 'POST':
        edit_data('CREDITOR', edit=True, pr_key=[NUMBER])
        return redirect(url_for('creditor'))
    table = get_query("select * from CREDITOR;")
    data = get_query("select {} from CREDITOR where CreditorNumber = {}".format(','.join(INPUT_DICT['CREDITOR']), NUMBER))
    return render_template(
                'creditor.html',
                columns=['編號','姓名','聯絡電話'],
                table=table,
                edit=True,
                data=data[0]
            )

##### Delete Creditor
@app.route('/creditor/delete/<NUMBER>')
def creditor_delete(NUMBER):
    edit_data('CREDITOR', delete=True, pr_key=[NUMBER])
    return redirect(url_for('creditor'))

############################################### Project Type ###############################################
##### New Project Type
@app.route('/project_type', methods=['GET', 'POST'])
def project_type():
    if request.method == 'POST':
        edit_data('LOAN_PROJECT_TYPE')
    table = get_query("select * from LOAN_PROJECT_TYPE;")
    return render_template(
                'project_type.html',
                columns=['案件類型編號','名稱','每月應還本金','每月應還利息','期數','借款金額','備註'],
                table=table
            )

##### Edit Project Type
@app.route('/project_type/edit/<NUMBER>', methods=['GET', 'POST'])
def project_type_edit(NUMBER):
    if request.method == 'POST':
        edit_data('LOAN_PROJECT_TYPE', edit=True, pr_key=[NUMBER])

        return redirect(url_for('project_type'))
    table = get_query("select * from LOAN_PROJECT_TYPE;")
    data = get_query("select {} from LOAN_PROJECT_TYPE where TypeNumber = {}".format(','.join(INPUT_DICT['LOAN_PROJECT_TYPE']), NUMBER))
    return render_template(
                'project_type.html',
                columns=['案件類型編號','名稱','每月應還本金','每月應還利息','期數','借款金額','備註'],
                table=table,
                edit=True,
                data=data[0]
            )

##### Delete Project Type
@app.route('/project_type/delete/<NUMBER>')
def project_type_delete(NUMBER):
    edit_data('LOAN_PROJECT_TYPE', delete=True, pr_key=[NUMBER])
    return redirect(url_for('project_type'))

############################################### Project ###############################################
@app.route('/project', methods=['GET', 'POST'])
def project():
    types = get_query("select TypeNumber,TypeName, TotalPrinciple, NumberOfPeriod from LOAN_PROJECT_TYPE;")
    debters = get_query("select ID, Name from DEBTER;")
    creditors = get_query("select CreditorNumber, Name from CREDITOR;")

    if request.method == 'POST':
        values = []
        for temp in types:
            if f'{temp[0]} {temp[1]}: ${temp[2]}, {temp[3]}期' == request.values['TypeNumber']: values.append(temp[0])
        for temp in debters:
            if f'{temp[0]} {temp[1]}' == request.values['DebterID']: values.append(temp[0])
        for temp in creditors:
            if f'{temp[0]} {temp[1]}' == request.values['CreditorNumber']: values.append(temp[0])

        values.append(request.values['StartDate'])
        edit_data('LOAN_PROJECT', values)

    table = get_query("select * from LOAN_PROJECT;")
    return render_template(
                'project.html',
                types=types,
                debters=debters,
                creditors=creditors,
                columns=['案件編號','類型編號','債務人身份證字號','債權人編號','開始日期','借款金額'],
                table=table
            )

############################################### Period ###############################################
##### New Period
@app.route('/period', methods=['GET', 'POST'])
def period():
    projects = get_query("select ProjectNumber,StartDate from LOAN_PROJECT;")
    if request.method == 'POST':
        for temp in projects:
            if f'{temp[0]}: {temp[1]}' == request.values['ProjectNumber']: break
        
        edit_data('LOAN_PERIOD', [temp[0]])

    table = get_query("select * from LOAN_PERIOD;")
    return render_template(
                'period.html',
                projects=projects,
                columns=['案件編號','期數','預計還款日期','實際還款日期','本金','利息','還款方式','備註'],
                table=table
        )

############################################### Search ###############################################
##### Search Repayment Record
@app.route('/repayment_record', methods=['GET', 'POST'])
def repayment_record():
    projects = get_query("select ProjectNumber,StartDate from LOAN_PROJECT;")
    if request.method == 'POST' and request.values['ProjectNumber'] != '':
        for temp in projects:
            if f'{temp[0]} | {temp[1]}' == request.values['ProjectNumber']: break
        table = get_query("select RepaymentDate, RepaymentMethod, GetPrinciple+GetInterest from LOAN_PERIOD where ProjectNumber = {};".format(temp[0]))
        total_repayment = sum([table[i][2] for i in range(len(table))])
        total_outstanding = get_query("select OutstandingAmount from LOAN_PROJECT where ProjectNumber = {}".format(temp[0]))[0][0]
        total_outstanding = total_outstanding - total_repayment

        return render_template(
                    'repayment_record.html',
                    projects=projects,
                    show=True,
                    project_number=temp[0],
                    project_date=temp[1],
                    total_repayment=total_repayment,
                    total_outstanding=total_outstanding,
                    columns=['繳款日期', '繳款方式', '繳款金額'],
                    table=table
            )
    
    return render_template(
                'repayment_record.html',
                projects=projects,
                show=False
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
