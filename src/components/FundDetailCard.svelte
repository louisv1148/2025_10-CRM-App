<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import type { Fund, Note } from "../lib/api";
  import { fetchFundNotes, updateFund, fetchGPs, type GP } from "../lib/api";
  import NoteDetailCard from "./NoteDetailCard.svelte";
  import SalesFunnel from "./SalesFunnel.svelte";

  export let fund: Fund;

  const dispatch = createEventDispatcher();

  let isEditing = false;
  let editedFund: Partial<Fund> = { ...fund };

  let showNotes = false;
  let showRoadshows = false;
  let showSalesFunnel = false;

  let notes: Note[] = [];
  let loading = true;

  let selectedNote: Note | null = null;
  let showNoteDetail = false;

  // GP lookup for displaying GP name
  let gps: GP[] = [];
  let gpName = "-";

  const statusOptions = ["premarketing", "fundraising", "semiliquid"];

  onMount(async () => {
    if (!fund.id) return;

    try {
      // Fetch notes and GPs in parallel
      const [fetchedNotes, fetchedGPs] = await Promise.all([
        fetchFundNotes(fund.id),
        fetchGPs()
      ]);

      // Filter notes to only show those with actual content
      notes = fetchedNotes.filter(note => {
        return note.summary || note.raw_notes || note.content_text;
      });

      gps = fetchedGPs;

      // Find GP name
      if (fund.gp_notion_id) {
        const gp = gps.find(g => g.notion_id === fund.gp_notion_id);
        if (gp) {
          gpName = gp.name;
        }
      }
    } catch (err) {
      console.error("Failed to fetch fund details:", err);
    } finally {
      loading = false;
    }
  });

  function close() {
    dispatch("close");
  }

  function handleEdit() {
    isEditing = true;
    editedFund = { ...fund };
  }

  function cancelEdit() {
    isEditing = false;
    editedFund = { ...fund };
  }

  async function saveEdit() {
    if (!fund.id) return;

    try {
      const updated = await updateFund(fund.id, editedFund);
      fund = updated;
      isEditing = false;
      dispatch("updated", updated);
    } catch (err) {
      console.error("Failed to update fund:", err);
      alert("Failed to update fund");
    }
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
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-card" on:click|stopPropagation>
    <div class="card-header">
      <h2>{fund.fund_name}</h2>
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
          <div class="info-item">
            <label>Geography</label>
            {#if isEditing}
              <input type="text" bind:value={editedFund.geography} placeholder="Geography" />
            {:else}
              <div class="value">{fund.geography || "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Status</label>
            {#if isEditing}
              <select bind:value={editedFund.status}>
                <option value="">Select status...</option>
                {#each statusOptions as option}
                  <option value={option}>{option}</option>
                {/each}
              </select>
            {:else}
              <div class="value">{fund.status || "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Asset Class</label>
            {#if isEditing}
              <input type="text" bind:value={editedFund.asset_class} placeholder="Asset Class" />
            {:else}
              <div class="value">{fund.asset_class || "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>GP</label>
            <div class="value">{gpName}</div>
          </div>

          <div class="info-item">
            <label>Target ($M)</label>
            {#if isEditing}
              <input type="number" bind:value={editedFund.target_mn} placeholder="Target" />
            {:else}
              <div class="value">{fund.target_mn ? `$${fund.target_mn}M` : "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Hard Cap ($M)</label>
            {#if isEditing}
              <input type="number" bind:value={editedFund.hard_cap_mn} placeholder="Hard Cap" />
            {:else}
              <div class="value">{fund.hard_cap_mn ? `$${fund.hard_cap_mn}M` : "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Launch</label>
            {#if isEditing}
              <input type="date" bind:value={editedFund.launch} />
            {:else}
              <div class="value">{formatDate(fund.launch)}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Final Close</label>
            {#if isEditing}
              <input type="date" bind:value={editedFund.final_close} />
            {:else}
              <div class="value">{formatDate(fund.final_close)}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Roadshow Date</label>
            {#if isEditing}
              <input type="date" bind:value={editedFund.roadshow_date} />
            {:else}
              <div class="value">{formatDate(fund.roadshow_date)}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Target IRR</label>
            {#if isEditing}
              <input type="text" bind:value={editedFund.target_irr} placeholder="Target IRR" />
            {:else}
              <div class="value">{fund.target_irr || "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Target Multiple</label>
            {#if isEditing}
              <input type="number" step="0.1" bind:value={editedFund.target_multiple} placeholder="Target Multiple" />
            {:else}
              <div class="value">{fund.target_multiple ? `${fund.target_multiple}x` : "-"}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Potential</label>
            {#if isEditing}
              <input type="text" bind:value={editedFund.potential} placeholder="Potential" />
            {:else}
              <div class="value">{fund.potential || "-"}</div>
            {/if}
          </div>
        </div>

        {#if isEditing || fund.sectors}
          <div class="text-section">
            <h4>Sectors</h4>
            {#if isEditing}
              <textarea bind:value={editedFund.sectors} placeholder="Sectors"></textarea>
            {:else}
              <div class="text-content">{fund.sectors}</div>
            {/if}
          </div>
        {/if}

        {#if isEditing || fund.current_lps}
          <div class="text-section">
            <h4>Current LPs</h4>
            {#if isEditing}
              <textarea bind:value={editedFund.current_lps} placeholder="Current LPs"></textarea>
            {:else}
              <div class="text-content">{fund.current_lps}</div>
            {/if}
          </div>
        {/if}

        {#if isEditing || fund.note}
          <div class="text-section">
            <h4>Notes</h4>
            {#if isEditing}
              <textarea bind:value={editedFund.note} placeholder="Notes"></textarea>
            {:else}
              <div class="text-content">{fund.note}</div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Separator Line -->
      <div class="section-divider"></div>

      <!-- Toggle Sections -->
      <div class="toggle-sections">
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
          <button class="toggle-header" on:click={() => showRoadshows = !showRoadshows}>
            <span class="toggle-icon">{showRoadshows ? '▼' : '▶'}</span>
            <span class="toggle-title">Roadshows</span>
          </button>
          {#if showRoadshows}
            <div class="toggle-content">
              <p class="empty-state">Coming soon</p>
            </div>
          {/if}
        </div>

        <div class="toggle-section">
          <button class="toggle-header" on:click={() => showSalesFunnel = !showSalesFunnel}>
            <span class="toggle-icon">{showSalesFunnel ? '▼' : '▶'}</span>
            <span class="toggle-title">Sales Funnel</span>
          </button>
          {#if showSalesFunnel && fund.id}
            <div class="toggle-content">
              <SalesFunnel fundId={fund.id} />
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
    max-width: 900px;
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

  .info-item input,
  .info-item select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.2s;
  }

  .info-item input:focus,
  .info-item select:focus {
    outline: none;
    border-color: #3498db;
  }

  .text-section {
    margin-top: 2rem;
  }

  .text-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .text-content {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    color: #555;
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .text-section textarea {
    width: 100%;
    min-height: 100px;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.2s;
  }

  .text-section textarea:focus {
    outline: none;
    border-color: #3498db;
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

  .item-summary {
    font-size: 0.9rem;
    color: #555;
    margin-top: 0.5rem;
    line-height: 1.5;
  }

  .interest-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    background: #e8f4f8;
    color: #3498db;
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
</style>
