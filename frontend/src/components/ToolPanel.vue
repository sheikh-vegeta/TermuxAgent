<template>
  <div class="tool-panel">
    <h3>Browser Tool (noVNC)</h3>
    <iframe
      src="http://127.0.0.1:5901"
      width="100%"
      height="400"
      style="border: 1px solid #444;"
    >
    </iframe>
    <p class="help-text">
      This panel streams the sandboxed browser. The backend must be running the VNC and websockify services.
    </p>
  </div>
</template>

<script setup>
// This component is a simple wrapper for the noVNC iframe.
// More advanced logic could be added here to manage the connection state.
</script>

<style scoped>
.tool-panel {
  padding: 1rem;
  background-color: #252526;
  border-radius: 8px;
}
h3 {
  margin-top: 0;
  color: #00aae4;
}
.help-text {
  font-size: 0.9rem;
  color: #888;
  text-align: center;
}
</style>
