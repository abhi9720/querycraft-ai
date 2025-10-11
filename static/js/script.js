document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');
    const tableList = document.getElementById('table-list');
    const modal = document.getElementById('table-preview-modal');
    const closeBtn = document.querySelector('.close-btn');
    const modalTableName = document.getElementById('modal-table-name');
    const modalColumnsList = document.getElementById('modal-columns-list');
    const modalSampleData = document.getElementById('modal-sample-data');

    let conversationState = { prompt: '' };
    let currentChatId = null;
    let allTables = [];

    // Fetch and render tables
    async function loadTables() {
        try {
            const response = await fetch('/api/tables');
            const tables = await response.json();
            tableList.innerHTML = '';
            tables.forEach(table => {
                const listItem = document.createElement('li');
                listItem.textContent = table;
                listItem.addEventListener('click', () => {
                    openTablePreview(table);
                });
                tableList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Error loading tables:', error);
        }
    }

    // Open table preview modal
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

    // Close modal
    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // Load chat history from local storage
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
            listItem.textContent = displayTitle;
            listItem.title = chat.title; // Show full title on hover

            listItem.dataset.chatId = chatId;
            listItem.addEventListener('click', () => {
                loadChat(chatId);
            });
            historyList.appendChild(listItem);
        }
    }

    // Load a specific chat
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
        }
    }

    // Save a message to the current chat
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

    // New Chat button event listener
    newChatBtn.addEventListener('click', () => {
        currentChatId = null;
        chatHistory.innerHTML = '';
        addMessage('bot', 'Hey! I\'m your personal SQL agent. Ask me a question about your data, and I\'ll help you build the right query to answer it.');
    });

    // Initial bot message
    addMessage('bot', 'Hey! I\'m your personal SQL agent. Ask me a question about your data, and I\'ll help you build the right query to answer it.');

    window.handleConfirmation = handleConfirmation; 
    sendBtn.addEventListener('click', handleUserInput);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); 
            handleUserInput();
        }
    });

    loadTables();
    loadChatHistory();
});
