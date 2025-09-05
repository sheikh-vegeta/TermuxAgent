<template>
  <div class="chat-input">
    <input
      v-model="inputText"
      @keyup.enter="handleSubmit"
      :placeholder="isLoading ? 'Agent is thinking...' : 'Type your command...'"
      :disabled="isLoading"
    />
    <button @click="handleSubmit" :disabled="isLoading">
      {{ isLoading ? '...' : 'Send' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  isLoading: {
    type: Boolean,
    default: false,
  },
})

const inputText = ref('')
const emit = defineEmits(['send'])

const handleSubmit = () => {
  if (inputText.value.trim()) {
    emit('send', inputText.value)
    inputText.value = ''
  }
}
</script>

<style scoped>
.chat-input {
  display: flex;
  padding: 1rem;
  background-color: #1f1f1f;
  border-top: 1px solid #333;
}
input {
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid #555;
  background-color: #3c3c3c;
  color: #e0e0e0;
  border-radius: 5px;
  margin-right: 1rem;
}
button {
  padding: 0.75rem 1.5rem;
  border: none;
  background-color: #007acc;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background-color: #005f9e;
}
button:disabled, input:disabled {
  background-color: #555;
  cursor: not-allowed;
}
button:disabled:hover {
  background-color: #555;
}
</style>
