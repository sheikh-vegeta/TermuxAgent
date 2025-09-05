<template>
  <div class="chat-page">
    <div class="chat-container">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :message="msg" />
    </div>
    <ChatInput @send="sendMessage" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'

const messages = ref([])

// Function to handle sending messages
const sendMessage = (text) => {
  if (text.trim() === '') return;
  messages.value.push({ id: Date.now(), author: 'user', text: text });
  // Here you would send the message to the backend API
  // e.g., fetch('/api/chat', { method: 'POST', ... })

  // Dummy response for demonstration
  setTimeout(() => {
    messages.value.push({ id: Date.now(), author: 'agent', text: `Received: "${text}"` });
  }, 1000);
}

// Setup Server-Sent Events (SSE) listener
onMounted(() => {
  const eventSource = new EventSource('/sse'); // Connects to the FastAPI backend

  eventSource.onmessage = (event) => {
    // Add server events to the chat history
    messages.value.push({ id: Date.now(), author: 'system', text: event.data });
  };

  eventSource.onerror = (error) => {
    console.error("SSE Error:", error);
    messages.value.push({ id: Date.now(), author: 'system', text: 'Connection to server lost.' });
    eventSource.close();
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
