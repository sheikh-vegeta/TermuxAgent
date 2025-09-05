<template>
  <div class="chat-page">
    <div class="chat-container" ref="chatContainer">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :message="msg" />
    </div>
    <ChatInput @send="sendMessage" :is-loading="isLoading" />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import ChatMessage from '../components/ChatMessage.vue';
import ChatInput from '../components/ChatInput.vue';

const messages = ref([]);
const isLoading = ref(false);
const chatContainer = ref(null);

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
};

// Function to handle sending messages to the backend
const sendMessage = async (text) => {
  if (text.trim() === '' || isLoading.value) return;

  isLoading.value = true;
  messages.value.push({ id: Date.now(), author: 'user', text });
  scrollToBottom();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Backend request failed');
    }
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({
      id: Date.now(),
      author: 'system',
      text: `<strong>Error:</strong> Could not send message to the backend. ${error.message}`,
    });
    isLoading.value = false;
  }
  // The result will be displayed via the SSE stream, so we don't need to handle it here.
  // The isLoading flag is reset by the SSE handler when a result or error arrives.
};

// Setup Server-Sent Events (SSE) listener
onMounted(() => {
  messages.value.push({ id: Date.now(), author: 'system', text: 'Connecting to agent...'});
  const eventSource = new EventSource('/sse');

  eventSource.onopen = () => {
    messages.value.push({ id: Date.now(), author: 'system', text: 'Connection established. Ready for commands.'});
  };

  eventSource.onmessage = (event) => {
    const eventData = JSON.parse(event.data);
    let message = {};

    let outputHtml = '';
    switch (eventData.type) {
        case 'status':
            message = { id: Date.now(), author: 'system', text: eventData.data };
            // Don't set isLoading for every status, only for the final result/error
            break;

        case 'plan':
            outputHtml = `<h4>Research Plan:</h4><ol>`;
            eventData.data.forEach(step => {
                outputHtml += `<li>${step}</li>`;
            });
            outputHtml += `</ol>`;
            message = { id: Date.now(), author: 'agent', text: outputHtml };
            isLoading.value = true; // Research has started
            break;

        case 'plan_step_result':
            const stepResult = eventData.data;
            outputHtml = `<details><summary><strong>Step ${eventData.step} Results:</strong> ${stepResult.results.length} found</summary>`;
            if (stepResult.status === 'success' && stepResult.results.length > 0) {
                outputHtml += '<ul>';
                stepResult.results.forEach(res => {
                    outputHtml += `<li><a href="${res.link}" target="_blank">${res.title}</a><p>${res.snippet}</p></li>`;
                });
                outputHtml += '</ul>';
            } else {
                outputHtml += `<p>No results found or an error occurred: ${stepResult.message || ''}</p>`;
            }
            outputHtml += `</details>`;
            message = { id: Date.now(), author: 'agent', text: outputHtml };
            break;

        case 'final_report':
            // Using a library like 'marked' would be better for production
            // but for now, we can just replace newlines with <br>
            const reportText = eventData.data.replace(/\n/g, '<br>');
            outputHtml = `<div class="final-report"><h4>Final Report</h4>${reportText}</div>`;
            message = { id: Date.now(), author: 'agent', text: outputHtml };
            isLoading.value = false; // Research is finished
            break;

        case 'result': // This is for single tool_use mode
            const resultData = eventData.data;
            const toolName = eventData.tool_name;
            if (toolName === 'shell') {
                outputHtml = `<details open><summary><strong>Shell Result (Code: ${resultData.returncode})</strong></summary>`;
                outputHtml += `<p><strong>Command:</strong> <code>${resultData.command}</code></p>`;
                if (resultData.stdout) outputHtml += `<strong>STDOUT:</strong><pre>${resultData.stdout}</pre>`;
                if (resultData.stderr) outputHtml += `<strong>STDERR:</strong><pre>${resultData.stderr}</pre>`;
                outputHtml += `</details>`;
            } else if (toolName === 'google_search') {
                outputHtml = `<details open><summary><strong>Google Search Results</strong></summary>`;
                if (resultData.status === 'success' && resultData.results.length > 0) {
                    outputHtml += '<ul>';
                    resultData.results.forEach(res => {
                        outputHtml += `<li><a href="${res.link}" target="_blank">${res.title}</a><p>${res.snippet}</p></li>`;
                    });
                    outputHtml += '</ul>';
                } else {
                    outputHtml += `<p>No results found or an error occurred: ${resultData.message || ''}</p>`;
                }
                outputHtml += `</details>`;
            } else {
                outputHtml = `<details open><summary><strong>Tool Result</strong></summary><pre>${JSON.stringify(resultData, null, 2)}</pre></details>`;
            }
            message = { id: Date.now(), author: 'agent', text: outputHtml };
            isLoading.value = false;
            break;

        case 'error':
            message = { id: Date.now(), author: 'system', text: `<strong>Backend Error:</strong> ${eventData.data}` };
            isLoading.value = false;
            break;

        default:
            console.warn("Unknown SSE event type:", eventData);
            message = { id: Date.now(), author: 'system', text: `Unknown event: ${event.data}` };
    }

    messages.value.push(message);
    scrollToBottom();
  };

  eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    messages.value.push({ id: Date.now(), author: 'system', text: '<strong>Connection to server lost.</strong> Please refresh the page to reconnect.' });
    eventSource.close();
    isLoading.value = false;
  };
});
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chat-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid #333;
  margin-bottom: 1rem;
}
</style>

<style>
/* Global styles for chat output formatting */
pre {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 0.75rem;
  border-radius: 6px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9em;
}
code {
    background-color: #333;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Courier New', Courier, monospace;
}
details {
    border: 1px solid #444;
    border-radius: 6px;
    padding: 0.5rem;
    margin-top: 0.5rem;
}
summary {
    cursor: pointer;
    font-weight: bold;
}
ul {
    list-style-type: none;
    padding-left: 0;
}
li {
    border-bottom: 1px solid #444;
    padding: 0.5rem 0;
}
li:last-child {
    border-bottom: none;
}
li a {
    color: #8bf;
    text-decoration: none;
}
li a:hover {
    text-decoration: underline;
}
li p {
    margin: 0.25rem 0 0 0;
    font-size: 0.9em;
    color: #ccc;
}
ol {
    padding-left: 20px;
}
.final-report {
    border: 1px solid #00aae4;
    border-radius: 8px;
    padding: 1rem;
    background-color: #2d2d30;
}
.final-report h4 {
    margin-top: 0;
    color: #00aae4;
}
</style>
