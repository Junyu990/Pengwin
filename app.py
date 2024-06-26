from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, datetime
import json
import re
import os



from CountryPayroll import *



app = Flask(__name__)

app.secret_key = 'your_secret_key'
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
        if not name.isalpha():
            flash("Name must only contain alphabetic characters.", "danger")
            return redirect(url_for('add_employee'))
        
        phone_number = request.form['phone_number']
        if not phone_number.isdigit() or len(phone_number) > 18:
            flash("Phone number must only contain up to 18 digits.", "danger")
            return redirect(url_for('add_employee'))
        
        email = request.form['email']
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for('add_employee'))
        
        salary = request.form['salary']
        if not re.match(r'^\d+(\.\d{1,2})?$', salary):
            flash("Salary must be a valid number (up to 2 decimal places).", "danger")
            return redirect(url_for('add_employee'))
        
        date_of_birth = request.form['date_of_birth']
        if not validate_date_of_birth(date_of_birth):
            flash("Date of birth must be before the current date.", "danger")
            return redirect(url_for('add_employee'))
        
        
        password = generate_password(name, date_of_birth)
        
        
        employee_data = {
            'password': password,
            'name': name,
            'phone_number': phone_number,
            'email': email,
            'address': request.form['address'],
            'wallet_address': request.form['wallet_address'],
            'salary': salary,
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

def validate_date_of_birth(date_of_birth):
    try:
        birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        return birth_date < date.today()
    except ValueError:
        return False

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

@app.route('/calculate_payroll', methods=['POST'])
def calculate_payroll():
    try:
        data = request.json
        gross_salary = data['gross_salary']
        location = data['location']

        if location == 'South Korea':
            wallet_address = "0x7f3bEF0bF9DE7545e3A686674834716f8379aB3A"
            payroll = SouthKoreaPayroll(gross_salary, wallet_address)
        elif location == 'Singapore':
            wallet_address = "0x9091700FCfD4D0120d66Ad5a1638738A885CA813"
            payroll = SingaporePayroll(gross_salary, wallet_address)
        else:
            return jsonify({"error": "Invalid location"}), 400

        payroll_data = payroll.get_salary_breakdown()
        payroll_data["Country Wallet Address"] = wallet_address

        return jsonify(payroll_data)
    except Exception as e:
        print(f"Error calculating payroll: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/validate-auth-key', methods=['POST'])
def validate_auth_key():
    data = request.get_json()
    auth_key = data.get('authKey')
    
    # Replace 'your_actual_auth_key' with the actual authorization key
    if auth_key == '123456':
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/tax-transfers')
def tax_transfers():
    try:
        tax_transfers_ref = db.collection('taxtransfers')
        countries = tax_transfers_ref.stream()
        
        print("Tax Transfers Reference:", tax_transfers_ref)
        
        tax_dict = []
        for country_doc in countries:
            country_id = country_doc.id
            print(f"Country ID: {country_id}")  # Debugging statement
            
            employees_ref = country_doc.reference.collection('employees').stream()
            employees_found = False
            
            for employee_doc in employees_ref:
                employees_found = True
                print(f"Employee ID: {employee_doc.id}")  # Debugging statement
                tax_transfer_data = employee_doc.to_dict()
                tax_transfer_data['country'] = country_id
                tax_transfer_data['employee_id'] = employee_doc.id
                
                # Calculate total tax based on country
                if country_id == 'South Korea':
                    total_tax = (
                        tax_transfer_data.get('income_tax', 0) +
                        tax_transfer_data.get('local_income_tax', 0) +
                        tax_transfer_data.get('social_security_contribution', 0)
                    )
                elif country_id == 'Singapore':
                    total_tax = (
                        tax_transfer_data.get('income_tax', 0) +
                        tax_transfer_data.get('cpf_contribution', 0)
                    )
                else:
                    # Default calculation if country is not specifically handled
                    total_tax = (

                    )
                
                tax_transfer_data['total_tax'] = total_tax
                
                tax_dict.append(tax_transfer_data)
            
            if not employees_found:
                print(f"No employees found for country {country_id}")
        
        if not tax_dict:
            print("No tax transfers found.")
        
        print(f"Tax Transfers: {tax_dict}")  # Debugging statement to print data to console
        return render_template('tax_transfers.html', tax_dict=tax_dict)
    except Exception as e:
        print("Error retrieving tax transfers:", e)
        return render_template('tax_transfers.html', tax_dict=[])

    
@app.route('/record_tax_transfer', methods=['POST'])
def record_tax_transfer():
    try:
        data = request.json
        print("Received data:", data)  # Add logging to debug the received data
        
        employee_id = data['employee_id']
        tax_amount_klay = data['tax_amount_klay']
        tax_amount_usd = data['tax_amount_usd']
        timestamp = data['timestamp']
        country = data['country']
        month = data['month']  # Get the month from the request
        country_name = data['country']  # Get the country name from the request
        year = data['year']

        tax_transfer_data = {
            'tax_amount_klay': tax_amount_klay,
            'tax_amount_usd': tax_amount_usd,
            'timestamp': timestamp,
            'country_name': country_name,  # Add country name to tax transfer data
            'month': month,  # Add month to tax transfer data
            'year': year
        }

        # Add country-specific tax details
        if country == 'South Korea':
            tax_transfer_data['income_tax'] = data.get('income_tax', 0)
            tax_transfer_data['local_income_tax'] = data.get('local_income_tax', 0)
            tax_transfer_data['social_security_contribution'] = data.get('social_security_contribution', 0)
        elif country == 'Singapore':
            tax_transfer_data['income_tax'] = data.get('income_tax', 0)
            tax_transfer_data['cpf_contribution'] = data.get('cpf_contribution', 0)

        # Create a document ID that includes the employee ID and month
        document_id = f"{employee_id}_{month}_{year}"

        # Record the tax transfer in Firebase
        db.collection('taxtransfers').document(country).collection('employees').document(document_id).set(tax_transfer_data)

        # Update the country document with the country name if it doesn't exist
        country_doc_ref = db.collection('taxtransfers').document(country)
        country_doc = country_doc_ref.get()
        if not country_doc.exists:
            country_doc_ref.set({'country_name': country_name})

        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error recording tax transfer: {e}")
        import traceback
        traceback.print_exc()  # Print the traceback for debugging
        return jsonify({'error': str(e)}), 500
    
    

@app.route('/manage-pensions')
def manage_pensions():
    return render_template('manage_pensions.html')





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
    try:
        leave_requests = Leave.get_pending_requests()
        return render_template('pending_leave_requests.html', leave_requests=leave_requests)
    except Exception as e:
        print(f"Error in /pending_leave_requests: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/approve_leave/<string:leave_id>', methods=['POST'])
def approve_leave(leave_id):
    try:
        leave_request = Leave.get(leave_id)
        if leave_request:
            leave_request.approve()
        return redirect(url_for('pending_leave_requests'))
    except Exception as e:
        print(f"Error approving leave request: {e}")
        return redirect(url_for('pending_leave_requests'))

@app.route('/reject_leave/<string:leave_id>', methods=['POST'])
def reject_leave(leave_id):
    try:
        leave_request = Leave.get(leave_id)
        if leave_request:
            leave_request.reject()
        return redirect(url_for('pending_leave_requests'))
    except Exception as e:
        print(f"Error rejecting leave request: {e}")
        return redirect(url_for('pending_leave_requests'))

@app.route('/request_leave', methods=['GET', 'POST'])
def request_leave():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']
        file = None

        # Handle file upload for Medical Leave
        if leave_type == 'Medical Leave' and 'file' in request.files:
            file = request.files['file']
            if file:
                # Save the file to a desired location, e.g., 'uploads' directory
                file_path = f"uploads/{file.filename}"
                file.save(file_path)
                file = file_path  # Update the file path to be saved in the database

        leave_request = Leave(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            file=file
        )
        leave_request.save()

        return redirect(url_for('view_all_leaves'))

    employees_ref = db.collection("employees")
    employees = [{'id': employee.id, 'name': employee.to_dict()['name']} for employee in employees_ref.stream()]

    return render_template('request_leave.html', employees=employees)

@app.route('/leave_overview')
def leave_overview():
    return render_template('leave_overview.html')

class Leave:
    def __init__(self, employee_id, leave_type, start_date, end_date, reason, file=None, leave_id=None):
        self.employee_id = employee_id
        self.leave_type = leave_type
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.file = file
        self.leave_id = leave_id or self.generate_leave_id()
        self.status = 'Pending'
        self.submission_date = datetime.now().isoformat()

    def generate_leave_id(self):
        leave_requests_ref = db.collection('employees').document(self.employee_id).collection('leave_requests')
        existing_ids = [doc.id for doc in leave_requests_ref.stream()]
        for num in range(1, 1000):
            new_id = f"{self.employee_id}_{datetime.now().strftime('%Y%m%d')}_{num:03d}"
            if new_id not in existing_ids:
                return new_id
        raise ValueError("Unable to generate a unique leave ID")

    def save(self):
        request_data = {
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'reason': self.reason,
            'status': self.status,
            'submission_date': self.submission_date,
            'file': self.file
        }
        db.collection('employees').document(self.employee_id).collection('leave_requests').document(self.leave_id).set(request_data)

    @classmethod
    def get(cls, leave_id):
        employee_id, date_str, num = leave_id.split('_')
        doc = db.collection('employees').document(employee_id).collection('leave_requests').document(leave_id).get()
        if doc.exists:
            data = doc.to_dict()
            return cls(
                employee_id=data['employee_id'],
                leave_type=data['leave_type'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                reason=data['reason'],
                status=data['status'],
                submission_date=data['submission_date'],
                leave_id=doc.id,
                file=data.get('file')
            )
        else:
            return None

    def approve(self):
        self.status = 'Approved'
        self.save()

    def reject(self):
        self.status = 'Rejected'
        self.save()

    def delete(self):
        db.collection('employees').document(self.employee_id).collection('leave_requests').document(self.leave_id).delete()

    @classmethod
    def get_pending_requests(cls):
        leave_requests_ref = db.collection_group('leave_requests').where('status', '==', 'Pending')
        leave_requests = []
        for doc in leave_requests_ref.stream():
            request = doc.to_dict()
            request['leave_id'] = doc.id
            leave_requests.append(request)
        return leave_requests