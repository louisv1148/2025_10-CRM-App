<script lang="ts">
  import { gps, selectedGP } from "../lib/stores";
  import { createGP, fetchGPs } from "../lib/api";

  let newGPName = "";

  async function addGP() {
    if (newGPName.trim()) {
      await createGP({ name: newGPName.trim() });
      $gps = await fetchGPs();
      newGPName = "";
    }
  }
</script>

<section class="gp-section">
  <h3>General Partner</h3>

  <div class="select-group">
    <select bind:value={$selectedGP}>
      <option value={null}>Select GP...</option>
      {#each $gps as gp}
        <option value={gp.id}>{gp.name}</option>
      {/each}
    </select>
  </div>

  <div class="add-group">
    <input
      type="text"
      placeholder="New GP name"
      bind:value={newGPName}
      on:keypress={(e) => e.key === "Enter" && addGP()}
    />
    <button on:click={addGP}>Add</button>
  </div>

  <div class="participants">
    <h4>Participants</h4>
    <p class="placeholder">Participant management coming soon...</p>
  </div>
</section>

<style>
  .gp-section {
    margin-bottom: 1.5rem;
  }

  h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 2px solid #e74c3c;
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
    background: #e74c3c;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  button:hover {
    background: #c0392b;
  }

  .placeholder {
    color: #999;
    font-size: 0.85rem;
    font-style: italic;
  }
</style>
