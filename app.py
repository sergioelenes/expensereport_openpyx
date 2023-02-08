from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_basicauth import BasicAuth
import openpyxl
import pandas as pd


app = Flask(__name__)
app.secret_key = "Macarenas"
basic_auth = BasicAuth(app)
app.config['BASIC_AUTH_USERNAME'] = 'brad'
app.config['BASIC_AUTH_PASSWORD'] = 'keonda'
basic_auth = BasicAuth(app)



def datainput(month, concept, amount, notes):
    book = openpyxl.load_workbook('expensedb.xlsx')
    detailsheet = book['detail']
    detailsheet.append([month,concept,float(amount),notes])
    book.save('expensedb.xlsx')


@app.route("/", methods=['GET','POST'])
@basic_auth.required
def loginroute():
        return render_template('index.html')



@app.route("/datain", methods=['POST'])
def datain():
    if request.method == 'POST':
        month = request.form['month']
        if month=='Month Select':
                flash('information incomplete, please try again')
                return render_template('index.html')
        concept = request.form['concept']
        if concept == 'Expense Concept':
                flash('information incomplete, please try again')
                return render_template('index.html')                
        amount = request.form['amount']
        if amount == "":
                flash('information incomplete, please try again')
                return render_template('index.html')
        notes = request.form['notes']

        datainput(month, concept, amount, notes)
        return render_template('index.html')
    

@app.route("/reports", methods=['GET','POST'])
@basic_auth.required
def reports():
        book = openpyxl.load_workbook('expensedb.xlsx')
        book.save('expensedb.xlsx')
        return render_template('reports.html')

@app.route("/year", methods=['GET','POST'])
@basic_auth.required
def year():
        try:
                df = pd.read_excel('expensedb.xlsx', sheet_name='detail')
                pivot = df.pivot_table(values='Amount', index='Concept', columns='Month', aggfunc='sum', fill_value="-", margins=True, margins_name='Total')
                #pivott = pivot.style.format({"Amount":"{:,d}"})
                return render_template('reports.html', tables=[pivot.to_html()], titles=[''] )
        except ValueError:
                return render_template('reports.html')


@app.route("/bymonth", methods=['GET','POST'])
@basic_auth.required
def bymonth():
        if request.method == 'POST':
                mess = request.form['elmess']
                dflogstotal = pd.read_excel('expensedb.xlsx', sheet_name='detail', index_col=1)
                dflogstotal2 = dflogstotal.fillna(" ")
                pormes = dflogstotal2[(dflogstotal['Month']==mess)]
                return render_template('reports.html', tables=[pormes.to_html()], titles=[''] )

@app.route("/data", methods=['GET','POST'])
@basic_auth.required
def data():
        dflogstotal = pd.read_excel('expensedb.xlsx', sheet_name='detail')
        dflogstotal2 = dflogstotal.fillna(" ")
        return render_template('reports.html', tables=[dflogstotal2.to_html()], titles=[''] )

@app.route('/downloadxls')
@basic_auth.required
def downloadxls ():
        alldata = "expensedb.xlsx"
        return send_file(alldata, as_attachment=True)

if __name__=='__main__':
    app.run(debug=True)