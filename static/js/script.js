document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');
    const tableList = document.getElementById('table-list');
    const modal = document.getElementById('table-preview-modal');
    const addTableModal = document.getElementById('add-table-modal');
    const addTableBtn = document.getElementById('add-table-btn');
    const addTableForm = document.getElementById('add-table-form');
    const addTableSqlForm = document.getElementById('add-table-sql-form');
    const closeButtons = document.querySelectorAll('.close-btn');
    const modalTableName = document.getElementById('modal-table-name');
    const modalColumnsList = document.getElementById('modal-columns-list');
    const modalSampleData = document.getElementById('modal-sample-data');
    const addColumnBtn = document.getElementById('add-column-btn');
    const columnsContainer = document.getElementById('columns-container');
    const cancelBtns = document.querySelectorAll('.cancel-btn');
    const tabLinks = document.querySelectorAll('.tab-link');
    const printChatBtn = document.getElementById('print-chat-btn');

    let conversationState = { prompt: '' };
    let currentChatId = null;
    let allTables = [];

    async function rebuildSchemaGraph() {
        try {
            await fetch('/api/rebuild-graph', { method: 'POST' });
        } catch (error) {
            console.error('Error rebuilding schema graph:', error);
        }
    }

    async function loadTables() {
        try {
            const response = await fetch('/api/tables');
            const tables = await response.json();
            allTables = tables;
            tableList.innerHTML = '';
            tables.forEach(table => {
                const listItem = document.createElement('li');
                listItem.textContent = table;
                
                const deleteIcon = document.createElement('i');
                deleteIcon.classList.add('fas', 'fa-trash-alt', 'delete-table-icon');
                deleteIcon.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    const confirmation = confirm(`Are you sure you want to delete the table "${table}"?`);
                    if (confirmation) {
                        try {
                            const response = await fetch(`/api/table/${table}`, { method: 'DELETE' });
                            if (response.ok) {
                                await loadTables();
                                await rebuildSchemaGraph();
                            } else {
                                const data = await response.json();
                                throw new Error(data.error || 'Failed to delete table.');
                            }
                        } catch (error) {
                            console.error('Error deleting table:', error);
                            alert(`Error: ${error.message}`);
                        }
                    }
                });

                listItem.appendChild(deleteIcon);
                listItem.addEventListener('click', () => {
                    openTablePreview(table);
                });
                tableList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Error loading tables:', error);
        }
    }

    async function openTablePreview(tableName) {
        try {
            const response = await fetch(`/api/table/${tableName}`);
            const data = await response.json();

            if (response.ok) {
                modalTableName.textContent = tableName;
                
                modalColumnsList.innerHTML = '';
                data.columns.forEach(column => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${column.name} (${column.type})`;
                    modalColumnsList.appendChild(listItem);
                });

                modalSampleData.innerHTML = '';
                if (data.sample_data && data.sample_data.length > 0) {
                    const table = document.createElement('table');
                    const thead = document.createElement('thead');
                    const tbody = document.createElement('tbody');
                    const headerRow = document.createElement('tr');

                    Object.keys(data.sample_data[0]).forEach(key => {
                        const th = document.createElement('th');
                        th.textContent = key;
                        headerRow.appendChild(th);
                    });
                    thead.appendChild(headerRow);

                    data.sample_data.forEach(rowData => {
                        const row = document.createElement('tr');
                        Object.values(rowData).forEach(value => {
                            const td = document.createElement('td');
                            td.textContent = value;
                            row.appendChild(td);
                        });
                        tbody.appendChild(row);
                    });

                    table.appendChild(thead);
                    table.appendChild(tbody);
                    modalSampleData.appendChild(table);
                } else {
                    modalSampleData.textContent = 'No sample data available.';
                }

                modal.style.display = 'block';
            } else {
                throw new Error(data.error || 'Failed to fetch table preview.');
            }
        } catch (error) {
            console.error('Error fetching table preview:', error);
            alert(`Error: ${error.message}`);
        }
    }

    closeButtons.forEach(btn => {
        btn.onclick = () => {
            modal.style.display = 'none';
            addTableModal.style.display = 'none';
        };
    });

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
        if (event.target == addTableModal) {
            addTableModal.style.display = 'none';
        }
    };

    addTableBtn.addEventListener('click', () => {
        addTableModal.style.display = 'block';
    });

    cancelBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            addTableModal.style.display = 'none';
        });
    });

    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            const tabId = link.dataset.tab;

            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');

            tabLinks.forEach(innerLink => {
                innerLink.classList.remove('active');
            });
            link.classList.add('active');
        });
    });

    function createColumnRow() {
        const newColumnRow = document.createElement('div');
        newColumnRow.classList.add('column-row');
        newColumnRow.innerHTML = `
            <div class="form-group">
                <input type="text" name="column_name" placeholder="name" required>
            </div>
            <div class="form-group">
                <select name="column_type" required>
                    <option value="VARCHAR(255)" selected>VARCHAR(255)</option>
                    <option value="INT">INT</option>
                    <option value="TEXT">TEXT</option>
                    <option value="DATE">DATE</option>
                    <option value="DATETIME">DATETIME</option>
                    <option value="BOOLEAN">BOOLEAN</option>
                    <option value="DECIMAL(10, 2)">DECIMAL(10, 2)</option>
                    <option value="SERIAL">SERIAL</option>
                </select>
            </div>
            <div class="form-group">
                <input type="text" name="column_default" placeholder="null">
            </div>
            <div class="form-group">
                <select name="column_constraints">
                    <option value="">None</option>
                    <option value="PRIMARY KEY">PRIMARY KEY</option>
                    <option value="UNIQUE">UNIQUE</option>
                    <option value="NOT NULL">NOT NULL</option>
                    <option value="FOREIGN KEY">FOREIGN KEY</option>
                </select>
            </div>
            <div class="form-group foreign-key-details" style="display: none;">
                <select name="foreign_key_table"></select>
                <select name="foreign_key_column"></select>
            </div>
        `;
        columnsContainer.appendChild(newColumnRow);
        initializeForeignKeyFunctionality(newColumnRow);
    }

    async function initializeForeignKeyFunctionality(row) {
        const constraintSelect = row.querySelector('select[name="column_constraints"]');
        const foreignKeyDetails = row.querySelector('.foreign-key-details');
        const fkTableSelect = row.querySelector('select[name="foreign_key_table"]');
        const fkColumnSelect = row.querySelector('select[name="foreign_key_column"]');

        fkTableSelect.innerHTML = '<option value="">Select table</option>';
        allTables.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.textContent = table;
            fkTableSelect.appendChild(option);
        });

        constraintSelect.addEventListener('change', (e) => {
            if (e.target.value === 'FOREIGN KEY') {
                foreignKeyDetails.style.display = 'contents';
            } else {
                foreignKeyDetails.style.display = 'none';
            }
        });

        fkTableSelect.addEventListener('change', async (e) => {
            const selectedTable = e.target.value;
            fkColumnSelect.innerHTML = '<option value="">Select column</option>';
            if (selectedTable) {
                try {
                    const response = await fetch(`/api/table/${selectedTable}/columns`);
                    const columns = await response.json();
                    columns.forEach(column => {
                        const option = document.createElement('option');
                        option.value = column;
                        option.textContent = column;
                        fkColumnSelect.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error fetching columns:', error);
                }
            }
        });
    }

    addColumnBtn.addEventListener('click', createColumnRow);

    addTableForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tableName = document.getElementById('new-table-name').value.trim();
        const columnRows = columnsContainer.querySelectorAll('.column-row');
        
        let columns = [];
        let foreignKeys = [];

        columnRows.forEach(row => {
            const name = row.querySelector('input[name="column_name"]').value.trim();
            const type = row.querySelector('select[name="column_type"]').value;
            const defaultVal = row.querySelector('input[name="column_default"]').value.trim();
            const constraints = row.querySelector('select[name="column_constraints"]').value;
            
            if(name && type) {
                let columnDef = `${name} ${type}`;
                if (defaultVal && defaultVal.toLowerCase() !== 'no default') {
                    columnDef += ` DEFAULT ${defaultVal}`;
                }
                if (constraints && constraints !== 'FOREIGN KEY') {
                    columnDef += ` ${constraints}`;
                }
                columns.push(columnDef);

                if (constraints === 'FOREIGN KEY') {
                    const fkTable = row.querySelector('select[name="foreign_key_table"]').value;
                    const fkColumn = row.querySelector('select[name="foreign_key_column"]').value;
                    if (fkTable && fkColumn) {
                        foreignKeys.push(`FOREIGN KEY (${name}) REFERENCES ${fkTable}(${fkColumn})`);
                    }
                }
            }
        });

        const columnsStr = columns.join(', ');
        const foreignKeysStr = foreignKeys.join(', ');
        const finalColumnsStr = foreignKeys.length > 0 ? `${columnsStr}, ${foreignKeysStr}` : columnsStr;

        if (tableName && finalColumnsStr) {
            try {
                const response = await fetch('/api/tables', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: 'form', tableName, columns: finalColumnsStr }),
                });

                if (response.ok) {
                    addTableModal.style.display = 'none';
                    addTableForm.reset();
                    columnsContainer.innerHTML = '';
                    createColumnRow();
                    await loadTables();
                    await rebuildSchemaGraph();
                } else {
                    const data = await response.json();
                    throw new Error(data.error || 'Failed to add table.');
                }
            } catch (error) {
                console.error('Error adding table:', error);
                alert(`Error: ${error.message}`);
            }
        }
    });

    addTableSqlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const sql = document.getElementById('sql-create-statement').value.trim();
        if (sql) {
            try {
                const response = await fetch('/api/tables', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: 'sql', sql }),
                });

                if (response.ok) {
                    addTableModal.style.display = 'none';
                    addTableSqlForm.reset();
                    await loadTables();
                    await rebuildSchemaGraph();
                } else {
                    const data = await response.json();
                    throw new Error(data.error || 'Failed to add table.');
                }
            } catch (error) {
                console.error('Error adding table:', error);
                alert(`Error: ${error.message}`);
            }
        }
    });

    function loadChatHistory() {
        const chats = JSON.parse(localStorage.getItem('chats')) || {};
        historyList.innerHTML = '';
        for (const chatId in chats) {
            const chat = chats[chatId];
            const listItem = document.createElement('li');

            const words = chat.title.split(' ');
            let displayTitle = chat.title;
            if (words.length > 5) {
                displayTitle = words.slice(0, 5).join(' ') + '...';
            }
            
            const titleSpan = document.createElement('span');
            titleSpan.textContent = displayTitle;
            titleSpan.title = chat.title;
            listItem.appendChild(titleSpan);

            const iconsDiv = document.createElement('div');
            iconsDiv.classList.add('history-icons');

            const renameIcon = document.createElement('i');
            renameIcon.classList.add('fas', 'fa-pencil-alt');
            renameIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                renameChat(chatId);
            });
            iconsDiv.appendChild(renameIcon);

            const deleteIcon = document.createElement('i');
            deleteIcon.classList.add('fas', 'fa-trash-alt');
            deleteIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteChat(chatId);
            });
            iconsDiv.appendChild(deleteIcon);

            listItem.appendChild(iconsDiv);
            listItem.dataset.chatId = chatId;
            listItem.addEventListener('click', () => {
                loadChat(chatId);
            });
            historyList.appendChild(listItem);
        }
    }

    function renameChat(chatId) {
        const newName = prompt("Enter new chat name:");
        if (newName) {
            const chats = JSON.parse(localStorage.getItem('chats')) || {};
            if (chats[chatId]) {
                chats[chatId].title = newName;
                localStorage.setItem('chats', JSON.stringify(chats));
                loadChatHistory();
            }
        }
    }

    function deleteChat(chatId) {
        const confirmation = confirm("Are you sure you want to delete this chat?");
        if (confirmation) {
            const chats = JSON.parse(localStorage.getItem('chats')) || {};
            delete chats[chatId];
            localStorage.setItem('chats', JSON.stringify(chats));
            if (currentChatId === chatId) {
                currentChatId = null;
                chatHistory.innerHTML = '';
                 addMessage('bot', 'Hey! I\'m your personal SQL agent. Ask me a question about your data, and I\'ll help you build the right query to answer it.');
            }
            loadChatHistory();
        }
    }

    function loadChat(chatId) {
        const chats = JSON.parse(localStorage.getItem('chats')) || {};
        const chat = chats[chatId];
        if (chat) {
            currentChatId = chatId;
            chatHistory.innerHTML = '';
            chat.messages.forEach((message, index) => {
                if (message.sender === 'bot' && typeof message.message === 'object' && message.message.type === 'confirmation') {
                    const nextMessage = chat.messages[index + 1];
                    const isCompleted = nextMessage && nextMessage.sender === 'user' && nextMessage.message.startsWith('Confirmed tables:');
                    addConfirmation(message.message.tables, true, isCompleted);
                } else {
                    addMessage(message.sender, message.message, message.isHtml, message.isSql);
                }
            });
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    }

    function saveMessage(sender, message, isHtml = false, isSql = false) {
        const chats = JSON.parse(localStorage.getItem('chats')) || {};
        if (!currentChatId) {
            currentChatId = `chat_${Date.now()}`;
            chats[currentChatId] = { title: 'New Chat', messages: [] };
        }

        chats[currentChatId].messages.push({ sender, message, isHtml, isSql });

        if (chats[currentChatId].messages.length === 1 && sender === 'user') {
            chats[currentChatId].title = message;
        }
        localStorage.setItem('chats', JSON.stringify(chats));
        loadChatHistory();
    }

    function addMessage(sender, message, isHtml = false, isSql = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);

        const avatar = document.createElement('img');
        avatar.classList.add('avatar');
        avatar.src = sender === 'user' ? 'https://img.icons8.com/color/48/000000/user-male-circle.png' : 'https://img.icons8.com/fluency/48/000000/bot.png';
        
        const content = document.createElement('div');
        content.classList.add('content');

        if (isSql) {
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.textContent = message;
            pre.appendChild(code);
            content.appendChild(pre);

            const copyBtn = document.createElement('button');
            copyBtn.innerHTML = '<i class="far fa-copy"></i> Copy SQL';
            copyBtn.className = 'copy-sql-btn';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(message).then(() => {
                    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        copyBtn.innerHTML = '<i class="far fa-copy"></i> Copy SQL';
                    }, 2000);
                });
            };
            content.appendChild(copyBtn);
        } else if (isHtml) {
            content.innerHTML = marked.parse(message);
        } else {
            content.textContent = message;
        }

        messageElement.appendChild(avatar);
        messageElement.appendChild(content);
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('message', 'bot', 'typing-indicator');

        const avatar = document.createElement('img');
        avatar.classList.add('avatar');
        avatar.src = 'https://img.icons8.com/fluency/48/000000/bot.png';

        const content = document.createElement('div');
        content.classList.add('content');
        content.innerHTML = '<div class="typing-dots"><div></div><div></div><div></div></div>';

        typingIndicator.appendChild(avatar);
        typingIndicator.appendChild(content);
        chatHistory.appendChild(typingIndicator);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function addConfirmation(suggestedTables, isReloading = false, isCompleted = false) {
        let currentTables = [...suggestedTables];

        const confirmationContainer = document.createElement('div');
        confirmationContainer.classList.add('confirmation-container');

        const message = document.createElement('p');
        if (currentTables.length > 0) {
            message.textContent = "I'm planning to use the tables below to generate the query. Does this look correct?";
        } else {
            message.textContent = "I couldn't identify the right tables for your request. Please select the tables you'd like to use below.";
        }
        confirmationContainer.appendChild(message);

        const tableSelector = document.createElement('div');
        tableSelector.classList.add('table-selector');
        
        const header = document.createElement('div');
        header.classList.add('table-selector-header');
        header.textContent = 'Tables to be used:';
        tableSelector.appendChild(header);

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Add another table...';
        searchInput.classList.add('table-search-input');
        tableSelector.appendChild(searchInput);

        const tableListElement = document.createElement('ul');
        tableListElement.classList.add('table-list');
        tableSelector.appendChild(tableListElement);

        const suggestionsList = document.createElement('ul');
        suggestionsList.classList.add('suggestions-list');
        tableSelector.appendChild(suggestionsList);

        const renderTableList = () => {
            tableListElement.innerHTML = '';
            currentTables.forEach(table => {
                const listItem = document.createElement('li');
                listItem.textContent = table;
                if (!isCompleted) {
                    const removeBtn = document.createElement('span');
                    removeBtn.textContent = ' ×';
                    removeBtn.classList.add('remove-table');
                    removeBtn.onclick = () => {
                        currentTables = currentTables.filter(t => t !== table);
                        renderTableList();
                    };
                    listItem.appendChild(removeBtn);
                }
                tableListElement.appendChild(listItem);
            });
        };

        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase();
            suggestionsList.innerHTML = '';
            if (query) {
                const filteredTables = allTables.filter(t => t.toLowerCase().includes(query) && !currentTables.includes(t));
                filteredTables.forEach(table => {
                    const listItem = document.createElement('li');
                    listItem.textContent = table;
                    listItem.onclick = () => {
                        currentTables.push(table);
                        renderTableList();
                        searchInput.value = '';
                        suggestionsList.innerHTML = '';
                    };
                    suggestionsList.appendChild(listItem);
                });
            }
        });

        const looksGoodBtn = document.createElement('button');
        looksGoodBtn.classList.add('looks-good-btn');
        looksGoodBtn.textContent = 'Looks Good';
        
        if (!isCompleted) {
            let countdown = 10;
            const countdownInterval = setInterval(() => {
                countdown--;
                looksGoodBtn.textContent = `Looks Good (${countdown})`;
                if (countdown <= 0) {
                    clearInterval(countdownInterval);
                    looksGoodBtn.textContent = 'Looks Good';
                    looksGoodBtn.disabled = false;
                }
            }, 1000);
            looksGoodBtn.onclick = () => {
                clearInterval(countdownInterval);
                handleConfirmation(true, currentTables, confirmationContainer);
            };
        } else {
            looksGoodBtn.style.display = 'none';
        }

        tableSelector.appendChild(looksGoodBtn);
        confirmationContainer.appendChild(tableSelector);

        if (isCompleted) {
            confirmationContainer.classList.add('disabled');
            searchInput.disabled = true;
        }

        const botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot');
        const avatar = document.createElement('img');
        avatar.classList.add('avatar');
        avatar.src = 'https://img.icons8.com/fluency/48/000000/bot.png';
        botMessage.appendChild(avatar);
        botMessage.appendChild(confirmationContainer);
        chatHistory.appendChild(botMessage);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        renderTableList();
        if (!isReloading) {
            saveMessage('bot', { type: 'confirmation', tables: suggestedTables }, true);
        }
    }

    async function handleConfirmation(isCorrect, tables = [], confirmationContainer) {
      const confirmationMessage = `Confirmed tables: ${tables.join(', ')}`;
      addMessage('user', confirmationMessage);
      saveMessage('user', confirmationMessage);

      if (isCorrect) {
          confirmationContainer.classList.add('disabled');
          const searchInput = confirmationContainer.querySelector('.table-search-input');
          searchInput.disabled = true;

          const removeBtns = confirmationContainer.querySelectorAll('.remove-table');
          removeBtns.forEach(btn => btn.style.display = 'none');

          const looksGoodBtn = confirmationContainer.querySelector('.looks-good-btn');
          looksGoodBtn.style.display = 'none';

          await sendMessage(conversationState.prompt, tables);
      } else {
          addMessage('bot', 'My apologies. Please try rephrasing your question or provide more specific details about the tables I should use.');
          saveMessage('bot', 'My apologies. Please try rephrasing your question or provide more specific details about the tables I should use.');
          conversationState = {}; // Reset state
      }
    }

    async function sendMessage(prompt, tables = null) {
        showTypingIndicator();
        try {
            const chats = JSON.parse(localStorage.getItem('chats')) || {};
            const currentChat = chats[currentChatId];
            const history = currentChat ? currentChat.messages : [];

            const body = { prompt, history };
            if (tables) {
                body.tables = tables;
            }

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            hideTypingIndicator();
            const data = await response.json();

            if (response.ok) {
                if (data.type === 'confirm_tables') {
                    allTables = data.all_tables;
                    addConfirmation(data.tables, false);
                } else if (data.type === 'sql_query') {
                    addMessage('bot', data.sql, false, true);
                    saveMessage('bot', data.sql, false, true);
                    if (data.explanation) {
                        addMessage('bot', data.explanation, true, false);
                        saveMessage('bot', data.explanation, true, false);
                    }
                    conversationState = {}; // Reset state after completion
                } else if (data.type === 'direct_answer' || data.type === 'clarification') {
                    addMessage('bot', data.response, true, false);
                    saveMessage('bot', data.response, true, false);
                }
            } else {
                const errorMessage = data.error || 'Sorry, something went wrong.';
                addMessage('bot', errorMessage, true);
                saveMessage('bot', errorMessage, true);
                if(data.description) {
                    addMessage('bot', `<pre>${data.description}</pre>`, true);
                    saveMessage('bot', `<pre>${data.description}</pre>`, true);
                }
                conversationState = {}; // Reset state on error
            }
        } catch (error) {
            hideTypingIndicator();
            console.error('Error:', error);
            addMessage('bot', 'Sorry, something went wrong. Please try again.');
            saveMessage('bot', 'Sorry, something went wrong. Please try again.');
            conversationState = {}; // Reset state on error
        }
    }

    async function handleUserInput() {
        const prompt = userInput.value.trim();
        if (prompt === '') return;

        addMessage('user', prompt);
        saveMessage('user', prompt);
        userInput.value = '';

        const confirmationContainer = document.querySelector('.confirmation-container:not(.disabled)');
        if (confirmationContainer) {
            const currentTables = Array.from(confirmationContainer.querySelectorAll('.table-list li')).map(li => li.textContent.replace(' ×',''));
            const feedback = prompt;
            const combinedPrompt = `${conversationState.prompt} (user feedback: ${feedback})`;
            
            const parentMessage = confirmationContainer.closest('.message.bot');
            if(parentMessage) {
                parentMessage.remove();
            }

            await sendMessage(combinedPrompt, currentTables);
        } else {
            conversationState.prompt = prompt;
            await sendMessage(prompt);
        }
    }

    newChatBtn.addEventListener('click', () => {
        currentChatId = null;
        chatHistory.innerHTML = '';
        addMessage('bot', 'Hey! I\'m your personal SQL agent. Ask me a question about your data, and I\'ll help you build the right query to answer it.');
    });

    printChatBtn.addEventListener('click', () => {
        window.print();
    });

    addMessage('bot', 'Hey! I\'m your personal SQL agent. Ask me a question about your data, and I\'ll help you build the right query to answer it.');

    window.handleConfirmation = handleConfirmation; 
    sendBtn.addEventListener('click', handleUserInput);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            handleUserInput();
        }
    });

    (async () => {
        await loadTables();
        createColumnRow(); // Create the initial column row
        loadChatHistory();
    })();
});
