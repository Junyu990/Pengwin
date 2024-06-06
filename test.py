from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date
import json

app = Flask(__name__)
app.static_folder = 'static'

# Firebase initialization
cred = credentials.Certificate("pengwin-d7fcd-firebase-adminsdk-dc2pi-34b51f5929.json")  # Adjust the path as necessary
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employees')
def employee_list():
    employees_ref = db.collection('employees')
    docs = employees_ref.stream()
    employees = [doc.to_dict() for doc in docs]
    return render_template('employee_list.html', employees=employees)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        employee_data = {
            'password': request.form['password'],
            'name': request.form['name'],
            'phone_number': request.form['phone_number'],
            'email': request.form['email'],
            'address': request.form['address'],
            'wallet_address': request.form['wallet_address'],
            'salary': float(request.form['salary']),
            'date_of_birth': date.fromisoformat(request.form['date_of_birth']).isoformat(),
            'citizenship': request.form['citizenship'],
            'employment_start_date': date.fromisoformat(request.form['employment_start_date']).isoformat(),
            'job_title': request.form['job_title'],
            'branch': request.form['branch']
        }

        print("Collected employee data:", json.dumps(employee_data, indent=2))  # Debug statement

        # Add employee data to Firestore
        try:
            doc_ref = db.collection('employees').document("name") # change to add username into document !!!!!!!!!!!
            doc_ref.set(employee_data) # !!!!!!!!!!!!!!!
            print("Employee added to Firestore successfully")  # Debug statement
        except Exception as e:
            print("Error adding employee to Firestore:", e)  # Debug statement

        return redirect(url_for('employee_list'))
    return render_template('add_employee.html')

@app.route('/employee/delete/<string:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee_ref = db.collection('employees').document(employee_id)
    try:
        employee_ref.delete()
        print(f"Employee with ID {employee_id} deleted successfully")  # Debug statement
    except Exception as e:
        print(f"Error deleting employee with ID {employee_id}:", e)  # Debug statement
    return redirect(url_for('employee_list'))

if __name__ == '__main__':
    app.run(debug=True)
