document.addEventListener('DOMContentLoaded', () => {
    // --- API Key Management ---
    const apiKeyInput = document.getElementById('apiKey');
    const saveApiKeyButton = document.getElementById('saveApiKey');

    // Load API key from localStorage on page load
    const loadApiKey = () => {
        const savedKey = localStorage.getItem('termuxAgentApiKey');
        if (savedKey) {
            apiKeyInput.value = savedKey;
        }
    };

    // Save API key to localStorage
    const saveApiKey = () => {
        localStorage.setItem('termuxAgentApiKey', apiKeyInput.value);
        alert('API Key saved!');
    };

    saveApiKeyButton.addEventListener('click', saveApiKey);
    loadApiKey();

    // --- Page-specific logic ---
    const isChatPage = !!document.getElementById('chat-window');
    const isTerminalPage = !!document.getElementById('terminal-container');

    // --- Chat Page Logic ---
    if (isChatPage) {
        const sendButton = document.getElementById('send-button');
        const messageInput = document.getElementById('message-input');
        const chatHistory = document.getElementById('chat-history');
        let conversationHistory = [];

        const addMessageToHistory = (sender, message) => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', `${sender}-message`);
            // Basic markdown for code blocks
            message = message.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
            messageElement.innerHTML = `<p>${message}</p>`;
            chatHistory.appendChild(messageElement);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        };

        const sendChatMessage = async () => {
            const message = messageInput.value.trim();
            const apiKey = apiKeyInput.value;

            if (!message) return;
            if (!apiKey) {
                alert('Please enter your API key.');
                return;
            }

            addMessageToHistory('user', message);
            messageInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey,
                    },
                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory,
                    }),
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || `HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                conversationHistory = data.history;
                addMessageToHistory('ai', data.reply);

            } catch (error) {
                addMessageToHistory('error', `Error: ${error.message}`);
            }
        };

        sendButton.addEventListener('click', sendChatMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }

    // --- Terminal Page Logic ---
    if (isTerminalPage) {
        const term = new Terminal({
            cursorBlink: true,
            convertEol: true,
            theme: {
                background: '#000000',
                foreground: '#00FF00',
            }
        });
        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);
        const terminalContainer = document.getElementById('terminal-container');
        term.open(terminalContainer);
        fitAddon.fit();
        window.addEventListener('resize', () => fitAddon.fit());

        const executeButton = document.getElementById('execute-button');
        const commandInput = document.getElementById('command-input');
        const inVmCheckbox = document.getElementById('in-vm');

        const executeCommand = async () => {
            const command = commandInput.value.trim();
            const inVm = inVmCheckbox.checked;
            const apiKey = apiKeyInput.value;

            if (!command) return;
            if (!apiKey) {
                alert('Please enter your API key.');
                return;
            }

            term.writeln(`\r\n$ ${command}`);
            commandInput.value = '';

            try {
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey,
                    },
                    body: JSON.stringify({
                        command: command,
                        in_vm: inVm,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        break;
                    }
                    term.write(decoder.decode(value, { stream: true }));
                }

            } catch (error) {
                term.writeln(`\r\n\x1b[31mError: ${error.message}\x1b[0m`);
            }
        };

        executeButton.addEventListener('click', executeCommand);
        commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeCommand();
            }
        });
    }
});
