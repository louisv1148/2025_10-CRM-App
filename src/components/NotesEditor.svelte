<script lang="ts">
  import { currentNote, hasUnsavedChanges, lastSaved } from "../lib/stores";
  import { updateNote, createNote } from "../lib/api";

  let notes = "";
  let autoSaveTimer: number;

  // Auto-save every 10 seconds
  function scheduleAutoSave() {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);

    autoSaveTimer = setTimeout(async () => {
      await saveNotes();
    }, 10000);
  }

  async function saveNotes() {
    if ($currentNote?.id) {
      await updateNote($currentNote.id, { raw_notes: notes });
    } else {
      const newNote = await createNote({ raw_notes: notes });
      $currentNote = newNote;
    }

    $hasUnsavedChanges = false;
    $lastSaved = new Date();
  }

  function handleInput() {
    $hasUnsavedChanges = true;
    scheduleAutoSave();
  }
</script>

<section class="notes-editor">
  <div class="editor-header">
    <h3>Meeting Notes</h3>
    <div class="save-status">
      {#if $hasUnsavedChanges}
        <span class="unsaved">Unsaved changes</span>
      {:else if $lastSaved}
        <span class="saved">Last saved: {$lastSaved.toLocaleTimeString()}</span>
      {/if}
    </div>
  </div>

  <textarea
    bind:value={notes}
    on:input={handleInput}
    placeholder="Type your meeting notes here...

The notes will auto-save every 10 seconds.

You can also:
- Record audio
- Transcribe automatically
- Generate AI summaries"
  />

  <div class="editor-actions">
    <button on:click={saveNotes}>Save Now</button>
    <button class="secondary">Generate Summary</button>
  </div>
</section>

<style>
  .notes-editor {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  h3 {
    margin: 0;
    color: #2c3e50;
  }

  .save-status {
    font-size: 0.85rem;
  }

  .unsaved {
    color: #e74c3c;
  }

  .saved {
    color: #27ae60;
  }

  textarea {
    flex: 1;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    resize: none;
    line-height: 1.6;
  }

  textarea:focus {
    outline: none;
    border-color: #3498db;
  }

  .editor-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  button {
    padding: 0.5rem 1rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  button:hover {
    background: #2980b9;
  }

  button.secondary {
    background: #95a5a6;
  }

  button.secondary:hover {
    background: #7f8c8d;
  }
</style>
