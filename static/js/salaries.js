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

    // Example: Interact with your smart contract (replace with actual ABI and contract address)
    const contractAbi = [
        [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "inputs": [
                    {
                        "internalType": "address payable",
                        "name": "employee",
                        "type": "address"
                    }
                ],
                "name": "distributeSalary",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "klayUsdPrice",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "owner",
                "outputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "",
                        "type": "address"
                    }
                ],
                "name": "salaryByLocation",
                "outputs": [
                    {
                        "internalType": "uint256",
                        "name": "",
                        "type": "uint256"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "address",
                        "name": "employee",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amount",
                        "type": "uint256"
                    }
                ],
                "name": "setSalary",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {
                        "internalType": "uint256",
                        "name": "newPrice",
                        "type": "uint256"
                    }
                ],
                "name": "updateKlayUsdPrice",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
    ];
    const contractAddress = '0xfd4b0f538cad6245db3abe7a897243e2b6c46d393c43c2a1c4bfd19ed39819f3'; // Replace with your contract address

    // Example: Set salary function
    document.getElementById('setSalaryBtn').addEventListener('click', async function() {
        const employeeAddress = '0xEmployeeAddress'; // Replace with the employee's address
        const salaryAmount = 100; // Example: Set salary amount (in Wei)

        try {
            if (typeof window.ethereum !== 'undefined') {
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                const account = accounts[0];
                const contract = new web3.eth.Contract(contractAbi, contractAddress);

                // Example: Call setSalary function on your smart contract
                await contract.methods.setSalary(employeeAddress, salaryAmount).send({ from: account });

                console.log('Salary set successfully!');
                // Add UI update or success message here
            } else {
                console.error('MetaMask is not installed');
            }
        } catch (error) {
            console.error('Error setting salary:', error);
            // Handle error and display user-friendly message
        }
    });

    // Example: Distribute salary function
    document.getElementById('distributeSalaryBtn').addEventListener('click', async function() {
        const employeeAddress = '0xEmployeeAddress'; // Replace with the employee's address

        try {
            if (typeof window.ethereum !== 'undefined') {
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                const account = accounts[0];
                const contract = new web3.eth.Contract(contractAbi, contractAddress);

                // Example: Call distributeSalary function on your smart contract
                await contract.methods.distributeSalary(employeeAddress).send({ from: account, value: web3.utils.toWei('1', 'ether') });

                console.log('Salary distributed successfully!');
                // Add UI update or success message here
            } else {
                console.error('MetaMask is not installed');
            }
        } catch (error) {
            console.error('Error distributing salary:', error);
            // Handle error and display user-friendly message
        }
    });

    // Example: Update KLAY/USD price function
    document.getElementById('updatePriceBtn').addEventListener('click', async function() {
        const newPrice = 210000000000000000; // Example: New price in Wei (replace with your actual logic)
        
        try {
            if (typeof window.ethereum !== 'undefined') {
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                const account = accounts[0];
                const contract = new web3.eth.Contract(contractAbi, contractAddress);

                // Example: Call updateKlayUsdPrice function on your smart contract
                await contract.methods.updateKlayUsdPrice(newPrice).send({ from: account });

                console.log('Klay/USD price updated successfully!');
                // Add UI update or success message here
            } else {
                console.error('MetaMask is not installed');
            }
        } catch (error) {
            console.error('Error updating Klay/USD price:', error);
            // Handle error and display user-friendly message
        }
    });
});
