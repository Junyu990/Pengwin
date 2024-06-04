from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from datetime import date

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'pengwinDB',
    'host': 'mongodb+srv://junyu:YT@Preo150404@pengwincluster.h853ma2.mongodb.net/?retryWrites=true&w=majority&appName=PengwinCluster',
    'retryWrites': True,
    'w': 'majority'
}
app.static_folder = 'static'

db = MongoEngine()
db.init_app(app)

class Employee(db.Document):
    password = db.StringField(required=True)
    name = db.StringField(required=True, max_length=120)
    phone_number = db.StringField(required=True, max_length=20)
    email = db.EmailField(required=True, unique=True)
    address = db.StringField(required=True, max_length=200)
    wallet_address = db.StringField(required=True, max_length=200)
    salary = db.FloatField(required=True)
    date_of_birth = db.DateField(required=True)
    citizenship = db.StringField(required=True, max_length=100)
    employment_start_date = db.DateField(required=True)
    job_title = db.StringField(required=True, max_length=100)
    branch = db.StringField(required=True, max_length=100)

    def __repr__(self):
        return f"<Employee {self.name}>"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employee_list():
    employees = Employee.objects.all()
    return render_template('employee_list.html', employees=employees)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        employee_data = Employee(
            password=request.form['password'],
            name=request.form['name'],
            phone_number=request.form['phone_number'],
            email=request.form['email'],
            address=request.form['address'],
            wallet_address=request.form['wallet_address'],
            salary=float(request.form['salary']),
            date_of_birth=date.fromisoformat(request.form['date_of_birth']),
            citizenship=request.form['citizenship'],
            employment_start_date=date.fromisoformat(request.form['employment_start_date']),
            job_title=request.form['job_title'],
            branch=request.form['branch']
        )
        employee_data.save()
        return redirect(url_for('employee_list'))
    return render_template('add_employee.html')

@app.route('/employee/delete/<string:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee = Employee.objects.get_or_404(id=employee_id)
    employee.delete()
    return redirect(url_for('employee_list'))

if __name__ == '__main__':
    app.run(debug=True)