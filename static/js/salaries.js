document.addEventListener('DOMContentLoaded', async function() {
    const rightPanel = document.getElementById('rightPanel');
    const togglePanelBtn = document.getElementById('togglePanelBtn');
    const employeeList = document.getElementById('employeeList');
    const selectedCount = document.getElementById('selectedCount');
    const totalPayment = document.getElementById('totalPayment');
    const totalinKlay = document.getElementById('totalinKlay');
    const checkboxes = document.querySelectorAll('input[name="employee_id"]');
    const contractBalanceElement = document.getElementById('contractBalance'); // Element to display contract balance
    const contractBalanceUSDElement = document.getElementById('contractBalanceUSD'); // Element to display contract balance
    const distributeBalanceBtn = document.getElementById('distributeBalanceBtn');
    const errorMessage = document.getElementById('errorMessage'); // Error message element
    const payrollMonth = document.getElementById('payrollMonth'); // Month selector
    const balanceErrorMessage = document.getElementById('balanceErrorMessage');
    
    let selectedEmployees = []; // Define selectedEmployees at a higher scope
    let account;
    let contract;

    async function getUsdToKlayRate() {
        const apiUrl = 'https://api.coingecko.com/api/v3/simple/price?ids=klay-token&vs_currencies=usd';
        
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const klayToUsdRate = data['klay-token'].usd;
            const usdToKlayRate = 1 / klayToUsdRate;
            console.log(`Current USD to KLAY rate: ${usdToKlayRate}`);
            return usdToKlayRate;
        } catch (error) {
            console.error('Error fetching USD to KLAY rate:', error);
            return null;
        }
    }
     await getUsdToKlayRate();
    // Example usage
    getUsdToKlayRate().then(rate => {
        if (rate !== null) {
            // Update your UI or perform calculations with the rate
            console.log(`USD to KLAY rate is ${rate}`);
        }
    });
    
    

    var exchangerate = await getUsdToKlayRate();
    console.log(exchangerate)
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
                const employee_id = checkbox.value; // Assuming employee_id is stored in the value attribute
                const name = row.querySelector('td:nth-child(2)').textContent;
                const address = row.querySelector('td:nth-child(3)').textContent;
                const salary = parseFloat(row.querySelector('td:nth-child(6)').textContent.replace('$', ''));
                const location = row.querySelector('td:nth-child(4)').textContent;
                selectedEmployees.push({ id: employee_id, name, address, salary, location });
                totalPaymentAmount += salary;
                totalinKlayamount += salary * exchangerate;
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

    // togglePanelBtn.addEventListener('click', showPanel);
    // closePanelBtn.addEventListener('click', hidePanel);

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

    const selectAllCheckbox = document.getElementById('selectAll');

    selectAllCheckbox.addEventListener('change', function() {
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
        });
        updateSelectedEmployees();
    });

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (!checkbox.checked) {
                selectAllCheckbox.checked = false;
            } else if (Array.from(checkboxes).every(cb => cb.checked)) {
                selectAllCheckbox.checked = true;
            }
            updateSelectedEmployees();
        });
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
            "inputs": [],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": false,
                    "internalType": "uint256",
                    "name": "amount",
                    "type": "uint256"
                }
            ],
            "name": "BalanceDistributed",
            "type": "event"
        },
        {
            "inputs": [],
            "name": "distributeBalanceToOwner",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": false,
                    "internalType": "string",
                    "name": "errorMessage",
                    "type": "string"
                }
            ],
            "name": "ErrorLog",
            "type": "event"
        },
        {
            "anonymous": false,
            "inputs": [
                {
                    "indexed": false,
                    "internalType": "address",
                    "name": "employee",
                    "type": "address"
                },
                {
                    "indexed": false,
                    "internalType": "address",
                    "name": "country",
                    "type": "address"
                },
                {
                    "indexed": false,
                    "internalType": "uint256",
                    "name": "salaryAmount",
                    "type": "uint256"
                },
                {
                    "indexed": false,
                    "internalType": "uint256",
                    "name": "taxAmount",
                    "type": "uint256"
                }
            ],
            "name": "SalaryTransferred",
            "type": "event"
        },
        {
            "inputs": [
                {
                    "internalType": "address payable",
                    "name": "employee",
                    "type": "address"
                },
                {
                    "internalType": "address payable",
                    "name": "country",
                    "type": "address"
                },
                {
                    "internalType": "uint256",
                    "name": "salaryAmount",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "taxAmount",
                    "type": "uint256"
                }
            ],
            "name": "transferSalary",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
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
    const contractAddress = '0x50796D1d04204687C866D293Ed8BD2721F898f08'; // Replace with your contract address

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
        
        
        contractBalanceUSDElement.textContent = contractKlayBalance / exchangerate;

        // Function to calculate payroll
    async function calculatePayroll(grossSalary, location) {
        try {
            const response = await fetch('/calculate_payroll', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ gross_salary: grossSalary, location: location })
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await response.json();
            console.log(data);
            return data;
        } catch (error) {
            console.error('Error calculating payroll:', error);
            return null;
        }
    }
    
    
    if (distributeBtn) {
        distributeBtn.addEventListener('click', async function() {
            if (!contract || !account) {
                throw new Error('Contract not initialized or account not connected');
            }
    
            if (selectedEmployees.length === 0) {
                errorMessage.style.display = 'block';
                return;
            } else {
                errorMessage.style.display = 'none';
            }
    
            const totalPaymentAmountInUSD = parseFloat(totalPayment.textContent.replace('$', ''));
            const contractBalanceInUSD = parseFloat(contractBalanceUSDElement.textContent.replace('$', ''));
    
            if (totalPaymentAmountInUSD > contractBalanceInUSD) {
                balanceErrorMessage.style.display = 'block';
                return;
            } else {
                balanceErrorMessage.style.display = 'none';
            }
    
            const authKey = document.getElementById('authKey').value;
            if (!authKey) {
                authKeyWarning.textContent = 'Please enter the authorization key.';
                authKeyWarning.style.display = 'block';
                return;
            }
    
            const response = await fetch('/validate-auth-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ authKey })
            });
    
            const result = await response.json();
            if (!result.success) {
                authKeyWarning.textContent = 'Invalid authorization key. Please try again.';
                authKeyWarning.style.display = 'block';
                return;
            }
    
            authKeyWarning.style.display = 'none'; // Hide the warning if the key is valid
    
            const selectedMonth = payrollMonth.value; // Get the selected month

            const currentYear = new Date().getFullYear(); // Get the current year
    
            for (const employee of selectedEmployees) {
                const payrollData = await calculatePayroll(employee.salary, employee.location);
                if (!payrollData) continue;
    
                exchangerate = await getUsdToKlayRate();
    
                const netSalary = payrollData['Net Salary'] * exchangerate;
                const roundedNetSalary = netSalary.toFixed(2);  // Round to 2 decimal places
                const salaryWei = web3.utils.toWei(roundedNetSalary.toString(), 'ether');
    
                let taxWei;
                if (employee.location === 'South Korea' || employee.location === 'Singapore') {
                    const totalTaxes = payrollData['Total Taxes'];
                    const roundedTotalTaxes = (totalTaxes * exchangerate).toFixed(2);  // Round to 2 decimal places
                    taxWei = web3.utils.toWei(roundedTotalTaxes.toString(), 'ether');
                } else {
                    console.error('Unsupported country:', employee.location);
                    continue;
                }
    
                const countryWallet = payrollData['Country Wallet Address'];
                console.log(employee.address, countryWallet, salaryWei, taxWei);
    
                const transactionParameters = {
                    to: contractAddress,
                    from: account,
                    data: contract.methods.transferSalary(employee.address, countryWallet, salaryWei, taxWei).encodeABI(),
                    gas: 3000000 // Increase gas limit
                };
    
                try {
                    const gasEstimate = await web3.eth.estimateGas(transactionParameters);
                    transactionParameters.gas = gasEstimate;
                } catch (error) {
                    console.error(`Failed to estimate gas for ${employee.name}:`, error);
                    continue; // Move to the next employee
                }
    
                try {
                    await web3.eth.sendTransaction(transactionParameters);
    
                    // Record the tax transfer in Firebase
                    await recordTaxTransfer(employee, payrollData, taxWei, selectedMonth, currentYear); // Pass the selected month
                } catch (error) {
                    console.error(`Error Storing ${employee.name}:`, error);
                    continue; // Move to the next employee
                }
            }
    
            location.reload();
            alert('Salaries and taxes distributed successfully!');
        });
    }

    async function recordTaxTransfer(employee, payrollData, taxWei, month, year) {
        const exchangerate = await getUsdToKlayRate();
        const taxUSD = parseFloat(web3.utils.fromWei(taxWei, 'ether')) / exchangerate;

        const taxData = {
            employee_id: employee.id,
            tax_amount_klay: web3.utils.fromWei(taxWei, 'ether'),
            tax_amount_usd: taxUSD.toFixed(2),
            timestamp: new Date().toISOString(),
            country: employee.location,
            month: month, // Include the selected month
            year: year
        };

        if (employee.location === 'South Korea') {
            taxData.income_tax = payrollData["Income Tax"];
            taxData.local_income_tax = payrollData["Local Income Tax"];
            taxData.social_security_contribution = payrollData["Social Security Contribution"];
        } else if (employee.location === 'Singapore') {
            taxData.income_tax = payrollData["Income Tax"];
            taxData.cpf_contribution = payrollData["CPF Contribution"];
        }

        try {
            const response = await fetch('/record_tax_transfer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taxData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            console.log('Tax transfer recorded successfully');
        } catch (error) {
            console.error('Error recording tax transfer:', error);
        }
    }

        // Event listener for Deposit button
        const depositBtn = document.getElementById('depositBtn');
        if (depositBtn) {
            depositBtn.addEventListener('click', async function() {
                try {

                    exchangerate = await getUsdToKlayRate();

                    // Prompt user to enter deposit amount
                    const depositAmount = prompt('Enter the amount of $USD to deposit:');
                    const depositAmountinKlay = depositAmount * exchangerate

                    if (!depositAmount || isNaN(depositAmount)) {
                        throw new Error('Invalid amount');
                    }

                    // Convert Ether to Wei
                    const amountWei = web3.utils.toWei(depositAmountinKlay.toString(), 'ether');

                    // Send transaction to deposit Ether into the contract
                    const transactionParameters = {
                        to: contractAddress,
                        from: account,
                        value: amountWei
                    };

                    // Send transaction
                    const result = await web3.eth.sendTransaction(transactionParameters);



                    console.log('Deposit transaction result:', result);
                    location.reload();
                    alert(`Successfully deposited $${depositAmount} into the contract!`);
                } catch (error) {
                    console.error('Error depositing Ether:', error);
                    alert('Error depositing Ether. See console for details.');
                }
            });
        }

        // Distribute remaining balance in contract to owner
        if (distributeBalanceBtn) {
            distributeBalanceBtn.addEventListener('click', async function() {
                try {
                    if (!contract || !account) {
                        throw new Error('Contract not initialized or account not connected');
                    }
    
                    const transactionParameters = {
                        to: contractAddress,
                        from: account,
                        data: contract.methods.distributeBalanceToOwner().encodeABI()
                    };
    
                    const result = await web3.eth.sendTransaction(transactionParameters);
    
                    console.log('Balance distributed to owner:', result);
                    location.reload();
                    alert('Balance distributed to owner successfully!');
                } catch (error) {
                    console.error('Error distributing balance to owner:', error);
                    alert('Error distributing balance to owner. See console for details.');
                }
            });
        }
    } catch (error) {
        console.error('User rejected the request or an error occurred', error);
    }
});
