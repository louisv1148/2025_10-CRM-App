<script lang="ts">
  import { selectedLPs, selectedParticipants, lps } from "../lib/stores";
  import { searchLPs, createLP, searchPeople, createPerson, type LP, type Person } from "../lib/api";

  let lpSearchQuery = "";
  let lpSearchResults: LP[] = [];
  let lpShowDropdown = false;
  let lpSearchTimeout: ReturnType<typeof setTimeout>;
  let selectedLPObjects: LP[] = [];

  let newLPName = "";

  // Reactive: Update selectedLPObjects when selectedLPs changes
  $: {
    selectedLPObjects = $selectedLPs
      .map(id => $lps.find(lp => lp.id === id))
      .filter((lp): lp is LP => lp !== undefined);
  }

  function removeLP(lpId: number | undefined) {
    if (lpId) {
      $selectedLPs = $selectedLPs.filter(id => id !== lpId);
    }
  }

  // Participants
  let participantSearchQuery = "";
  let participantSearchResults: Person[] = [];
  let participantShowDropdown = false;
  let participantSearchTimeout: ReturnType<typeof setTimeout>;
  let participantObjects: Person[] = []; // Local cache of full Person objects
  let newParticipantName = "";

  // LP search-as-you-type
  async function handleLPSearch() {
    clearTimeout(lpSearchTimeout);

    if (lpSearchQuery.trim().length < 2) {
      lpSearchResults = [];
      lpShowDropdown = false;
      return;
    }

    lpSearchTimeout = setTimeout(async () => {
      try {
        lpSearchResults = await searchLPs(lpSearchQuery);
        lpShowDropdown = lpSearchResults.length > 0;
      } catch (err) {
        console.error("LP search failed:", err);
      }
    }, 300);
  }

  function selectLP(lp: LP) {
    if (lp.id && !$selectedLPs.includes(lp.id)) {
      $selectedLPs = [...$selectedLPs, lp.id];
    }
    lpSearchQuery = "";
    lpShowDropdown = false;
  }

  function clearLPSearch() {
    lpSearchQuery = "";
    lpSearchResults = [];
    lpShowDropdown = false;
  }

  async function addLP() {
    if (newLPName.trim()) {
      await createLP({ name: newLPName.trim() });
      newLPName = "";
    }
  }

  // Participant search-as-you-type
  async function handleParticipantSearch() {
    clearTimeout(participantSearchTimeout);

    if (participantSearchQuery.trim().length < 2) {
      participantSearchResults = [];
      participantShowDropdown = false;
      return;
    }

    participantSearchTimeout = setTimeout(async () => {
      try {
        participantSearchResults = await searchPeople(participantSearchQuery);
        participantShowDropdown = participantSearchResults.length > 0;
      } catch (err) {
        console.error("Participant search failed:", err);
      }
    }, 300);
  }

  function selectParticipant(person: Person) {
    if (person.id && !$selectedParticipants.includes(person.id)) {
      $selectedParticipants = [...$selectedParticipants, person.id];
      participantObjects = [...participantObjects, person];
    }
    participantSearchQuery = "";
    participantShowDropdown = false;
  }

  function removeParticipant(personId: number | undefined) {
    if (personId) {
      $selectedParticipants = $selectedParticipants.filter(id => id !== personId);
      participantObjects = participantObjects.filter(p => p.id !== personId);
    }
  }

  async function addParticipant() {
    if (newParticipantName.trim() && $selectedLPs.length > 0) {
      try {
        const newPerson = await createPerson({
          name: newParticipantName.trim(),
          role: "LP",
          org_type: "lp",
          org_id: $selectedLPs[0]  // Associate with first selected LP
        });
        if (newPerson.id) {
          $selectedParticipants = [...$selectedParticipants, newPerson.id];
          participantObjects = [...participantObjects, newPerson];
        }
        newParticipantName = "";
      } catch (err) {
        console.error("Failed to create participant:", err);
      }
    }
  }
</script>

<section class="lp-section">
  <h3>Limited Partner</h3>

  <div class="search-group">
    <div class="search-input-wrapper">
      <input
        type="text"
        placeholder="Search and select LPs..."
        bind:value={lpSearchQuery}
        on:input={handleLPSearch}
        on:focus={() => lpShowDropdown = lpSearchResults.length > 0}
        on:blur={() => setTimeout(() => lpShowDropdown = false, 200)}
      />
      {#if lpSearchQuery}
        <button class="clear-btn" on:click={clearLPSearch}>✕</button>
      {/if}
    </div>

    {#if lpShowDropdown}
      <div class="dropdown">
        {#each lpSearchResults as lp}
          <div class="dropdown-item" on:click={() => selectLP(lp)}>
            {lp.name}
          </div>
        {/each}
      </div>
    {/if}
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

  <!-- Selected LPs Display -->
  {#if selectedLPObjects.length > 0}
    <div class="selected-list">
      {#each selectedLPObjects as lp}
        <div class="selected-item">
          <span class="participant-name">{lp.name}</span>
          <button class="remove-btn" on:click={() => removeLP(lp.id)}>✕</button>
        </div>
      {/each}
    </div>
  {/if}

  <div class="participants">
    <h4>Participants</h4>

    <div class="search-group">
      <div class="search-input-wrapper">
        <input
          type="text"
          placeholder="Search people..."
          bind:value={participantSearchQuery}
          on:input={handleParticipantSearch}
          on:focus={() => participantShowDropdown = participantSearchResults.length > 0}
          on:blur={() => setTimeout(() => participantShowDropdown = false, 200)}
        />
      </div>

      {#if participantShowDropdown}
        <div class="dropdown">
          {#each participantSearchResults as person}
            <div class="dropdown-item" on:click={() => selectParticipant(person)}>
              {person.name}
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <div class="add-group">
      <input
        type="text"
        placeholder="New participant name"
        bind:value={newParticipantName}
        on:keypress={(e) => e.key === "Enter" && addParticipant()}
      />
      <button on:click={addParticipant}>Add</button>
    </div>

    <div class="selected-list">
      {#each participantObjects as participant}
        <div class="selected-item">
          <span class="participant-name">{participant.name}</span>
          <button class="remove-btn" on:click={() => removeParticipant(participant.id)}>✕</button>
        </div>
      {/each}
    </div>
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

  .search-group {
    position: relative;
    margin-bottom: 1rem;
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  input[type="text"] {
    width: 100%;
    padding: 0.5rem;
    padding-right: 2rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  input[type="text"]:focus {
    outline: none;
    border-color: #3498db;
  }

  .clear-btn {
    position: absolute;
    right: 0.5rem;
    background: transparent;
    border: none;
    color: #999;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.25rem;
  }

  .clear-btn:hover {
    color: #666;
  }

  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-top: none;
    border-radius: 0 0 4px 4px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .dropdown-item {
    padding: 0.5rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .dropdown-item:hover {
    background: #f5f5f5;
  }


  .add-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .add-group input {
    flex: 1;
  }

  .add-group button {
    background: #3498db;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .add-group button:hover {
    background: #2980b9;
  }

  .participants {
    margin-top: 1.5rem;
  }

  .selected-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .selected-item {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    background: #f8f8f8;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .participant-name {
    flex: 1;
    font-weight: 500;
    color: #2c3e50;
  }


  .remove-btn {
    background: transparent;
    border: none;
    color: #3498db;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.25rem;
    line-height: 1;
  }

  .remove-btn:hover {
    color: #2980b9;
  }
</style>
