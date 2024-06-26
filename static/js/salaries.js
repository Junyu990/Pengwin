document.addEventListener('DOMContentLoaded', async function() {
    const rightPanel = document.getElementById('rightPanel');
    const togglePanelBtn = document.getElementById('togglePanelBtn');
    const closePanelBtn = document.getElementById('closePanelBtn');
    const employeeList = document.getElementById('employeeList');
    const selectedCount = document.getElementById('selectedCount');
    const totalPayment = document.getElementById('totalPayment');
    const totalinKlay = document.getElementById('totalinKlay');
    const checkboxes = document.querySelectorAll('input[name="employee_id"]');
    const contractBalanceElement = document.getElementById('contractBalance'); // Element to display contract balance
    let selectedEmployees = []; // Define selectedEmployees at a higher scope
    let account;
    let contract;

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
        let totalinKlayamount = 0
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const row = checkbox.closest('tr');
                const name = row.querySelector('td:nth-child(2)').textContent;
                const address = row.querySelector('td:nth-child(3)').textContent;
                const salary = parseFloat(row.querySelector('td:nth-child(6)').textContent.replace('$', ''));
                selectedEmployees.push({ name, address, salary });
                totalPaymentAmount += salary;
                totalinKlayamount += salary * 6.118;
            }
        });

        selectedCount.textContent = selectedEmployees.length;
        totalPayment.textContent = `$${totalPaymentAmount.toFixed(2)}`;
        totalinKlay.textContent = `${totalinKlayamount.toFixed(2)}`;

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
                const web3 = new Web3(window.ethereum);

                // Request account access if needed
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                account = accounts[0];
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

                // Initialize contract
                contract = new web3.eth.Contract(abi, contractAddress);
            } catch (error) {
                console.error('User rejected the request or an error occurred', error);
            }
        } else {
            console.error('MetaMask is not installed');
        }
    });

    // Contract ABI and address
    const abi = [
        {
            "inputs": [
                {
                    "internalType": "address payable",
                    "name": "_employeeAddress",
                    "type": "address"
                },
                {
                    "internalType": "uint256",
                    "name": "_salaryAmount",
                    "type": "uint256"
                }
            ],
            "name": "transferSalary",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "stateMutability": "payable",
            "type": "receive"
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
        }
    ];
    const contractAddress = '0x7Ce49F0520F521a39E77E40d2Bf0D1b6D1c94646'; // Replace with your contract address

    // Initialize contract
    const web3 = new Web3(window.ethereum); // Initialize Web3

    try {
        // Request account access if needed
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        account = accounts[0];
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

        // Initialize contract instance
        contract = new web3.eth.Contract(abi, contractAddress);

        // Fetch and display contract balance
        const contractBalance = await web3.eth.getBalance(contractAddress);
        const contractKlayBalance = web3.utils.fromWei(contractBalance, 'ether');
        contractBalanceElement.textContent = contractKlayBalance;

        // Event listener for Distribute button (directly within DOMContentLoaded)
        const distributeBtn = document.getElementById('distributeBtn');
        if (distributeBtn) {
            distributeBtn.addEventListener('click', async function() {
                try {
                    if (!contract || !account) {
                        throw new Error('Contract not initialized or account not connected');
                    }

                    // Get selected employee addresses and salaries
                    const employeeTransactions = [];
                    selectedEmployees.forEach(({ address, salary }) => {
                        const usdToWeiRate = salary * 6.1118; // Exchange rate from USD to Wei
                        const salaryWei = web3.utils.toWei(usdToWeiRate.toString(), 'ether'); // Convert salary to Wei
                        console.log(salaryWei);
                        // Prepare transaction parameters
                        const transactionParameters = {
                            to: contractAddress,
                            from: account,
                            data: contract.methods.transferSalary(address, salaryWei).encodeABI()
                        };

                        // Add transaction object to array
                        employeeTransactions.push(transactionParameters);
                    });

                    // Sign and send each transaction
                    const results = await Promise.all(employeeTransactions.map(params =>
                        web3.eth.sendTransaction(params)
                    ));

                    console.log('Transactions sent:', results);
                    alert('Salaries distributed successfully!');
                } catch (error) {
                    console.error('Error distributing salaries:', error);
                    alert('Error distributing salaries. See console for details.');
                }
            });
        }

        // Event listener for Deposit button
        const depositBtn = document.getElementById('depositBtn');
        if (depositBtn) {
            depositBtn.addEventListener('click', async function() {
                try {
                    // Prompt user to enter deposit amount
                    const depositAmount = prompt('Enter the amount of Ether to deposit:');

                    if (!depositAmount || isNaN(depositAmount)) {
                        throw new Error('Invalid amount');
                    }

                    // Convert Ether to Wei
                    const amountWei = web3.utils.toWei(depositAmount.toString(), 'ether');

                    // Send transaction to deposit Ether into the contract
                    const transactionParameters = {
                        to: contractAddress,
                        from: account,
                        value: amountWei
                    };

                    // Send transaction
                    const result = await web3.eth.sendTransaction(transactionParameters);

                    console.log('Deposit transaction result:', result);
                    alert(`Successfully deposited ${depositAmount} Ether into the contract!`);
                } catch (error) {
                    console.error('Error depositing Ether:', error);
                    alert('Error depositing Ether. See console for details.');
                }
            });
        }
    } catch (error) {
        console.error('User rejected the request or an error occurred', error);
    }
});
