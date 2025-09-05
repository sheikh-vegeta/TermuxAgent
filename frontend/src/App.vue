<template>
  <div id="main-layout">
    <header>
      <h1>Termux AI Agent</h1>
    </header>
    <main>
      <!-- The ChatPage component will be the primary view -->
      <ChatPage />
    </main>
  </div>
</template>

<script setup>
// This is a placeholder for the ChatPage component which will be created next.
// To make this file valid, we can create a dummy ChatPage component or import it.
// For now, we assume ChatPage will be created.
import ChatPage from './pages/ChatPage.vue'
</script>

<style>
/* Basic layout styles */
#main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #121212;
  color: #e0e0e0;
}
header {
  padding: 1rem;
  background-color: #1f1f1f;
  border-bottom: 1px solid #333;
  text-align: center;
}
main {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
}
</style>
