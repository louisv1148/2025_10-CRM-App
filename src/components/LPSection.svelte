<script lang="ts">
  import { lps, selectedLP } from "../lib/stores";
  import { createLP, fetchLPs } from "../lib/api";

  let newLPName = "";

  async function addLP() {
    if (newLPName.trim()) {
      await createLP({ name: newLPName.trim() });
      $lps = await fetchLPs();
      newLPName = "";
    }
  }
</script>

<section class="lp-section">
  <h3>Limited Partner</h3>

  <div class="select-group">
    <select bind:value={$selectedLP}>
      <option value={null}>Select LP...</option>
      {#each $lps as lp}
        <option value={lp.id}>{lp.name}</option>
      {/each}
    </select>
  </div>

  <div class="add-group">
    <input
      type="text"
      placeholder="New LP name"
      bind:value={newLPName}
      on:keypress={(e) => e.key === "Enter" && addLP()}
    />
    <button on:click={addLP}>Add</button>
  </div>

  <div class="participants">
    <h4>Participants</h4>
    <p class="placeholder">Participant management coming soon...</p>
  </div>
</section>

<style>
  .lp-section {
    margin-bottom: 1.5rem;
  }

  h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
  }

  h4 {
    font-size: 0.9rem;
    color: #666;
    margin: 1rem 0 0.5rem 0;
  }

  .select-group {
    margin-bottom: 1rem;
  }

  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .add-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  button {
    background: #3498db;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  button:hover {
    background: #2980b9;
  }

  .placeholder {
    color: #999;
    font-size: 0.85rem;
    font-style: italic;
  }
</style>
