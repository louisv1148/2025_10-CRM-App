<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { fetchNoteLPs, fetchNoteGPs, updateNote, type Note, type LP, type GP } from "../lib/api";
  import { parseNotionContentWithImages } from "../lib/notionParser";

  export let note: Note;

  const dispatch = createEventDispatcher();

  // Related entities
  let relatedLPs: LP[] = [];
  let relatedGPs: GP[] = [];
  let loadingRelations = true;

  // Edit mode
  let isEditing = false;
  let editedNote: Partial<Note> = {};
  let saving = false;

  // Load related entities when note is opened
  onMount(async () => {
    if (!note.id) {
      loadingRelations = false;
      return;
    }

    try {
      const [lps, gps] = await Promise.all([
        fetchNoteLPs(note.id),
        fetchNoteGPs(note.id)
      ]);
      relatedLPs = lps;
      relatedGPs = gps;
    } catch (err) {
      console.error('Failed to load related entities:', err);
    } finally {
      loadingRelations = false;
    }
  });

  function startEditing() {
    isEditing = true;
    editedNote = {
      name: note.name,
      date: note.date,
      contact_type: note.contact_type,
      interest: note.interest,
      fundraise: note.fundraise,
      summary: note.summary,
      useful: note.useful
    };
  }

  function cancelEditing() {
    isEditing = false;
    editedNote = {};
  }

  async function saveChanges() {
    if (!note.id) return;

    saving = true;
    try {
      const updated = await updateNote(note.id, editedNote);
      // Update the note object with the new values
      Object.assign(note, updated);
      isEditing = false;
      editedNote = {};
    } catch (err) {
      console.error('Failed to save note:', err);
      alert('Failed to save changes');
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
      <h2>{note.name || 'Untitled Note'}</h2>
      <div class="actions">
        {#if isEditing}
          <button class="action-btn save" on:click={saveChanges} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button class="action-btn cancel" on:click={cancelEditing} disabled={saving}>
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

          <div class="info-item">
            <label>Fundraise</label>
            {#if isEditing}
              <input class="edit-input" type="text" bind:value={editedNote.fundraise} />
            {:else}
              <div class="value">{note.fundraise || '-'}</div>
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
        </div>

        <div class="summary-section">
          <h4>Summary</h4>
          {#if isEditing}
            <textarea class="edit-textarea" bind:value={editedNote.summary} rows="5"></textarea>
          {:else}
            <div class="summary">{note.summary || '-'}</div>
          {/if}
        </div>

        {#if parsedRawNotes.text}
          <div class="notes-section">
            <h4>Notes</h4>
            <div class="notes">{parsedRawNotes.text}</div>
          </div>
        {/if}

        {#if parsedContentText.text}
          <div class="content-section">
            <h4>Content</h4>
            <div class="content">{parsedContentText.text}</div>
          </div>
        {/if}

        {#if !loadingRelations && (relatedLPs.length > 0 || relatedGPs.length > 0)}
          <div class="relations-section">
            {#if relatedLPs.length > 0}
              <div class="relation-group">
                <h4>Related LPs</h4>
                <div class="relation-list">
                  {#each relatedLPs as lp}
                    <div class="relation-item">{lp.name}</div>
                  {/each}
                </div>
              </div>
            {/if}

            {#if relatedGPs.length > 0}
              <div class="relation-group">
                <h4>Related GPs</h4>
                <div class="relation-list">
                  {#each relatedGPs as gp}
                    <div class="relation-item">{gp.name}</div>
                  {/each}
                </div>
              </div>
            {/if}
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
</style>
