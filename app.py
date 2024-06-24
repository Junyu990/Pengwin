from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date
from datetime import datetime
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
    employee_ref = db.collection("employees")
    docs = employee_ref.stream()

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
        
        
        # Leave data initialization
        leave_data = {
            'Annual Leave': {'allowed': 14, 'taken': 0},
            'Unpaid Leave': {'allowed': 14, 'taken': 0},
            'Compassionate Leave': {'allowed': 14, 'taken': 0},
            'Medical Leave': {'allowed': 14, 'taken': 0}
        }
        

        # Add employee data to Firestore
        try:
            doc_ref = db.collection('employees').document(request.form['name']) # change to add username into document !!!!!!!!!!!
            doc_ref.set(employee_data) # !!!!!!!!!!!!!!!
            print("Employee added to Firestore successfully")  # Debug statement
            for leave_type, data in leave_data.items():
                doc_ref.collection('leaves').document(leave_type).set(data)
            print("Employee and leave data added to Firestore successfully")  # Debug statement
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

@app.route('/overview')
def overview():
    return render_template('overview.html')



# Static data to simulate pending salaries
pending_salaries_data = [
    {
        'id': 1,
        'name': 'John Doe',
        'request_date': '2024-06-01',
        'location': 'New York',
        'status': 'Pending',
        'salary': 5000,
        'total_paid_this_year': 30000
    },
    {
        'id': 2,
        'name': 'Jane Smith',
        'request_date': '2024-06-02',
        'location': 'Los Angeles',
        'status': 'Pending',
        'salary': 6000,
        'total_paid_this_year': 35000
    },
    {
        'id': 3,
        'name': 'Michael Johnson',
        'request_date': '2024-06-03',
        'location': 'Chicago',
        'status': 'Pending',
        'salary': 5500,
        'total_paid_this_year': 32000
    },
    {
        'id': 4,
        'name': 'Michael Johnson',
        'request_date': '2024-06-03',
        'location': 'Chicago',
        'status': 'Pending',
        'salary': 5500,
        'total_paid_this_year': 32000
    }
]

@app.route('/pending-salaries')
def pending_salaries():
    return render_template('pending_salaries.html', pending_salaries=pending_salaries_data)



@app.route('/tax-authorisation')
def tax_authorisation():
    return render_template('tax_authorisation.html')

@app.route('/manage-pensions')
def manage_pensions():
    return render_template('manage_pensions.html')

@app.route('/leaves')


def view_all_leaves():
    employees_ref = db.collection("employees")
    employees = employees_ref.stream()
    
    all_leaves = []
    
    for employee in employees:
        employee_data = employee.to_dict()
        employee_id = employee.id
        leave_ref = employees_ref.document(employee_id).collection('leaves')
        leaves = {doc.id: doc.to_dict() for doc in leave_ref.stream()}
        all_leaves.append({'name': employee_data['name'], 'leaves': leaves})
    
    return render_template('view_all_leaves.html', all_leaves=all_leaves)


@app.route('/leave/overview')
def leave_overview():
    return render_template('leave_overview.html')


@app.route('/leave/pending', methods=['GET', 'POST'])
def pending_leave_request():
    if request.method == 'POST':
        name = request.form['name']
        leave_type = request.form['leave_type']
        start_date = date.fromisoformat(request.form['start_date'])
        end_date = date.fromisoformat(request.form['end_date'])
        reason = request.form['reason']
        file = request.files['file']

        days_requested = (end_date - start_date).days + 1

        # Fetch employee leave data
        employee_ref = db.collection('employees').document(name)
        leave_ref = employee_ref.collection('leaves').document(leave_type)
        leave_data = leave_ref.get().to_dict()

        if leave_data['allowed'] < days_requested:
            return "Leave request exceeds allowed leave days", 400

        # Save leave request to Firestore
        leave_request_data = {
            'name': name,
            'leave_type': leave_type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'reason': reason,
            'status': 'Pending',
            'days_requested': days_requested
        }
        db.collection('leave_requests').add(leave_request_data)

        return redirect(url_for('pending_leave_request'))

    # Fetch pending leave requests
    leave_requests_ref = db.collection('leave_requests').where('status', '==', 'Pending')
    leave_requests = [{'id': doc.id, **doc.to_dict()} for doc in leave_requests_ref.stream()]

    return render_template('pending_leave_request.html', pending_requests=leave_requests)

from datetime import datetime

@app.route('/submit_leave_request', methods=['POST'])
def submit_leave_request():
    name = request.form['name']
    leave_type = request.form['leave_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    reason = request.form['reason']
    file = request.files['file'] if 'file' in request.files else None

    # Calculate days_requested
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    days_requested = (end_date_obj - start_date_obj).days + 1  # Include end date

    leave_data = {
        'name': name,
        'leave_type': leave_type,
        'start_date': start_date,
        'end_date': end_date,
        'reason': reason,
        'days_requested': days_requested,  # Add this line
        'status': 'Pending'
    }

    if file:
        # Optionally save the file to Firebase storage or a location
        leave_data['file_name'] = file.filename

    db.collection('leave_requests').add(leave_data)
    return redirect(url_for('pending_leave_request'))

@app.route('/approve_leave_request/<request_id>', methods=['POST'])
def approve_leave_request(request_id):
    leave_request_ref = db.collection('leave_requests').document(request_id)
    leave_request_ref.update({'status': 'Approved'})
    return redirect(url_for('pending_leave_request'))

@app.route('/reject_leave_request/<request_id>', methods=['POST'])
def reject_leave_request(request_id):
    leave_request_ref = db.collection('leave_requests').document(request_id)
    leave_request_ref.update({'status': 'Rejected'})
    return redirect(url_for('pending_leave_request'))

if __name__ == '__main__':
    app.run(debug=True)
