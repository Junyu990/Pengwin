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

    employees = []
    for doc in docs:
        employee_data = doc.to_dict()
        employee_data['employee_id'] = doc.id  # Add the unique ID to the employee data
        employees.append(employee_data)
        
    return render_template('employee_list.html', employees=employees)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        job_title = request.form['job_title']
        prefix = ''.join([word[0].upper() for word in job_title.split()])  # Create prefix from job title
        unique_id = generate_unique_id(prefix)
        
        name = request.form['name']
        
        date_of_birth = request.form['date_of_birth']
        password = generate_password(name, date_of_birth)
        
        employee_data = {
            'password': password,
            'name': name,
            'phone_number': request.form['phone_number'],
            'email': request.form['email'],
            'address': request.form['address'],
            'wallet_address': request.form['wallet_address'],
            'salary': float(request.form['salary']),
            'date_of_birth': date.fromisoformat(date_of_birth).isoformat(),
            'citizenship': request.form['citizenship'],
            'employment_start_date': date.fromisoformat(request.form['employment_start_date']).isoformat(),
            'job_title': job_title,
            'branch': request.form['branch']
        }

        print("Collected employee data:", json.dumps(employee_data, indent=2))  # Debug statement
        
        # Collect leave data from form
        leave_data = {
            'Annual Leave': {'allowed': int(request.form['annual_leave_allowed']), 'taken': 0},
            'Unpaid Leave': {'allowed': int(request.form['unpaid_leave_allowed']), 'taken': 0},
            'Compassionate Leave': {'allowed': int(request.form['compassionate_leave_allowed']), 'taken': 0},
            'Medical Leave': {'allowed': int(request.form['medical_leave_allowed']), 'taken': 0}
        }

        # Add employee data to Firestore
        try:
            doc_ref = db.collection('employees').document(unique_id)  # Use the generated ID
            doc_ref.set(employee_data)
            print("Employee added to Firestore successfully")  # Debug statement
            for leave_type, data in leave_data.items():
                doc_ref.collection('leaves').document(leave_type).set(data)
            print("Employee and leave data added to Firestore successfully")  # Debug statement
        except Exception as e:
            print("Error adding employee to Firestore:", e)  # Debug statement

        return redirect(url_for('employee_list'))
    return render_template('add_employee.html')

def generate_password(name, date_of_birth):
    first_initial = name[0].upper()  # Take the first name and convert to lower case
    birth_date_obj = datetime.strptime(date_of_birth, '%Y-%m-%d')
    birth_date_formatted = birth_date_obj.strftime('%d%m%y')  # Format birthdate as ddmmyy
    return f"{first_initial}{birth_date_formatted}"

def generate_unique_id(prefix):
    employees_ref = db.collection('employees')
    existing_ids = [doc.id for doc in employees_ref.stream()]
    
    for num in range(1, 1000):
        new_id = f"{prefix}{num:03d}"
        if new_id not in existing_ids:
            return new_id
    raise ValueError("Unable to generate a unique ID")


@app.route('/employee/delete/<string:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee_ref = db.collection('employees').document(employee_id)
    
    try:
        # Delete employee document
        employee_ref.delete()
        print(f"Employee with ID {employee_id} deleted successfully")  # Debug statement
        
        # Delete leave data associated with the employee
        leave_ref = employee_ref.collection('leaves')
        leave_docs = leave_ref.stream()
        for doc in leave_docs:
            doc.reference.delete()
        
        print(f"Leave data for employee with ID {employee_id} deleted successfully")  # Debug statement
        
    except Exception as e:
        print(f"Error deleting employee with ID {employee_id}: {e}")  # Debug statement
    
    return redirect(url_for('employee_list'))

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/payroll-summary')
def payroll_summary():
    return render_template('payroll_summary.html')


@app.route('/pending-salaries')
def pending_salaries():
    pending_salaries_ref = db.collection('employees')
    docs = pending_salaries_ref.stream()

    pending_salaries = []
    for doc in docs:
        salary_data = doc.to_dict()
        salary_data['id'] = doc.id
        pending_salaries.append(salary_data)
    
    return render_template('pending_salaries.html', pending_salaries=pending_salaries)

@app.route('/tax-authorisation')
def tax_authorisation():
    return render_template('tax_authorisation.html')

@app.route('/manage-pensions')
def manage_pensions():
    return render_template('manage_pensions.html')

@app.route('/leaves')


@app.route('/leaves', methods=['GET'])
def view_all_leaves():
    employees_ref = db.collection("employees")
    employees = employees_ref.stream()
    
    all_leaves = []
    
    for employee in employees:
        employee_data = employee.to_dict()
        employee_id = employee.id
        leave_ref = employees_ref.document(employee_id).collection('leaves')
        leaves = {doc.id: doc.to_dict() for doc in leave_ref.stream()}
        all_leaves.append({'id': employee_id, 'name': employee_data['name'], 'leaves': leaves})
    
    return render_template('view_all_leaves.html', all_leaves=all_leaves)

@app.route('/pending_leave_requests')
def pending_leave_requests():
    leave_requests_ref = db.collection_group('leave_requests')
    leave_requests = [doc.to_dict() for doc in leave_requests_ref.stream()]
    
    # Update each leave request with employee name and days requested
    for request in leave_requests:
        if 'employee_id' in request:
            employee_ref = db.collection('employees').document(request['employee_id'])
            employee_data = employee_ref.get().to_dict()
            if employee_data is not None:
                request['name'] = employee_data['name']
                start_date = datetime.strptime(request['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(request['end_date'], '%Y-%m-%d')
                request['days_requested'] = (end_date - start_date).days + 1
            else:
                # Handle case where employee data is not found
                request['name'] = 'Unknown'
                request['days_requested'] = 'Unknown'
        
    return render_template('pending_leave_requests.html', leave_requests=leave_requests)


def approve_leave_request(employee_id, request_id):
    try:
        # Get the employee document reference
        employee_ref = db.collection('employees').document(employee_id)
        employee_data = employee_ref.get().to_dict()

        # Get the leave request document reference
        leave_request_ref = employee_ref.collection('leave_requests').document(request_id)
        leave_request_data = leave_request_ref.get().to_dict()

        if employee_data and leave_request_data:
            # Update leave status to 'Approved'
            leave_request_ref.update({'status': 'Approved'})
            return True
        else:
            print("Employee or leave request not found.")
            return False
    except Exception as e:
        print(f"Error approving leave request: {e}")
        return False

# Usage example
employee_id = 'your_employee_id'
request_id = 'your_request_id'
approve_leave_request(employee_id, request_id)

@app.route('/reject_leave/<string:request_id>')
def reject_leave(request_id):
    try:
        leave_request_ref = db.collection('employees').document(request_id.split('_')[0]).collection('leave_requests').document(request_id)
        leave_request_ref.update({'status': 'Rejected'})
        return redirect(url_for('pending_leave_requests'))
    except Exception as e:
        print(f"Error rejecting leave request: {e}")
        return redirect(url_for('pending_leave_requests'))


@app.route('/leave/overview')
def leave_overview():
    return render_template('leave_overview.html')


@app.route('/request_leave', methods=['GET', 'POST'])
def request_leave():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']
        
        # Calculate number of days
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        num_days = (end_date_obj - start_date_obj).days + 1  # Add 1 to include the end date
        
        # Get employee name
        employee_ref = db.collection('employees').document(employee_id)
        employee_data = employee_ref.get().to_dict()
        employee_name = employee_data['name']
        
        # Get current date and time as submission date
        submission_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        leave_data = {
            'employee_id': employee_id,
            'name': employee_name,
            'leave_type': leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason,
            'status': 'Pending',
            'num_days': num_days,
            'submission_date': submission_date
        }
        
        try:
            db.collection('employees').document(employee_id).collection('leave_requests').add(leave_data)
            return redirect(url_for('view_all_leaves'))
        except Exception as e:
            print(f"Error adding leave request: {e}")
    
    employees_ref = db.collection("employees")
    employees = employees_ref.stream()
    employee_data = [{'id': employee.id, 'name': employee.to_dict()['name']} for employee in employees]
    
    return render_template('request_leave.html', employees=employee_data)




if __name__ == '__main__':
    app.run(debug=True)
