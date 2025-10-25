<script lang="ts">
  let count = 0;
</script>

<main>
  <h1>CRM Meeting App - Test</h1>
  <p>Count: {count}</p>
  <button on:click={() => count++}>Increment</button>
</main>

<style>
  main {
    padding: 2rem;
    font-family: Arial, sans-serif;
  }

  h1 {
    color: #2c3e50;
  }

  button {
    background: #3498db;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
</style>
