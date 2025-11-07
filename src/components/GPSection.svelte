<script lang="ts">
  import { selectedGP, gps } from "../lib/stores";
  import { searchGPs, createGP, searchPeople, createPerson, type GP, type Person } from "../lib/api";

  let gpSearchQuery = "";
  let gpSearchResults: GP[] = [];
  let gpShowDropdown = false;
  let gpSearchTimeout: ReturnType<typeof setTimeout>;
  let selectedGPObject: GP | null = null;

  let newGPName = "";

  // Reactive: Update selectedGPObject when selectedGP changes
  $: if ($selectedGP) {
    const found = $gps.find(gp => gp.id === $selectedGP);
    if (found) {
      selectedGPObject = found;
    }
  } else {
    selectedGPObject = null;
  }

  // Participants
  let participantSearchQuery = "";
  let participantSearchResults: Person[] = [];
  let participantShowDropdown = false;
  let participantSearchTimeout: ReturnType<typeof setTimeout>;
  let selectedParticipants: Person[] = [];
  let newParticipantName = "";

  // GP search-as-you-type
  async function handleGPSearch() {
    clearTimeout(gpSearchTimeout);

    if (gpSearchQuery.trim().length < 2) {
      gpSearchResults = [];
      gpShowDropdown = false;
      return;
    }

    gpSearchTimeout = setTimeout(async () => {
      try {
        gpSearchResults = await searchGPs(gpSearchQuery);
        gpShowDropdown = gpSearchResults.length > 0;
      } catch (err) {
        console.error("GP search failed:", err);
      }
    }, 300);
  }

  function selectGP(gp: GP) {
    $selectedGP = gp.id || null;
    selectedGPObject = gp;
    gpSearchQuery = "";
    gpShowDropdown = false;
  }

  function clearGP() {
    $selectedGP = null;
    gpSearchQuery = "";
    gpSearchResults = [];
  }

  function removeGP() {
    $selectedGP = null;
    selectedGPObject = null;
  }

  async function addGP() {
    if (newGPName.trim()) {
      await createGP({ name: newGPName.trim() });
      newGPName = "";
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
    if (!selectedParticipants.find(p => p.id === person.id)) {
      selectedParticipants = [...selectedParticipants, person];
    }
    participantSearchQuery = "";
    participantShowDropdown = false;
  }

  function removeParticipant(personId: number | undefined) {
    if (personId) {
      selectedParticipants = selectedParticipants.filter(p => p.id !== personId);
    }
  }

  async function addParticipant() {
    if (newParticipantName.trim() && $selectedGP) {
      try {
        const newPerson = await createPerson({
          name: newParticipantName.trim(),
          role: "GP",
          org_type: "gp",
          org_id: $selectedGP
        });
        selectedParticipants = [...selectedParticipants, newPerson];
        newParticipantName = "";
      } catch (err) {
        console.error("Failed to create participant:", err);
      }
    }
  }
</script>

<section class="gp-section">
  <h3>General Partner</h3>

  <div class="search-group">
    <div class="search-input-wrapper">
      <input
        type="text"
        placeholder="Search GP..."
        bind:value={gpSearchQuery}
        on:input={handleGPSearch}
        on:focus={() => gpShowDropdown = gpSearchResults.length > 0}
        on:blur={() => setTimeout(() => gpShowDropdown = false, 200)}
      />
      {#if $selectedGP && gpSearchQuery}
        <button class="clear-btn" on:click={clearGP}>✕</button>
      {/if}
    </div>

    {#if gpShowDropdown}
      <div class="dropdown">
        {#each gpSearchResults as gp}
          <div class="dropdown-item" on:click={() => selectGP(gp)}>
            {gp.name}
          </div>
        {/each}
      </div>
    {/if}
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

  <!-- Selected GP Display -->
  {#if selectedGPObject}
    <div class="selected-list">
      <div class="selected-item">
        <span class="participant-name">{selectedGPObject.name}</span>
        <button class="remove-btn" on:click={removeGP}>✕</button>
      </div>
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
      {#each selectedParticipants as participant}
        <div class="selected-item">
          <span class="participant-name">{participant.name}</span>
          <button class="remove-btn" on:click={() => removeParticipant(participant.id)}>✕</button>
        </div>
      {/each}
    </div>
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
    border-color: #e74c3c;
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
    background: #e74c3c;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .add-group button:hover {
    background: #c0392b;
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
    color: #e74c3c;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.25rem;
    line-height: 1;
  }

  .remove-btn:hover {
    color: #c0392b;
  }
</style>
