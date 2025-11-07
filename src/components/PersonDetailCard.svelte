<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { Person } from "../lib/api";
  import { updatePerson } from "../lib/api";

  export let person: Person;

  const dispatch = createEventDispatcher();

  let isEditing = false;
  let editedPerson: Person = { ...person };

  function close() {
    dispatch("close");
  }

  function handleEdit() {
    isEditing = true;
    editedPerson = { ...person };
  }

  function cancelEdit() {
    isEditing = false;
    editedPerson = { ...person };
  }

  async function saveEdit() {
    if (!person.id) return;
    try {
      const updated = await updatePerson(person.id, editedPerson);
      person = updated;
      isEditing = false;
      dispatch("updated", updated);
    } catch (err) {
      console.error("Failed to update person:", err);
      alert("Failed to update person");
    }
  }
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-card" on:click|stopPropagation>
    <div class="card-header">
      <h2>{person.name}</h2>
      <div class="actions">
        {#if isEditing}
          <button class="action-btn save" on:click={saveEdit}>Save</button>
          <button class="action-btn cancel" on:click={cancelEdit}>Cancel</button>
        {:else}
          <button class="action-btn edit" on:click={handleEdit}>Edit</button>
        {/if}
        <button class="action-btn close" on:click={close}>✕</button>
      </div>
    </div>

    <div class="card-body">
      <!-- Main Information Section -->
      <div class="info-section">
        <div class="info-grid">
          {#if isEditing || person.position}
            <div class="info-item">
              <label>Position</label>
              {#if isEditing}
                <input type="text" bind:value={editedPerson.position} placeholder="Position" />
              {:else}
                <div class="value">{person.position}</div>
              {/if}
            </div>
          {/if}

          {#if isEditing || person.role}
            <div class="info-item">
              <label>Role</label>
              {#if isEditing}
                <input type="text" bind:value={editedPerson.role} placeholder="Role" />
              {:else}
                <div class="value">{person.role}</div>
              {/if}
            </div>
          {/if}

          {#if isEditing || person.people_type}
            <div class="info-item">
              <label>Type</label>
              {#if isEditing}
                <input type="text" bind:value={editedPerson.people_type} placeholder="Type" />
              {:else}
                <div class="value">{person.people_type}</div>
              {/if}
            </div>
          {/if}

          {#if isEditing || person.org_type}
            <div class="info-item">
              <label>Organization Type</label>
              {#if isEditing}
                <input type="text" bind:value={editedPerson.org_type} placeholder="Organization Type" />
              {:else}
                <div class="value">{person.org_type}</div>
              {/if}
            </div>
          {/if}

          {#if isEditing || person.location}
            <div class="info-item">
              <label>Location</label>
              {#if isEditing}
                <input type="text" bind:value={editedPerson.location} placeholder="Location" />
              {:else}
                <div class="value">{person.location}</div>
              {/if}
            </div>
          {/if}

          {#if isEditing || person.email}
            <div class="info-item">
              <label>Email</label>
              {#if isEditing}
                <input type="email" bind:value={editedPerson.email} placeholder="Email" />
              {:else}
                <div class="value">{person.email}</div>
              {/if}
            </div>
          {/if}

          {#if isEditing || person.phone}
            <div class="info-item">
              <label>Phone</label>
              {#if isEditing}
                <input type="tel" bind:value={editedPerson.phone} placeholder="Phone" />
              {:else}
                <div class="value">{person.phone}</div>
              {/if}
            </div>
          {/if}

          {#if person.cell_phone}
            <div class="info-item">
              <label>Cell Phone</label>
              <div class="value">{person.cell_phone}</div>
            </div>
          {/if}

          {#if person.office_phone}
            <div class="info-item">
              <label>Office Phone</label>
              <div class="value">{person.office_phone}</div>
            </div>
          {/if}
        </div>

        {#if person.personal_note}
          <div class="notes-section">
            <h4>Personal Notes</h4>
            <div class="notes">{person.personal_note}</div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
  }

  .modal-card {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 700px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    border-bottom: 2px solid #e0e0e0;
    background: #f8f9fa;
  }

  h2 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .action-btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .action-btn.close {
    background: #95a5a6;
    color: white;
    font-size: 1.2rem;
    padding: 0.5rem 0.75rem;
  }

  .action-btn.close:hover {
    background: #7f8c8d;
  }

  .card-body {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
  }

  .info-section {
    margin-bottom: 1.5rem;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .info-item label {
    display: block;
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .info-item .value {
    font-size: 1rem;
    color: #2c3e50;
    font-weight: 500;
  }

  .notes-section {
    margin-top: 2rem;
  }

  .notes-section h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .notes {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    color: #555;
    line-height: 1.6;
    white-space: pre-wrap;
  }

  /* Edit mode styles */
  .info-item input,
  .notes-section textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.2s;
  }

  .info-item input:focus,
  .notes-section textarea:focus {
    outline: none;
    border-color: #3498db;
  }

  .notes-section textarea {
    min-height: 100px;
    resize: vertical;
  }

  .action-btn.edit {
    background: #3498db;
    color: white;
  }

  .action-btn.edit:hover {
    background: #2980b9;
  }

  .action-btn.save {
    background: #27ae60;
    color: white;
  }

  .action-btn.save:hover {
    background: #229954;
  }

  .action-btn.cancel {
    background: #95a5a6;
    color: white;
  }

  .action-btn.cancel:hover {
    background: #7f8c8d;
  }
</style>
