from datetime import date

class Employee:
    def __init__(self, employee_id, password, name, phone_number, email, address, wallet_address, salary, date_of_birth, citizenship, employment_start_date, job_title, branch):
        self.employee_id = employee_id                # PK
        self.password = password
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.address = address
        self.wallet_address = wallet_address
        self.salary = salary
        self.date_of_birth = date_of_birth
        self.citizenship = citizenship
        self.employment_start_date = employment_start_date
        self.job_title = job_title
        self.branch = branch

    def __str__(self):
        return f"Employee[ID={self.employee_id}, Name={self.name}, Email={self.email}, Job Title={self.job_title}, Branch={self.branch}]"