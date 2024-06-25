document.addEventListener('DOMContentLoaded', function() {
    const rightPanel = document.getElementById('rightPanel');
    const togglePanelBtn = document.getElementById('togglePanelBtn');
    const closePanelBtn = document.getElementById('closePanelBtn');
    const employeeList = document.getElementById('employeeList');
    const selectedCount = document.getElementById('selectedCount');
    const totalPayment = document.getElementById('totalPayment');
    const checkboxes = document.querySelectorAll('input[name="employee_id"]');
    let selectedEmployees = [];

    // Set payroll date to current date
    const payrollDate = document.getElementById('payrollDate');
    payrollDate.textContent = new Date().toLocaleDateString();

    function showPanel() {
        rightPanel.style.right = '0';
        togglePanelBtn.style.display = 'none';
    }

    function hidePanel() {
        rightPanel.style.right = '-600px';
        togglePanelBtn.style.display = 'block';
    }

    function updateSelectedEmployees() {
        selectedEmployees = [];
        let totalPaymentAmount = 0;
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const row = checkbox.closest('tr');
                const name = row.querySelector('td:nth-child(2)').textContent;
                const salary = parseFloat(row.querySelector('td:nth-child()').textContent.replace('$', ''));
                selectedEmployees.push({ name, salary });
                totalPaymentAmount += salary;
            }
        });

        selectedCount.textContent = selectedEmployees.length;
        totalPayment.textContent = `$${totalPaymentAmount.toFixed(2)}`;

        // Update employee list in the panel
        employeeList.innerHTML = '';
        selectedEmployees.forEach(employee => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.textContent = `${employee.name}: $${employee.salary.toFixed(2)}`;
            employeeList.appendChild(listItem);
        });
    }

    togglePanelBtn.addEventListener('click', showPanel);
    closePanelBtn.addEventListener('click', hidePanel);

    // Handle row click to toggle checkbox
    document.querySelectorAll('.table-responsive tr').forEach(row => {
        row.addEventListener('click', function(event) {
            if (event.target.type !== 'checkbox') {
                const checkbox = this.querySelector('input[name="employee_id"]');
                checkbox.checked = !checkbox.checked;
                updateSelectedEmployees();
            }
        });
    });

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedEmployees);
    });
});