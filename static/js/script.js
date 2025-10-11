document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');
    const tableList = document.getElementById('table-list');

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
                tableList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Error loading tables:', error);
        }
    }

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
            chat.messages.forEach(message => {
                addMessage(message.sender, message.message, message.isHtml, message.isSql);
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

        const isConfirmation = typeof message === 'object' && message.confirmation;

        if (!isConfirmation) {
            chats[currentChatId].messages.push({ sender, message, isHtml, isSql });
        }

        if (chats[currentChatId].messages.length === 1 && !isConfirmation) {
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

    function addConfirmation(suggestedTables) {
        let currentTables = [...suggestedTables];

        const confirmationContainer = document.createElement('div');
        confirmationContainer.classList.add('confirmation-container');

        const message = document.createElement('p');
        message.textContent = "I'm planning to use the tables below to generate the query";
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
                const removeBtn = document.createElement('span');
                removeBtn.textContent = ' ×';
                removeBtn.classList.add('remove-table');
                removeBtn.onclick = () => {
                    currentTables = currentTables.filter(t => t !== table);
                    renderTableList();
                };
                listItem.appendChild(removeBtn);
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
        
        tableSelector.appendChild(looksGoodBtn);
        confirmationContainer.appendChild(tableSelector);

        // Append to chat history
        const botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot');
        const avatar = document.createElement('img');
        avatar.classList.add('avatar');
        avatar.src = 'https://img.icons8.com/fluency/48/000000/bot.png';
        botMessage.appendChild(avatar);
        botMessage.appendChild(confirmationContainer);
        chatHistory.appendChild(botMessage);

        renderTableList();
        saveMessage('bot', { confirmation: true }, true);
    }

    async function handleConfirmation(isCorrect, tables = [], confirmationContainer) {
      const confirmationMessage = `Confirmed tables: ${tables.join(', ')}`;
      addMessage('user', confirmationMessage);
      saveMessage('user', confirmationMessage);

      if (isCorrect) {
          // Visually disable the confirmation container instead of removing it
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
            const body = { prompt };
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
                if (data.tables) {
                    allTables = data.all_tables;
                    addConfirmation(data.tables);
                } else if (data.sql) {
                    addMessage('bot', data.sql, false, true);
                    saveMessage('bot', data.sql, false, true);
                    if (data.explanation) {
                        addMessage('bot', data.explanation, true, false);
                        saveMessage('bot', data.explanation, true, false);
                    }
                    conversationState = {}; // Reset state after completion
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

        // Check if there's an active confirmation
        const confirmationContainer = document.querySelector('.confirmation-container:not(.disabled)');
        if (confirmationContainer) {
            // If the user types a message while the confirmation is active,
            // treat it as feedback and retry the query generation.
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