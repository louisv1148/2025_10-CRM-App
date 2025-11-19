<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import {
    fetchNoteLPs, fetchNoteGPs, fetchNoteFunds, updateNote, createNote,
    searchLPs, searchGPs, searchFunds,
    linkNoteToLP, unlinkNoteFromLP,
    linkNoteToGP, unlinkNoteFromGP,
    linkNoteToFund, unlinkNoteFromFund,
    type Note, type LP, type GP, type Fund
  } from "../lib/api";
  import { parseNotionContentWithImages } from "../lib/notionParser";

  export let note: Note;
  export let isNew: boolean = false;

  const dispatch = createEventDispatcher();

  // Related entities
  let relatedLPs: LP[] = [];
  let relatedGPs: GP[] = [];
  let relatedFunds: Fund[] = [];
  let loadingRelations = true;

  // LP search state
  let lpSearchQuery = "";
  let lpSearchResults: LP[] = [];
  let lpShowDropdown = false;
  let lpSearchTimeout: ReturnType<typeof setTimeout>;

  // GP search state
  let gpSearchQuery = "";
  let gpSearchResults: GP[] = [];
  let gpShowDropdown = false;
  let gpSearchTimeout: ReturnType<typeof setTimeout>;

  // Fund search state
  let fundSearchQuery = "";
  let fundSearchResults: Fund[] = [];
  let fundShowDropdown = false;
  let fundSearchTimeout: ReturnType<typeof setTimeout>;

  // Edit mode
  let isEditing = isNew;
  let editedNote: Partial<Note> = {};
  let saving = false;

  // Load related entities when note is opened
  onMount(async () => {
    // Skip loading related data if this is a new note
    if (isNew || !note.id) {
      loadingRelations = false;
      return;
    }

    try {
      const [lps, gps, funds] = await Promise.all([
        fetchNoteLPs(note.id),
        fetchNoteGPs(note.id),
        fetchNoteFunds(note.id)
      ]);
      relatedLPs = lps;
      relatedGPs = gps;
      relatedFunds = funds;
    } catch (err) {
      console.error('Failed to load related entities:', err);
    } finally {
      loadingRelations = false;
    }
  });

  // LP search-as-you-type
  function handleLPSearch() {
    clearTimeout(lpSearchTimeout);
    lpSearchTimeout = setTimeout(async () => {
      if (lpSearchQuery.trim().length < 2) {
        lpSearchResults = [];
        lpShowDropdown = false;
        return;
      }

      try {
        lpSearchResults = await searchLPs(lpSearchQuery);
        lpShowDropdown = true;
      } catch (err) {
        console.error("LP search failed:", err);
      }
    }, 300);
  }

  // GP search-as-you-type
  function handleGPSearch() {
    clearTimeout(gpSearchTimeout);
    gpSearchTimeout = setTimeout(async () => {
      if (gpSearchQuery.trim().length < 2) {
        gpSearchResults = [];
        gpShowDropdown = false;
        return;
      }

      try {
        gpSearchResults = await searchGPs(gpSearchQuery);
        gpShowDropdown = true;
      } catch (err) {
        console.error("GP search failed:", err);
      }
    }, 300);
  }

  // Fund search-as-you-type
  function handleFundSearch() {
    clearTimeout(fundSearchTimeout);
    fundSearchTimeout = setTimeout(async () => {
      if (fundSearchQuery.trim().length < 2) {
        fundSearchResults = [];
        fundShowDropdown = false;
        return;
      }

      try {
        fundSearchResults = await searchFunds(fundSearchQuery);
        fundShowDropdown = true;
      } catch (err) {
        console.error("Fund search failed:", err);
      }
    }, 300);
  }

  function clearLPSearch() {
    lpSearchQuery = "";
    lpSearchResults = [];
    lpShowDropdown = false;
  }

  function clearGPSearch() {
    gpSearchQuery = "";
    gpSearchResults = [];
    gpShowDropdown = false;
  }

  function clearFundSearch() {
    fundSearchQuery = "";
    fundSearchResults = [];
    fundShowDropdown = false;
  }

  async function addLP(lp: LP) {
    if (!note.id || !lp.id) return;

    // Check if LP is already linked
    if (relatedLPs.some(l => l.id === lp.id)) {
      console.log("LP already linked, skipping");
      clearLPSearch();
      return;
    }

    try {
      await linkNoteToLP(note.id, lp.id);
      relatedLPs = [...relatedLPs, lp];
      clearLPSearch();
      console.log("LP linked, dispatching updated event");
      dispatch("updated");
    } catch (err) {
      console.error("Failed to link LP:", err);
      alert("Failed to link LP");
    }
  }

  async function removeLP(lp: LP) {
    if (!note.id || !lp.id) return;

    try {
      await unlinkNoteFromLP(note.id, lp.id);
      relatedLPs = relatedLPs.filter(l => l.id !== lp.id);
      console.log("LP removed, dispatching updated event");
      dispatch("updated");
    } catch (err) {
      console.error("Failed to unlink LP:", err);
      alert("Failed to unlink LP");
    }
  }

  async function addGP(gp: GP) {
    if (!note.id || !gp.id) return;

    // Check if GP is already linked
    if (relatedGPs.some(g => g.id === gp.id)) {
      console.log("GP already linked, skipping");
      clearGPSearch();
      return;
    }

    try {
      await linkNoteToGP(note.id, gp.id);
      relatedGPs = [...relatedGPs, gp];
      clearGPSearch();
      console.log("GP linked, dispatching updated event");
      dispatch("updated");
    } catch (err) {
      console.error("Failed to link GP:", err);
      alert("Failed to link GP");
    }
  }

  async function removeGP(gp: GP) {
    if (!note.id || !gp.id) return;

    try {
      await unlinkNoteFromGP(note.id, gp.id);
      relatedGPs = relatedGPs.filter(g => g.id !== gp.id);
      console.log("GP removed, dispatching updated event");
      dispatch("updated");
    } catch (err) {
      console.error("Failed to unlink GP:", err);
      alert("Failed to unlink GP");
    }
  }

  async function addFund(fund: Fund) {
    if (!note.id || !fund.id) return;

    // Check if fund is already linked
    if (relatedFunds.some(f => f.id === fund.id)) {
      console.log("Fund already linked, skipping");
      clearFundSearch();
      return;
    }

    try {
      await linkNoteToFund(note.id, fund.id);
      relatedFunds = [...relatedFunds, fund];
      clearFundSearch();
      console.log("Fund linked, dispatching updated event");
      // Emit event to notify parent that note was updated
      dispatch("updated");
    } catch (err) {
      console.error("Failed to link fund:", err);
      alert("Failed to link fund");
    }
  }

  async function removeFund(fund: Fund) {
    if (!note.id || !fund.id) return;

    try {
      await unlinkNoteFromFund(note.id, fund.id);
      relatedFunds = relatedFunds.filter(f => f.id !== fund.id);
      console.log("Fund removed, dispatching updated event");
      // Emit event to notify parent that note was updated
      dispatch("updated");
    } catch (err) {
      console.error("Failed to unlink fund:", err);
      alert("Failed to unlink fund");
    }
  }

  function startEditing() {
    isEditing = true;
    editedNote = {
      name: note.name,
      date: note.date,
      contact_type: note.contact_type,
      interest: note.interest,
      fundraise: note.fundraise,
      summary: note.summary,
      useful: note.useful,
      raw_notes: note.raw_notes
    };
  }

  function cancelEditing() {
    isEditing = false;
    editedNote = {};
  }

  async function saveChanges() {
    saving = true;
    try {
      if (isNew) {
        // Creating a new note
        const created = await createNote(editedNote as Note);
        isEditing = false;
        editedNote = {};
        console.log("Note created, dispatching created event");
        dispatch("created", created);
        dispatch("close"); // Close the modal after creating
      } else {
        // Updating an existing note
        if (!note.id) return;
        const updated = await updateNote(note.id, editedNote);
        // Update the note object with the new values
        Object.assign(note, updated);
        isEditing = false;
        editedNote = {};
        console.log("Note saved, dispatching updated event");
        // Emit event to notify parent that note was updated
        dispatch("updated");
      }
    } catch (err) {
      console.error(`Failed to ${isNew ? 'create' : 'save'} note:`, err);
      alert(`Failed to ${isNew ? 'create' : 'save'} changes`);
    } finally {
      saving = false;
    }
  }

  // Parse Notion content into readable text and extract images
  $: parsedRawNotes = parseNotionContentWithImages(note.raw_notes);
  $: parsedContentText = parseNotionContentWithImages(note.content_text);

  // Combine image paths from both sources
  $: allImagePaths = [...parsedRawNotes.imagePaths, ...parsedContentText.imagePaths];

  // Lightbox state
  let showLightbox = false;
  let lightboxImageSrc = "";

  function close() {
    dispatch("close");
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  // Convert local file path to backend URL
  function getImageSrc(imagePath: string): string {
    // imagePath is like "notion_images/28cc5599-bacc-80b0-9909-f54b37e1b1f4_677b1fdcdb7b61c26bb3a0f367d8d059.png"
    // Extract just the filename
    const filename = imagePath.split('/').pop();
    return `http://localhost:8000/images/${filename}`;
  }

  // Open image in lightbox
  function openLightbox(imagePath: string) {
    lightboxImageSrc = getImageSrc(imagePath);
    showLightbox = true;
  }

  // Close lightbox
  function closeLightbox() {
    showLightbox = false;
    lightboxImageSrc = "";
  }
</script>

<div class="modal-overlay" on:click={close}>
  <div class="modal-card" on:click|stopPropagation>
    <div class="card-header">
      <h2>{isNew ? 'New Note' : (note.name || 'Untitled Note')}</h2>
      <div class="actions">
        {#if isEditing}
          <button class="action-btn save" on:click={saveChanges} disabled={saving}>
            {saving ? (isNew ? 'Creating...' : 'Saving...') : (isNew ? 'Create' : 'Save')}
          </button>
          <button class="action-btn cancel" on:click={isNew ? close : cancelEditing} disabled={saving}>
            Cancel
          </button>
        {:else}
          <button class="action-btn edit" on:click={startEditing}>Edit</button>
        {/if}
        <button class="action-btn close" on:click={close}>✕</button>
      </div>
    </div>

    <div class="card-body">
      <!-- Main Information Section -->
      <div class="info-section">
        <div class="info-grid">
          <div class="info-item">
            <label>Name</label>
            {#if isEditing}
              <input class="edit-input" type="text" bind:value={editedNote.name} />
            {:else}
              <div class="value">{note.name || 'Untitled'}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Date</label>
            {#if isEditing}
              <input class="edit-input" type="date" bind:value={editedNote.date} />
            {:else}
              <div class="value">{formatDate(note.date)}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Contact Type</label>
            {#if isEditing}
              <input class="edit-input" type="text" bind:value={editedNote.contact_type} />
            {:else}
              <div class="value">{note.contact_type || '-'}</div>
            {/if}
          </div>

          <div class="info-item">
            <label>Interest</label>
            {#if isEditing}
              <input class="edit-input" type="text" bind:value={editedNote.interest} />
            {:else}
              <div class="value">{note.interest || '-'}</div>
            {/if}
          </div>

          <div class="info-item full-width">
            <label>Fundraise (Funds)</label>
            {#if isEditing}
              <div class="fund-search-section">
                <div class="search-input-wrapper">
                  <input
                    class="edit-input"
                    type="text"
                    placeholder="Search funds..."
                    bind:value={fundSearchQuery}
                    on:input={handleFundSearch}
                    on:focus={() => fundSearchQuery && (fundShowDropdown = true)}
                  />
                  {#if fundSearchQuery}
                    <button class="clear-btn" on:click={clearFundSearch}>✕</button>
                  {/if}
                </div>

                {#if fundShowDropdown && fundSearchResults.length > 0}
                  <div class="search-dropdown">
                    {#each fundSearchResults as fund}
                      <div
                        class="search-result-item"
                        on:click={() => addFund(fund)}
                      >
                        {fund.fund_name}
                      </div>
                    {/each}
                  </div>
                {/if}

                {#if relatedFunds.length > 0}
                  <div class="selected-funds">
                    {#each relatedFunds as fund}
                      <div class="fund-chip">
                        <span>{fund.fund_name}</span>
                        <button class="remove-fund-btn" on:click={() => removeFund(fund)}>✕</button>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <div class="no-funds">No funds linked</div>
                {/if}
              </div>
            {:else}
              <div class="value">
                {#if relatedFunds.length > 0}
                  {relatedFunds.map(f => f.fund_name).join(', ')}
                {:else}
                  -
                {/if}
              </div>
            {/if}
          </div>

          <div class="info-item">
            <label>Useful</label>
            {#if isEditing}
              <label class="checkbox-wrapper">
                <input type="checkbox" bind:checked={editedNote.useful} />
                <span>Mark as useful</span>
              </label>
            {:else}
              <div class="value">{note.useful ? 'Yes' : 'No'}</div>
            {/if}
          </div>

          <!-- Related LPs Section -->
          <div class="info-item full-width">
            <label>Related LPs</label>
            {#if isEditing}
              <div class="fund-search-section">
                <div class="search-input-wrapper">
                  <input
                    class="edit-input"
                    type="text"
                    placeholder="Search LPs..."
                    bind:value={lpSearchQuery}
                    on:input={handleLPSearch}
                    on:focus={() => lpSearchQuery && (lpShowDropdown = true)}
                  />
                  {#if lpSearchQuery}
                    <button class="clear-btn" on:click={clearLPSearch}>✕</button>
                  {/if}
                </div>

                {#if lpShowDropdown && lpSearchResults.length > 0}
                  <div class="search-dropdown">
                    {#each lpSearchResults as lp}
                      <div
                        class="search-result-item"
                        on:click={() => addLP(lp)}
                      >
                        {lp.name}
                      </div>
                    {/each}
                  </div>
                {/if}

                {#if relatedLPs.length > 0}
                  <div class="selected-funds">
                    {#each relatedLPs as lp}
                      <div class="fund-chip">
                        <span>{lp.name}</span>
                        <button class="remove-fund-btn" on:click={() => removeLP(lp)}>✕</button>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <div class="no-funds">No LPs linked</div>
                {/if}
              </div>
            {:else}
              <div class="value">
                {#if relatedLPs.length > 0}
                  {relatedLPs.map(l => l.name).join(', ')}
                {:else}
                  -
                {/if}
              </div>
            {/if}
          </div>

          <!-- Related GPs Section -->
          <div class="info-item full-width">
            <label>Related GPs</label>
            {#if isEditing}
              <div class="fund-search-section">
                <div class="search-input-wrapper">
                  <input
                    class="edit-input"
                    type="text"
                    placeholder="Search GPs..."
                    bind:value={gpSearchQuery}
                    on:input={handleGPSearch}
                    on:focus={() => gpSearchQuery && (gpShowDropdown = true)}
                  />
                  {#if gpSearchQuery}
                    <button class="clear-btn" on:click={clearGPSearch}>✕</button>
                  {/if}
                </div>

                {#if gpShowDropdown && gpSearchResults.length > 0}
                  <div class="search-dropdown">
                    {#each gpSearchResults as gp}
                      <div
                        class="search-result-item"
                        on:click={() => addGP(gp)}
                      >
                        {gp.name}
                      </div>
                    {/each}
                  </div>
                {/if}

                {#if relatedGPs.length > 0}
                  <div class="selected-funds">
                    {#each relatedGPs as gp}
                      <div class="fund-chip">
                        <span>{gp.name}</span>
                        <button class="remove-fund-btn" on:click={() => removeGP(gp)}>✕</button>
                      </div>
                    {/each}
                  </div>
                {:else}
                  <div class="no-funds">No GPs linked</div>
                {/if}
              </div>
            {:else}
              <div class="value">
                {#if relatedGPs.length > 0}
                  {relatedGPs.map(g => g.name).join(', ')}
                {:else}
                  -
                {/if}
              </div>
            {/if}
          </div>
        </div>

        <div class="summary-section">
          <h4>Summary</h4>
          {#if isEditing}
            <textarea class="edit-textarea" bind:value={editedNote.summary} rows="5"></textarea>
          {:else}
            <div class="summary">{note.summary || '-'}</div>
          {/if}
        </div>

        <div class="notes-section">
          <h4>Notes</h4>
          {#if isEditing}
            <textarea class="edit-textarea" bind:value={editedNote.raw_notes} rows="10"></textarea>
          {:else}
            <div class="notes">{parsedRawNotes.text || '-'}</div>
          {/if}
        </div>

        {#if parsedContentText.text}
          <div class="content-section">
            <h4>Content</h4>
            <div class="content">{parsedContentText.text}</div>
          </div>
        {/if}


        {#if allImagePaths.length > 0}
          <div class="images-section">
            <h4>Images</h4>
            <div class="images-container">
              {#each allImagePaths as imagePath}
                <img
                  src={getImageSrc(imagePath)}
                  alt="Note image"
                  class="note-image"
                  on:click={() => openLightbox(imagePath)}
                />
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

{#if showLightbox}
  <div class="lightbox-overlay" on:click={closeLightbox}>
    <div class="lightbox-content" on:click|stopPropagation>
      <button class="lightbox-close" on:click={closeLightbox}>✕</button>
      <img src={lightboxImageSrc} alt="Zoomed note image" class="lightbox-image" />
    </div>
  </div>
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

  .action-btn.save {
    background: #27ae60;
    color: white;
  }

  .action-btn.save:hover:not(:disabled) {
    background: #229954;
  }

  .action-btn.cancel {
    background: #e74c3c;
    color: white;
  }

  .action-btn.cancel:hover:not(:disabled) {
    background: #c0392b;
  }

  .action-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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

  .edit-input,
  .edit-textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.2s;
  }

  .edit-input:focus,
  .edit-textarea:focus {
    outline: none;
    border-color: #3498db;
  }

  .edit-textarea {
    resize: vertical;
    min-height: 100px;
  }

  .checkbox-wrapper {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .checkbox-wrapper input[type="checkbox"] {
    cursor: pointer;
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

  .info-item.full-width {
    grid-column: 1 / -1;
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

  .summary-section,
  .notes-section,
  .content-section {
    margin-top: 2rem;
  }

  .summary-section h4,
  .notes-section h4,
  .content-section h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .summary,
  .notes,
  .content {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
    color: #555;
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .images-section {
    margin-top: 2rem;
  }

  .images-section h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .images-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .note-image {
    width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
  }

  .note-image:hover {
    transform: scale(1.01);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    opacity: 0.9;
  }

  /* Lightbox styles */
  .lightbox-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 20000;
    animation: fadeIn 0.2s ease-in-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .lightbox-content {
    position: relative;
    max-width: 95vw;
    max-height: 95vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .lightbox-image {
    max-width: 100%;
    max-height: 95vh;
    object-fit: contain;
    border-radius: 4px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  }

  .lightbox-close {
    position: absolute;
    top: -50px;
    right: -50px;
    width: 40px;
    height: 40px;
    background: white;
    border: none;
    border-radius: 50%;
    font-size: 1.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    color: #2c3e50;
  }

  .lightbox-close:hover {
    background: #e74c3c;
    color: white;
    transform: scale(1.1);
  }

  /* Fund search styles */
  .fund-search-section {
    position: relative;
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .clear-btn {
    position: absolute;
    right: 8px;
    background: none;
    border: none;
    font-size: 1.2rem;
    color: #999;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
  }

  .clear-btn:hover {
    color: #e74c3c;
  }

  .search-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    max-height: 200px;
    overflow-y: auto;
    z-index: 1000;
    margin-top: 4px;
  }

  .search-result-item {
    padding: 0.75rem;
    cursor: pointer;
    transition: background 0.2s;
    border-bottom: 1px solid #f0f0f0;
  }

  .search-result-item:last-child {
    border-bottom: none;
  }

  .search-result-item:hover {
    background: #f8f9fa;
  }

  .selected-funds {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }

  .fund-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #3498db;
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.9rem;
  }

  .remove-fund-btn {
    background: none;
    border: none;
    color: white;
    font-size: 1.1rem;
    cursor: pointer;
    padding: 0;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s;
  }

  .remove-fund-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .no-funds {
    margin-top: 0.75rem;
    color: #999;
    font-style: italic;
    font-size: 0.9rem;
  }
</style>
