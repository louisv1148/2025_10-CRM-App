<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import type { LP, Person, Note, Todo } from "../lib/api";
  import { fetchLPPeople, fetchLPNotes, fetchLPTasks, updateLP } from "../lib/api";
  import NoteDetailCard from "./NoteDetailCard.svelte";
  import PersonDetailCard from "./PersonDetailCard.svelte";

  export let lp: LP;

  const dispatch = createEventDispatcher();

  let isEditing = false;
  let editedLP: LP = { ...lp };

  let showPeople = false;
  let showNotes = false;
  let showTasks = false;

  let people: Person[] = [];
  let notes: Note[] = [];
  let tasks: Todo[] = [];
  let lastContact: string = "-";
  let loading = true;

  let selectedNote: Note | null = null;
  let showNoteDetail = false;
  let selectedPerson: Person | null = null;
  let showPersonDetail = false;

  onMount(async () => {
    if (!lp.id) return;

    try {
      // Fetch all related data in parallel
      const [fetchedPeople, fetchedNotes, fetchedTasks] = await Promise.all([
        fetchLPPeople(lp.id),
        fetchLPNotes(lp.id),
        fetchLPTasks(lp.id)
      ]);

      people = fetchedPeople;
      tasks = fetchedTasks;

      // Filter notes to only show those with actual content (not just dates)
      notes = fetchedNotes.filter(note => {
        return note.summary || note.raw_notes || note.content_text;
      });

      // Calculate last contact from notes (use all notes including date-only for last contact)
      if (fetchedNotes.length > 0) {
        const sortedNotes = fetchedNotes.sort((a, b) => {
          const dateA = a.date ? new Date(a.date).getTime() : 0;
          const dateB = b.date ? new Date(b.date).getTime() : 0;
          return dateB - dateA;
        });
        const latestNote = sortedNotes[0];
        if (latestNote.date) {
          lastContact = new Date(latestNote.date).toLocaleDateString();
        }
      }
    } catch (err) {
      console.error("Failed to fetch LP details:", err);
    } finally {
      loading = false;
    }
  });

  function close() {
    dispatch("close");
  }

  function handleEdit() {
    isEditing = true;
    editedLP = { ...lp };
  }

  function cancelEdit() {
    isEditing = false;
    editedLP = { ...lp };
  }

  async function saveEdit() {
    if (!lp.id) return;
    try {
      const updated = await updateLP(lp.id, editedLP);
      lp = updated;
      isEditing = false;
      dispatch("updated", updated);
    } catch (err) {
      console.error("Failed to update LP:", err);
      alert("Failed to update LP");
    }
  }

  function handleDelete() {
    if (confirm(`Are you sure you want to delete ${lp.name}?`)) {
      dispatch("delete", lp.id);
    }
  }

  function formatNumber(num: number | undefined): string {
    if (!num) return "-";
    return `$${num}B`;
  }

  function formatRange(low: number | undefined, high: number | undefined): string {
    if (!low && !high) return "-";
    if (!low) return `Up to $${high}M`;
    if (!high) return `From $${low}M`;
    return `$${low}M - $${high}M`;
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  function openNoteDetail(note: Note) {
    selectedNote = note;
    showNoteDetail = true;
  }

  function closeNoteDetail() {
    selectedNote = null;
    showNoteDetail = false;
  }

  function openPersonDetail(person: Person) {
    selectedPerson = person;
    showPersonDetail = true;
  }

  function closePersonDetail() {
    selectedPerson = null;
    showPersonDetail = false;
  }
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-card" on:click|stopPropagation>
    <div class="card-header">
      <h2>{lp.name}</h2>
      <div class="actions">
        {#if isEditing}
          <button class="action-btn save" on:click={saveEdit}>Save</button>
          <button class="action-btn cancel" on:click={cancelEdit}>Cancel</button>
        {:else}
          <button class="action-btn edit" on:click={handleEdit}>Edit</button>
          <button class="action-btn delete" on:click={handleDelete}>Delete</button>
        {/if}
        <button class="action-btn close" on:click={close}>✕</button>
      </div>
    </div>

    <div class="card-body">
      <!-- Main Information Section -->
      <div class="info-section">
        <div class="info-grid">
          <div class="info-item">
            <label>Type of Group</label>
            <div class="value">{lp.type_of_group || "-"}</div>
          </div>

          <div class="info-item">
            <label>Priority</label>
            {#if isEditing}
              <input type="text" bind:value={editedLP.priority} placeholder="Priority" />
            {:else}
              <div class="value priority">{lp.priority || "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Location</label>
            {#if isEditing}
              <input type="text" bind:value={editedLP.location} placeholder="Location" />
            {:else}
              <div class="value">{lp.location || "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>AUM</label>
            <div class="value">{formatNumber(lp.aum_billions)}</div>
          </div>

          <div class="info-item">
            <label>Ticket Range</label>
            <div class="value">{formatRange(lp.investment_low, lp.investment_high)}</div>
          </div>

          <div class="info-item">
            <label>Advisor</label>
            <div class="value">{lp.advisor || "-"}</div>
          </div>

          <div class="info-item">
            <label>Last Contact</label>
            <div class="value">{lastContact}</div>
          </div>
        </div>

        <div class="interests-section">
          <h4>Interests</h4>
          <div class="interests-grid">
            <div class="interest-item">
              <label>Local MF</label>
              <div class="value">{lp.local_mf || "-"}</div>
            </div>
            <div class="interest-item">
              <label>Local Alts</label>
              <div class="value">{lp.local_alts || "-"}</div>
            </div>
            <div class="interest-item">
              <label>Intl MF</label>
              <div class="value">{lp.intl_mf || "-"}</div>
            </div>
            <div class="interest-item">
              <label>Intl Alts</label>
              <div class="value">{lp.intl_alts || "-"}</div>
            </div>
          </div>
        </div>

        {#if lp.text}
          <div class="description-section">
            <h4>Description</h4>
            <div class="description">{lp.text}</div>
          </div>
        {/if}
      </div>

      <!-- Separator Line -->
      <div class="section-divider"></div>

      <!-- Toggle Sections -->
      <div class="toggle-sections">
        <div class="toggle-section">
          <button class="toggle-header" on:click={() => showPeople = !showPeople}>
            <span class="toggle-icon">{showPeople ? '▼' : '▶'}</span>
            <span class="toggle-title">People</span>
            <span class="count-badge">{people.length}</span>
          </button>
          {#if showPeople}
            <div class="toggle-content">
              {#if people.length === 0}
                <p class="empty-state">No people linked yet</p>
              {:else}
                <div class="list-items">
                  {#each people as person}
                    <div class="list-item clickable" on:click={() => openPersonDetail(person)}>
                      <div class="item-name">{person.name}</div>
                      {#if person.position}
                        <div class="item-detail">{person.position}</div>
                      {/if}
                      {#if person.email}
                        <div class="item-detail">{person.email}</div>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        </div>

        <div class="toggle-section">
          <button class="toggle-header" on:click={() => showNotes = !showNotes}>
            <span class="toggle-icon">{showNotes ? '▼' : '▶'}</span>
            <span class="toggle-title">Notes</span>
            <span class="count-badge">{notes.length}</span>
          </button>
          {#if showNotes}
            <div class="toggle-content">
              {#if notes.length === 0}
                <p class="empty-state">No notes linked yet</p>
              {:else}
                <div class="list-items">
                  {#each notes as note}
                    <div class="list-item clickable" on:click={() => openNoteDetail(note)}>
                      <div class="note-title-row">
                        <div class="note-date">{note.date ? formatDate(note.date) : 'No date'}</div>
                        {#if note.interest}
                          <span class="interest-badge">{note.interest}</span>
                        {/if}
                      </div>
                      {#if note.name}
                        <div class="note-name">{note.name}</div>
                      {/if}
                      {#if note.summary}
                        <div class="item-summary">{note.summary}</div>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        </div>

        <div class="toggle-section">
          <button class="toggle-header" on:click={() => showTasks = !showTasks}>
            <span class="toggle-icon">{showTasks ? '▼' : '▶'}</span>
            <span class="toggle-title">Tasks</span>
            <span class="count-badge">{tasks.length}</span>
          </button>
          {#if showTasks}
            <div class="toggle-content">
              {#if tasks.length === 0}
                <p class="empty-state">No tasks linked yet</p>
              {:else}
                <div class="list-items">
                  {#each tasks as task}
                    <div class="list-item">
                      <div class="item-header">
                        <div class="item-name">{task.description}</div>
                        <span class="status-badge {task.status}">{task.status || 'pending'}</span>
                      </div>
                      {#if task.due_date}
                        <div class="item-detail">Due: {formatDate(task.due_date)}</div>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

{#if showNoteDetail && selectedNote}
  <NoteDetailCard note={selectedNote} on:close={closeNoteDetail} />
{/if}

{#if showPersonDetail && selectedPerson}
  <PersonDetailCard person={selectedPerson} on:close={closePersonDetail} />
{/if}

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
    max-width: 800px;
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

  .action-btn.edit {
    background: #3498db;
    color: white;
  }

  .action-btn.edit:hover {
    background: #2980b9;
  }

  .action-btn.delete {
    background: #e74c3c;
    color: white;
  }

  .action-btn.delete:hover {
    background: #c0392b;
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

  .info-item .value.priority {
    color: #e74c3c;
    font-weight: 600;
  }

  .interests-section {
    margin-bottom: 2rem;
  }

  .interests-section h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .interests-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .interest-item label {
    display: block;
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.25rem;
  }

  .interest-item .value {
    font-size: 0.95rem;
    color: #555;
  }

  .description-section {
    margin-top: 2rem;
  }

  .description-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .description {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    color: #555;
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .section-divider {
    height: 2px;
    background: linear-gradient(to right, #e0e0e0 0%, #f0f0f0 100%);
    margin: 2rem 0;
  }

  .toggle-sections {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .toggle-section {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
  }

  .toggle-header {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #f8f9fa;
    border: none;
    cursor: pointer;
    transition: background 0.2s;
  }

  .toggle-header:hover {
    background: #e9ecef;
  }

  .toggle-icon {
    font-size: 0.8rem;
    color: #666;
  }

  .toggle-title {
    flex: 1;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    font-size: 1rem;
  }

  .count-badge {
    background: #3498db;
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: bold;
  }

  .toggle-content {
    padding: 1.5rem;
    background: white;
    border-top: 1px solid #e0e0e0;
  }

  .empty-state {
    color: #999;
    font-style: italic;
    text-align: center;
    margin: 0;
  }

  .list-items {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .list-item {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    border-left: 3px solid #3498db;
  }

  .list-item.clickable {
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
  }

  .list-item.clickable:hover {
    background: #e9ecef;
    transform: translateX(2px);
  }

  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .item-name {
    font-weight: 600;
    color: #2c3e50;
  }

  .item-detail {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.25rem;
  }

  .item-summary {
    font-size: 0.9rem;
    color: #555;
    margin-top: 0.5rem;
    line-height: 1.5;
  }

  .interest-badge,
  .status-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .interest-badge {
    background: #e8f4f8;
    color: #3498db;
  }

  .status-badge {
    background: #fff3cd;
    color: #856404;
  }

  .status-badge.completed {
    background: #d4edda;
    color: #155724;
  }

  .status-badge.pending {
    background: #f8d7da;
    color: #721c24;
  }

  .note-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .note-date {
    font-size: 0.85rem;
    color: #666;
    font-weight: 500;
  }

  .note-name {
    font-weight: 600;
    color: #2c3e50;
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }

  /* Edit mode styles */
  .info-item input,
  .description-section textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.2s;
  }

  .info-item input:focus,
  .description-section textarea:focus {
    outline: none;
    border-color: #3498db;
  }

  .description-section textarea {
    min-height: 100px;
    resize: vertical;
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
