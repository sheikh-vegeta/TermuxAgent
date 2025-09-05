<template>
  <div class="chat-message" :class="`message-${message.author}`">
    <strong class="author">{{ message.author }}:</strong>
    <p class="text">{{ message.text }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.chat-message {
  padding: 0.5rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  max-width: 80%;
}
.message-user {
  background-color: #007acc;
  color: white;
  align-self: flex-end;
  margin-left: auto;
}
.message-agent {
  background-color: #3a3d41;
  color: #e0e0e0;
  align-self: flex-start;
}
.message-system {
  background-color: #4a274f;
  color: #e0e0e0;
  align-self: center;
  font-style: italic;
  font-size: 0.9rem;
  text-align: center;
}
.author {
  font-weight: bold;
  margin-right: 0.5rem;
  text-transform: capitalize;
}
p.text {
  margin: 0;
  white-space: pre-wrap;
}
</style>
