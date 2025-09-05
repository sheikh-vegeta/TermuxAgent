<template>
  <aside class="sidebar">
    <h3>Agent Controls</h3>
    <ul>
      <li><button>Start Sandbox</button></li>
      <li><button>Stop Sandbox</button></li>
      <li><button>View Logs</button></li>
    </ul>
  </aside>
</template>

<script setup>
// Placeholder for sidebar logic
</script>

<style scoped>
.sidebar {
  width: 250px;
  padding: 1rem;
  background-color: #1f1f1f;
  border-right: 1px solid #333;
}
h3 {
  margin-top: 0;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  margin-bottom: 0.5rem;
}
button {
  width: 100%;
  padding: 0.5rem;
  background-color: #3a3d41;
  color: #e0e0e0;
  border: 1px solid #555;
  cursor: pointer;
}
button:hover {
  background-color: #4a4d51;
}
</style>
