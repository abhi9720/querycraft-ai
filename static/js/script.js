document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    let conversationState = { prompt: '' };

    function addMessage(sender, message, isHtml = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);

        const avatar = document.createElement('img');
        avatar.classList.add('avatar');
        avatar.src = sender === 'user' ? 'https://img.icons8.com/color/48/000000/user-male-circle.png' : 'https://img.icons8.com/fluency/48/000000/bot.png';
        
        const content = document.createElement('div');
        content.classList.add('content');
        if (isHtml) {
            content.innerHTML = message;
        } else {
            content.textContent = message;
        }

        messageElement.appendChild(avatar);
        messageElement.appendChild(content);
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function addConfirmation(tables) {
        const tablesList = `<ul>${tables.map(t => `<li>${t}</li>`).join('')}</ul>`;
        const confirmationHtml = `<div>To answer that, I believe I need to use the following tables. Is this correct?</div>${tablesList}`;
        addMessage('bot', confirmationHtml, true);

        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('confirmation-buttons');
        
        const yesBtn = document.createElement('button');
        yesBtn.textContent = 'Yes';
        yesBtn.onclick = () => handleConfirmation(true, tables);
        
        const noBtn = document.createElement('button');
        noBtn.textContent = 'No';
        noBtn.onclick = () => handleConfirmation(false);

        buttonContainer.appendChild(yesBtn);
        buttonContainer.appendChild(noBtn);
        chatHistory.appendChild(buttonContainer);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function handleConfirmation(isCorrect, tables = []) {
        document.querySelector('.confirmation-buttons').remove(); // Remove buttons after click
        if (isCorrect) {
            addMessage('user', 'Yes, that is correct.');
            await sendMessage(conversationState.prompt, tables);
        } else {
            addMessage('user', 'No, that is not correct.');
            addMessage('bot', 'My apologies. Please try rephrasing your question or provide more specific details about the tables I should use.');
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
                    addConfirmation(data.tables);
                } else if (data.sql) {
                    const formattedSql = `<pre><code>${data.sql}</code></pre>`;
                    addMessage('bot', formattedSql, true);
                    if (data.explanation) {
                        addMessage('bot', data.explanation, true);
                    }
                    conversationState = {}; // Reset state after completion
                }
            } else {
                const errorMessage = data.error || 'Sorry, something went wrong.';
                addMessage('bot', errorMessage, true);
                if(data.description) {
                    addMessage('bot', `<pre>${data.description}</pre>`, true);
                }
                conversationState = {}; // Reset state on error
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, something went wrong. Please try again.');
            conversationState = {}; // Reset state on error
        }
    }

    async function handleUserInput() {
        const prompt = userInput.value.trim();
        if (prompt === '') return;

        addMessage('user', prompt);
        userInput.value = '';
        
        conversationState.prompt = prompt;
        await sendMessage(prompt);
    }

    // Initial bot message
    addMessage('bot', 'Hey! I\'m your personal SQL agent. Ask me a question about your data, and I\'ll help you build the right query to answer it.');

    window.handleConfirmation = handleConfirmation; // Make it accessible globally for the button clicks
    sendBtn.addEventListener('click', handleUserInput);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent default behavior
            handleUserInput();
        }
    });
});