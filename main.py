from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

app = Flask(__name__)

INPUT_DICT = {
    'DEBTER': ['Name', 'ID', 'CompanyName', 'ResidenceAddress', 'MailingAddress', 'TelPhoneNumber', 'MobilePhoneNumber', 'CompanyPhoneNumber'],
    'CREDITOR': ['Name', 'PhoneNumber'],
    'LOAN_PROJECT_TYPE': ['TypeName', 'TotalPrinciple', 'InterestRate', 'NumberOfPeriod', 'Remark'],
    'LOAN_PROJECT': ['TypeNumber', 'DebterID', 'CreditorNumber', 'StartDate'],
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

# generate dataframe according to the query
def get_query(query , get_col=False):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    output = []
    cols = []
    for row in rows:
        temp = dict(row)
        output.append(list(temp.values()))
        if get_col: cols = list(temp.keys())

    if get_col:
        return output, cols
    return output

def edit_data(table, add_values = None, edit=False, delete=False, pr_key=[], from_project=False):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        if delete:
            query = f'DELETE FROM {table} WHERE ' + ','.join([f'{PR_KEY[table][i]} = {pr_key[i]}' for i in range(len(pr_key))])
            cur.execute(query)
            conn.commit()
            conn.close()
            return ''
            
        cols = INPUT_DICT[table].copy()
        if table == 'LOAN_PROJECT':
            values = add_values.copy()
        elif table == 'LOAN_PERIOD' and from_project:
            # add ProjectNumber, PeriodNumber and DueDate
            values = add_values.copy()
            cols = ['ProjectNumber', 'PeriodNumber', 'DueDate', 'ExpectPrinciple', 'ExpectInterest']
        else:
            values = [request.values[col] for col in cols]
            if table == 'DEBTER':
                values.append(datetime.date.today().strftime("%Y-%m-%d"))
                cols.append('EditDate')
            elif table == 'LOAN_PERIOD':
                # add ProjectNumber and PeriodNumber
                values.extend(add_values)
                cols.extend(['ProjectNumber', 'PeriodNumber'])

        if edit:
            query = f'UPDATE {table} SET ' + ','.join([f'{col}=?' for col in cols]) + ' WHERE ' + ' AND '.join([f'{PR_KEY[table][i]} = {pr_key[i]}' for i in range(len(pr_key))])
            output = 0
        else:
            query = 'INSERT INTO ' + table + '(' + ','.join(cols) + ')' + ' VALUES(' + ','.join(['?' for col in cols]) + ')'
            
        cur.execute(query, values)
        if table in ['CREDITOR', 'LOAN_PROJECT_TYPE', 'LOAN_PROJECT', 'LOAN_PERIOD'] and not edit:
            output = cur.lastrowid
        else:
            output = 0

        conn.commit()
        conn.close()
        return output
    except Exception as e:
        conn.close()
        print(e)
        return -1

def edit_periods(ProjectNumber, delete=False):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select StartDate, TypeNumber from LOAN_PROJECT where ProjectNumber = {}".format(ProjectNumber))
    project = dict(cur.fetchone())
    
    start_date = datetime.datetime.strptime(project['StartDate'], "%Y-%m-%d")
    cur.execute("select * from LOAN_PROJECT_TYPE where TypeNumber = {}".format(project['TypeNumber']))
    project_type = dict(cur.fetchone())

    temp = project_type['TotalPrinciple']
    rate = project_type['InterestRate']/12

    for period in range(project_type['NumberOfPeriod']):
        if delete:
            edit_data('LOAN_PERIOD', [ProjectNumber, period])
        else:
            due = start_date + relativedelta(months=period+1)
            principle = np.ceil(-np.ppmt(rate=rate, per=1, nper=20-period, pv=temp))
            interest = np.ceil(temp * rate)
            temp -= principle
            edit_data('LOAN_PERIOD', [ProjectNumber, period+1, due.strftime("%Y-%m-%d"), int(principle), int(interest)], from_project=True)
        
    
    conn.commit()
    conn.close()
    return

############################################### Index ###############################################
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
                columns=['債權人編號','姓名','聯絡電話'],
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
                columns=['債權人編號','姓名','聯絡電話'],
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
                columns=['類型編號','名稱','借款金額','年利率','期數','備註'],
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
                columns=['類型編號','名稱','借款金額','年利率','期數','備註'],
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
        project_number = edit_data('LOAN_PROJECT', values)
        edit_periods(project_number)

    table = get_query("select * from LOAN_PROJECT;")
    return render_template(
                'project.html',
                types=types,
                debters=debters,
                creditors=creditors,
                columns=['案件編號','類型編號','債務人身份證字號','債權人編號','開始日期'],
                table=table
            )

@app.route('/project/edit/<NUMBER>', methods=['GET', 'POST'])
def project_edit(NUMBER):
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
        edit_periods(NUMBER, delete=True)
        edit_data('LOAN_PROJECT', add_values=values, edit=True, pr_key=[NUMBER])
        edit_periods(NUMBER)
        return redirect(url_for('project'))

    table = get_query("select * from LOAN_PROJECT;")
    data = get_query("select {} from LOAN_PROJECT where ProjectNumber = {}".format(','.join(INPUT_DICT['LOAN_PROJECT']), NUMBER))
    data = data[0].copy()
    for temp in types:
        if temp[0] == data[0]:
            data[0] = f'{temp[0]} {temp[1]}: ${temp[2]}, {temp[3]}期'
            break
    for temp in debters:
        if temp[0] == data[1]:
            data[1] = f'{temp[0]} {temp[1]}'
            break
    for temp in creditors:
        if temp[0] == data[2]:
            data[2] = f'{temp[0]} {temp[1]}'
            break
    return render_template(
                'project.html',
                types=types,
                debters=debters,
                creditors=creditors,
                columns=['案件編號','類型編號','債務人身份證字號','債權人編號','開始日期'],
                table=table,
                edit=True,
                data=data
            )

##### Delete Project
@app.route('/project/delete/<NUMBER>')
def project_delete(NUMBER):
    edit_periods(NUMBER, delete=True)
    edit_data('LOAN_PROJECT', delete=True, pr_key=[NUMBER])
    return redirect(url_for('project'))

############################################### Period ###############################################
##### Choose Period
@app.route('/period', methods=['GET', 'POST'])
def period():
    projects = get_query("select ProjectNumber from LOAN_PROJECT;")
    try:
        if request.method == 'POST' and request.values['ProjectNumber'] != '':
            get_query("select * from LOAN_PERIOD where ProjectNumber = {};".format(request.values['ProjectNumber']))
            return redirect(url_for('period_show', PROJECT=request.values['ProjectNumber']))
    except:
        pass
    
    return render_template(
                'period.html',
                projects=projects,
                show=False,
                edit=False
        )

##### Show Periods of the Project
@app.route('/period_show/<PROJECT>', methods=['GET', 'POST'])
def period_show(PROJECT):
    try:
        if request.method == 'POST' and request.values['ProjectNumber'] != '':
            get_query("select * from LOAN_PROJECT where ProjectNumber = {}".format(request.values['ProjectNumber']))
            return redirect(url_for('period_show', PROJECT=request.values['ProjectNumber']))
    except:
        pass
    
    max_repayment = get_query("select MAX(ExpectPrinciple),MAX(ExpectInterest) from LOAN_PERIOD where ProjectNumber = {};".format(PROJECT))[0]
    min_repayment = get_query("select MIN(ExpectPrinciple),MIN(ExpectInterest) from LOAN_PERIOD where ProjectNumber = {};".format(PROJECT))[0]
    avg_repayment = get_query("select AVG(ExpectPrinciple),AVG(ExpectInterest) from LOAN_PERIOD where ProjectNumber = {};".format(PROJECT))[0]
    projects = get_query("select ProjectNumber from LOAN_PROJECT;")
    table = get_query("select * from LOAN_PERIOD where ProjectNumber = {};".format(PROJECT))
    total_repayment = sum([(table[i][5]+table[i][6]) for i in range(len(table))])
    date = get_query("select StartDate from LOAN_PROJECT where ProjectNumber = {}".format(PROJECT))[0][0]
    return render_template(
            'period.html',
            projects=projects,
            show=True,
            columns=['案件編號','期數','繳款期限','繳款日期','應繳本金','應繳利息','已繳本金','已繳利息','繳費方式','備註'],
            project_number=PROJECT,
            project_date=date,
            total_repayment=total_repayment,
            table=table,
            max_repayment=max_repayment,
            min_repayment=min_repayment,
            avg_repayment=avg_repayment
    )

##### Edit Period
@app.route('/period_edit/<PROJECT>-<PERIOD>', methods=['GET', 'POST'])
def period_edit(PROJECT, PERIOD):
    if request.method == 'POST':
        # show the other project
        try:
            if request.values['ProjectNumber'] != '':
                get_query("select * from LOAN_PROJECT where ProjectNumber = {}".format(request.values['ProjectNumber']))
                return redirect(url_for('period_show', PROJECT=request.values['ProjectNumber']))
        except:
            pass

        # else: edit period
        edit_data('LOAN_PERIOD', [PROJECT, PERIOD], edit=True, pr_key=[PROJECT, PERIOD])
        return redirect(url_for('period_show', PROJECT=PROJECT))
    
    data = get_query("select RepaymentDate, GetPrinciple, GetInterest, RepaymentMethod, Remark from LOAN_PERIOD where ProjectNumber = {} AND PeriodNumber = {};".format(PROJECT, PERIOD))
    projects = get_query("select ProjectNumber from LOAN_PROJECT;")
    table = get_query("select * from LOAN_PERIOD where ProjectNumber = {};".format(PROJECT))
    total_repayment = sum([(table[i][5]+table[i][6]) for i in range(len(table))])
    date = get_query("select StartDate from LOAN_PROJECT where ProjectNumber = {}".format(PROJECT))[0][0]
    return render_template(
            'period.html',
            projects=projects,
            edit=True,
            show=True,
            columns=['案件編號','期數','繳款期限','繳款日期','應繳本金','應繳利息','已繳本金','已繳利息','繳費方式','備註'],
            project_number=PROJECT,
            project_date=date,
            total_repayment=total_repayment,
            table=table,
            data=data[0]
    )

############################################### Search ###############################################
##### Search Repayment Record
@app.route('/repayment_record', methods=['GET', 'POST'])
def repayment_record():
    try:
        if request.method == 'POST' and request.values['ID'] != '':
            project_number = get_query("""
                select COUNT(ProjectNumber) from LOAN_PROJECT
                where EXISTS
                (select * from DEBTER
                where ID='{}' and LOAN_PROJECT.DebterID=DEBTER.ID);
            """.format(request.values['ID']))[0][0]

            projects = get_query("""
                select ProjectNumber from LOAN_PROJECT
                where EXISTS
                (select * from DEBTER
                where ID='{}' and LOAN_PROJECT.DebterID=DEBTER.ID);
            """.format(request.values['ID']))

            inputs = []
            for [PROJECT] in projects:
                table = get_query("""
                    select DueDate, RepaymentDate, RepaymentMethod, GetPrinciple+GetInterest, ExpectPrinciple+ExpectInterest-(GetPrinciple+GetInterest)
                    from LOAN_PERIOD
                    where ProjectNumber = {} AND DueDate <= DATE(\'now\');
                """.format(PROJECT))
                date = get_query("select StartDate from LOAN_PROJECT where ProjectNumber = {}".format(PROJECT))[0][0]
                if len(table) != 0:
                    total_repayment = get_query('select SUM(GetPrinciple+GetInterest) from LOAN_PERIOD where ProjectNumber = {} AND DueDate <= DATE(\'now\')'.format(PROJECT))[0][0]
                    total_outstanding = get_query('select SUM(ExpectPrinciple+ExpectInterest)-SUM(GetPrinciple+GetInterest ) from LOAN_PERIOD where ProjectNumber = {} AND DueDate <= DATE(\'now\')'.format(PROJECT))[0][0]
                else:
                    total_repayment = 0
                    total_outstanding = 0

                inputs.append([PROJECT, table.copy(), date, total_repayment, total_outstanding])
        
        return render_template(
            'repayment_record.html',
            show=True,
            columns=['繳款期限','繳款日期', '繳款方式', '已繳款金額', '剩餘繳款金額'],
            inputs=inputs,
            project_number=project_number
        )
    
    except:
        pass
    return render_template(
                'repayment_record.html',
                show=False
        )

##### Search Project Record
@app.route('/project_record', methods=['GET', 'POST'])
def project_record():
    try:
        if request.method == 'POST' and request.values['ProjectNumber'] != '':
            # Project Detail
            project_detail = get_query("""
                select
                ProjectNumber, StartDate, Name, ResidenceAddress, MailingAddress, MobilePhoneNumber, TelPhoneNumber
                from
                (select ProjectNumber, StartDate, DebterID from LOAN_PROJECT where ProjectNumber in ({})),
                (select ID, Name, ResidenceAddress, MailingAddress, MobilePhoneNumber, TelPhoneNumber from DEBTER)
                where ID = DebterID;
            """.format(request.values['ProjectNumber']))
            
            period_detail = get_query("""
                select ProjectNumber, PeriodNumber, DueDate, ExpectPrinciple, ExpectInterest, ExpectPrinciple+ExpectInterest, RepaymentDate, GetPrinciple+GetInterest
                from
                (select ProjectNumber, PeriodNumber, DueDate, RepaymentDate, ExpectPrinciple, ExpectInterest, GetPrinciple, GetInterest from LOAN_PERIOD where ProjectNumber in ({}))
                where GetPrinciple+GetInterest > 0;
                """.format(request.values['ProjectNumber']))

            return render_template(
                    'project_record.html',
                    show=True,
                    tables=[
                        ['案件明細', project_detail, ['案件編號','開始日期','客戶姓名','戶籍地址','通訊地址','行動電話','家用電話']],
                        ['統計表', period_detail, ['案件編號','期數','應繳款日期','應繳本金','應繳利息','本期應繳金額','已繳款日期','已繳款金額']]
                    ],
                    date=datetime.date.today().strftime("%Y / %m / %d")
                )

    except:
        pass
    return render_template(
                'project_record.html',
                show=False
            )

##### Search by SQL Query
@app.route('/sql_search', methods=['GET', 'POST'])
def sql_search():
    if request.method == 'POST' and request.values['query'] != '':
        try:
            table, cols = get_query(request.values['query'], get_col=True)
            return render_template('sql_search.html', table=table, columns=cols)
        except Exception as e:
            return render_template('sql_search.html', error=True, msg=e)

    return render_template('sql_search.html')

##### Add, Edit and Delete by SQL Query
@app.route('/sql_edit', methods=['GET', 'POST'])
def sql_edit():
    if request.method == 'POST' and request.values['query'] != '':
        try:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(request.values['query'])
            conn.commit()
            conn.close()
            return render_template('sql_edit.html', success=True)
        except Exception as e:
            return render_template('sql_edit.html', error=True, msg=e)

    return render_template('sql_edit.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
