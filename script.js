document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Focus input on load
    userInput.focus();

    // Function to create and append a message bubble
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    // Function to add a typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'ai', 'typing-indicator');
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        chatBox.appendChild(typingDiv);
        scrollToBottom();
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function setInputState(enabled) {
        userInput.disabled = !enabled;
        sendBtn.disabled = !enabled;
        if (enabled) {
            userInput.focus();
        }
    }

    // Handle sending message
    async function handleSend() {
        const text = userInput.value.trim();
        if (!text) return;

        // 1. Add User Message
        addMessage(text, 'user');
        
        // 2. Clear input and disable
        userInput.value = '';
        setInputState(false);

        // 3. Show typing indicator
        addTypingIndicator();

        try {
            // 4. Call Backend API
            const response = await fetch('http://localhost:8000/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: text
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            // 5. Remove typing indicator and show response
            removeTypingIndicator();
            addMessage(data.answer, 'ai');

        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage(`Error: Could not connect to the AI. ${error.message}`, 'ai error');
        } finally {
            // 6. Re-enable input
            setInputState(true);
        }
    }

    // Event Listeners
    sendBtn.addEventListener('click', handleSend);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
});
