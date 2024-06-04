from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.static_folder = 'static'

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    wallet_address = db.Column(db.String(200), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    citizenship = db.Column(db.String(100), nullable=False)
    employment_start_date = db.Column(db.Date, nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Employee {self.name}>"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employee_list():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        password = request.form['password']
        name = request.form['name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        address = request.form['address']
        wallet_address = request.form['wallet_address']
        salary = float(request.form['salary'])
        date_of_birth = date.fromisoformat(request.form['date_of_birth'])
        citizenship = request.form['citizenship']
        employment_start_date = date.fromisoformat(request.form['employment_start_date'])
        job_title = request.form['job_title']
        branch = request.form['branch']

        new_employee = Employee(
            password=password, name=name, phone_number=phone_number, email=email, address=address, wallet_address=wallet_address,
            salary=salary, date_of_birth=date_of_birth, citizenship=citizenship, employment_start_date=employment_start_date,
            job_title=job_title, branch=branch
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('employee_list'))
    return render_template('add_employee.html')

@app.route('/employee/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for('employee_list'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



#test2
#test3
