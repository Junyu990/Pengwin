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
                const salary = parseFloat(row.querySelector('td:nth-child(5)').textContent.replace('$', ''));
                selectedEmployees.push({ name, salary });
                totalPaymentAmount += salary;
            }
        });

        selectedCount.textContent = selectedEmployees.length;
        totalPayment.textContent = `$${totalPaymentAmount.toFixed(2)}`;

        // Update employee list in the panel
        employeeList.innerHTML = '';
        selectedEmployees.slice(0, 5).forEach(employee => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.textContent = `${employee.name}: $${employee.salary.toFixed(2)}`;
            employeeList.appendChild(listItem);
        });

        // Show "See More" button if there are more than 5 selected employees
        if (selectedEmployees.length > 5) {
            const seeMoreBtn = document.createElement('button');
            seeMoreBtn.className = 'btn btn-link';
            seeMoreBtn.textContent = 'See More';
            seeMoreBtn.onclick = function() {
                employeeList.innerHTML = '';
                selectedEmployees.forEach(employee => {
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item';
                    listItem.textContent = `${employee.name}: $${employee.salary.toFixed(2)}`;
                    employeeList.appendChild(listItem);
                });

                // Show "See Less" button after "See More" is clicked
                const seeLessBtn = document.createElement('button');
                seeLessBtn.className = 'btn btn-link';
                seeLessBtn.textContent = 'See Less';
                seeLessBtn.onclick = function() {
                    updateSelectedEmployees();
                };
                employeeList.appendChild(seeLessBtn);
                seeMoreBtn.remove();
            };
            employeeList.appendChild(seeMoreBtn);
        }
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

   // MetaMask wallet connection
   const connectMetaMaskBtn = document.getElementById('connectMetaMaskBtn');
   const walletInfoDiv = document.createElement('div');
   connectMetaMaskBtn.parentNode.insertBefore(walletInfoDiv, connectMetaMaskBtn.nextSibling);

   // Fetch and display KLAY balance from MetaMask
   connectMetaMaskBtn.addEventListener('click', async function() {
       if (typeof window.ethereum !== 'undefined') {
           try {
               // Initialize Web3
               let web3;
               if (typeof window.ethereum !== 'undefined') {
                   web3 = new Web3(window.ethereum);
               } else {
                   console.error('MetaMask is not installed');
                   return; // Exit early or handle the error
               }

               // Request account access if needed
               const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
               const account = accounts[0];
               console.log('Connected to MetaMask with account:', account);

               // Update button text with the connected account address
               connectMetaMaskBtn.textContent = `Connected: ${account.slice(0, 6)}...${account.slice(-4)}`;
               connectMetaMaskBtn.classList.add('btn-success'); // Optionally change the button style

               // Fetch KLAY balance using MetaMask provider and Web3
               const balance = await web3.eth.getBalance(account);
               const klayBalance = web3.utils.fromWei(balance, 'ether');

               // Display balance below the button
               walletInfoDiv.textContent = `Balance: ${klayBalance} KLAY`;
               walletInfoDiv.classList.add('mt-2');
           } catch (error) {
               console.error('User rejected the request or an error occurred', error);
           }
       } else {
           console.error('MetaMask is not installed');
       }
    });
});
