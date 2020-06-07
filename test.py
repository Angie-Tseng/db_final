from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/new_debter')
def new_debter():
    return render_template('new_debter.html')

@app.route('/sql', methods=['GET', 'POST'])
def sql_query():
    if request.method == 'POST' and request.values['query'] != '':
        return render_template('sql.html', query_result=request.values['query'])

    return render_template('sql.html')



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.values['username'] != '':
            return 'Hello ' + request.values['username'] + '\n' + render_template('test.html')
    return render_template('test.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
