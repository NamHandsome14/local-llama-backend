document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    
    // Generate a session ID for this tab
    const sessionId = 'session-' + Math.random().toString(36).substr(2, 9);
    
    // Chat history storage
    let conversationHistory = [];

    // Focus input on load
    userInput.focus();

    // Function to create and append a message bubble
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        scrollToBottom();
        return messageDiv;
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

        // 1. Add User Message to UI and History
        addMessage(text, 'user');
        conversationHistory.push({ role: "user", content: text });
        
        // 2. Clear input and disable
        userInput.value = '';
        setInputState(false);

        // 3. Create AI message bubble immediately
        const messageDiv = addMessage('', 'ai');
        let fullResponse = "";

        try {
            // 4. Call Backend API
            const response = await fetch('http://localhost:8000/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: conversationHistory,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                const errText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errText}`);
            }

            // 5. Handle Streaming Response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                if (chunk) {
                    fullResponse += chunk;
                    messageDiv.textContent = fullResponse;
                    scrollToBottom();
                }
            }

            // 6. Add AI response to history
            conversationHistory.push({ role: "assistant", content: fullResponse });

        } catch (error) {
            console.error('Error:', error);
            messageDiv.classList.add('error');
            messageDiv.textContent = `Error: ${error.message}`;
            // Remove failed user message from history so we can retry? 
            // Or just keep it. For now, we leave it.
        } finally {
            // 7. Re-enable input
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
