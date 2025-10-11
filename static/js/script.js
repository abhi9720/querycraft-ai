document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chat-history');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Function to add a message to the chat history
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

    // Function to handle sending a message
    async function sendMessage() {
        const prompt = userInput.value.trim();
        if (prompt === '') return;

        addMessage('user', prompt);
        userInput.value = '';

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });

            const data = await response.json();

            if (response.ok) {
                if (data.sql) {
                    const formattedSql = `<pre><code>${data.sql}</code></pre>`;
                    addMessage('bot', formattedSql, true);
                }
                if (data.explanation) {
                    addMessage('bot', data.explanation, true);
                }
            } else {
                // If the response is not OK, it's an error
                let errorMessage = data.error || 'Sorry, something went wrong.';
                if (data.description) {
                    errorMessage += `<br><pre>${data.description}</pre>`;
                }
                addMessage('bot', errorMessage, true);
            }
            
        } catch (error) {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, something went wrong. Please try again.');
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Initial bot message
    addMessage('bot', 'Hey Jeffrey, ask me a question, and I can help you by generating a first-draft query.');
});