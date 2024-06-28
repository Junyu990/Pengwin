class SouthKoreaPayroll:
    def __init__(self, gross_salary, wallet_address):
        self.gross_salary = gross_salary
        self.income_tax = 0
        self.local_income_tax = 0
        self.social_security_contribution = 0
        self.net_salary = 0
        self.wallet_address = wallet_address
        self.calculate_taxes()
        self.calculate_net_salary()

    def calculate_taxes(self):
        self.income_tax = self.calculate_income_tax(self.gross_salary)
        self.local_income_tax = self.calculate_local_income_tax(self.income_tax)
        self.social_security_contribution = self.calculate_social_security_contribution(self.gross_salary)

    def calculate_income_tax(self, gross_salary):
        # Progressive income tax rates for South Korea
        brackets = [
            (12000000, 0.06),
            (34000000, 0.15),
            (42000000, 0.25),
            (212000000, 0.35),
            (float('inf'), 0.40)
        ]
        
        tax = 0
        for bracket in brackets:
            if gross_salary > bracket[0]:
                taxable_income = min(gross_salary, bracket[0])
                tax += taxable_income * bracket[1]
                gross_salary -= taxable_income
            else:
                tax += gross_salary * bracket[1]
                break

        return tax

    def calculate_local_income_tax(self, income_tax):
        return income_tax * 0.10

    def calculate_social_security_contribution(self, gross_salary):
        # Assuming a combined rate for National Pension, Health Insurance, and Employment Insurance
        # National Pension: 4.5%
        # Health Insurance: 3.5%
        # Employment Insurance: 1.0%
        # Total: 8.8%
        return gross_salary * 0.088

    def calculate_net_salary(self):
        self.net_salary = (self.gross_salary - self.income_tax - self.local_income_tax - self.social_security_contribution)

    def calculate_total_taxes(self):
        return self.income_tax + self.local_income_tax + self.social_security_contribution
    
    def get_salary_breakdown(self):
        return {
            "Gross Salary": self.gross_salary,
            "Income Tax": self.income_tax,
            "Local Income Tax": self.local_income_tax,
            "Social Security Contribution": self.social_security_contribution,
            "Net Salary": self.net_salary,
            "Total Taxes": self.calculate_total_taxes(),
            "Country Wallet Address": self.wallet_address  # Example field, update as needed
        }

class SingaporePayroll:
    def __init__(self, gross_salary, wallet_address):
        self.gross_salary = gross_salary
        self.income_tax = 0
        self.cpf_contribution = 0
        self.net_salary = 0
        self.wallet_address = wallet_address
        self.calculate_taxes()
        self.calculate_net_salary()

    def calculate_taxes(self):
        self.income_tax = self.calculate_income_tax(self.gross_salary)
        self.cpf_contribution = self.calculate_cpf_contribution(self.gross_salary)

    def calculate_income_tax(self, gross_salary):
        # Progressive income tax rates for Singapore
        brackets = [
            (20000, 0.02),
            (30000, 0.035),
            (40000, 0.07),
            (80000, 0.115),
            (120000, 0.15),
            (160000, 0.18),
            (200000, 0.19),
            (240000, 0.195),
            (280000, 0.20),
            (float('inf'), 0.22)
        ]
        
        tax = 0
        for bracket in brackets:
            if gross_salary > bracket[0]:
                taxable_income = min(gross_salary, bracket[0])
                tax += taxable_income * bracket[1]
                gross_salary -= taxable_income
            else:
                tax += gross_salary * bracket[1]
                break

        return tax

    def calculate_cpf_contribution(self, gross_salary):
        # Assuming CPF contributions are calculated at a rate of 20% for simplicity
        # In reality, CPF rates vary based on age and other factors
        return gross_salary * 0.20

    def calculate_net_salary(self):
        self.net_salary = self.gross_salary - self.income_tax - self.cpf_contribution
        
    def calculate_total_taxes(self):
        return self.income_tax + self.cpf_contribution

    def get_salary_breakdown(self):
        return {
            "Gross Salary": self.gross_salary,
            "Income Tax": self.income_tax,
            "CPF Contribution": self.cpf_contribution,
            "Net Salary": self.net_salary,
            "Total Taxes": self.calculate_total_taxes(),
            "Country Wallet Address": self.wallet_address  # Example field, update as needed
        }