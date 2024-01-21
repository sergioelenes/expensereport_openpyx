from flask import Flask, render_template, request, redirect, url_for, flash
from flask_basicauth import BasicAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
import pandas as pd

app = Flask(__name__)
app.secret_key = "Macarenas"
basic_auth = BasicAuth(app)
app.config['BASIC_AUTH_USERNAME'] = 'brad'
app.config['BASIC_AUTH_PASSWORD'] = 'keonda'
basic_auth = BasicAuth(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)

class Concept(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    concept = db.Column(db.String(50), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(200), nullable=False)

def create_default_concepts():
    default_concepts = ['Auto fuel', 'Auto maint', 'Auto insur', 'Bella maint', 'Bella supplies', 'Dining', 'Fideicomisario',
                        'Gifts', 'Groceries', 'Hoa', 'Home repair', 'Household', 'Medical', 'Personal', 'Phone',
                        'Property management', 'Recreation', 'Rv parking', 'Storage', 'Taxes', 'Travel', 'Utilities',
                        'Zoey', 'Misc.']

    for concept_name in default_concepts:
        concept = Concept(name=concept_name)
        db.session.add(concept)

    db.session.commit()

with app.app_context():
    db.create_all()
    existing_concepts = Concept.query.all()
    if not existing_concepts:
        create_default_concepts()

@app.route("/", methods=['GET','POST'])
@basic_auth.required
def loginroute():
    concepts = Concept.query.order_by(func.lower(Concept.name)).all()
    return render_template('index.html', concepts=concepts)

@app.route("/datain", methods=['POST'])
def datain():
    if request.method == 'POST':
        month = request.form['month']
        if month == 'Month Select':
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
        year = 2024
        notes = request.form['notes']

        new_expense = Expense(concept=concept, month=month, year=year, amount=amount, notes=notes)
        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for('loginroute'))

@app.route("/reports", methods=['GET','POST'])
@basic_auth.required
def reports():
    return render_template('reports.html')

@app.route("/all_expenses", methods=['GET'])
@basic_auth.required
def all_expenses():
    month_order = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    expenses = Expense.query.order_by(case(month_order, value=Expense.month)).all()
    return render_template('all_expenses.html', expenses=expenses)

#agregar conceptos
@app.route("/add_concept", methods=['POST'])
@basic_auth.required
def add_concept():
    if request.method == 'POST':
        new_concept_name = request.form['newconcept']

        # Verifica si el concepto ya existe
        existing_concept = Concept.query.filter_by(name=new_concept_name).first()
        if existing_concept:
            flash('Concept already exists', 'danger')
        else:
            new_concept = Concept(name=new_concept_name)
            db.session.add(new_concept)
            db.session.commit()
            flash(f'Concept "{new_concept_name}" added successfully', 'success')

    return redirect(url_for('loginroute'))

#borrar entradas
@app.route("/delete_expense/<int:id>", methods=['POST'])
@basic_auth.required
def delete_expense(id):
    expense_to_delete = Expense.query.get_or_404(id)
    db.session.delete(expense_to_delete)
    db.session.commit()
    return redirect(url_for('all_expenses'))

#borrar conceptos
@app.route("/deleteconcept", methods=['POST'])
@basic_auth.required
def delete_concept():
    concept_name = request.form['deleteconcept']

    # Busca el concepto en la base de datos
    concept_to_delete = Concept.query.filter_by(name=concept_name).first()

    if concept_to_delete:
        # Elimina el concepto de la base de datos
        db.session.delete(concept_to_delete)
        db.session.commit()
        flash(f'Concept "{concept_name}" deleted successfully', 'success')
    else:
        flash(f'Concept "{concept_name}" not found', 'danger')
    
    return redirect(url_for('loginroute'))



# Tabla Anual
@app.route("/year_resume")
@basic_auth.required
def year_resume():
    expenses = Expense.query.all()

    # Crear un DataFrame de pandas con los datos de los gastos
    df = pd.DataFrame([(e.concept, e.month, e.year, e.amount, e.notes) for e in expenses],
                      columns=['concept', 'month', 'year', 'amount', 'notes'])
  

    
    # Crear la tabla pivote con todos los meses y conceptos
    pivot = df.pivot_table(values='amount', index='concept', columns='month', aggfunc='sum', fill_value=0, margins=True, margins_name='Sum')

    return render_template('year_resume.html', tables=[pivot.to_html(classes="table table-striped table-hover")], titles=[''])






if __name__ == '__main__':
    app.run(debug=True)


'''
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
        return send_file(alldata, as_attachment=True)'''