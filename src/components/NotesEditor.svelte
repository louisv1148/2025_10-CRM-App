<script lang="ts">
  import {
    currentNote,
    hasUnsavedChanges,
    lastSaved,
    selectedLP,
    selectedGP,
    selectedParticipants,
    selectedFunds,
    meetingDate,
    meetingTitle,
    meetingFundraise,
    meetingType,
    meetingPinned
  } from "../lib/stores";
  import { updateNote, createNote, createNoteRelationships } from "../lib/api";

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
    try {
      // Generate note name in YYYY_MM_DD_Title format
      const dateFormatted = $meetingDate.replace(/-/g, '_');
      const titlePart = $meetingTitle.trim() || 'Meeting';
      const noteName = `${dateFormatted}_${titlePart}`;

      if ($currentNote?.id) {
        // Update existing note
        await updateNote($currentNote.id, {
          name: noteName,
          raw_notes: notes,
          summary: notes.substring(0, 200) // First 200 chars as summary
        });
        console.log("Note updated:", $currentNote.id);
      } else {
        // Create new note with all metadata
        const newNote = await createNote({
          name: noteName,
          raw_notes: notes,
          summary: notes.substring(0, 200),
          date: $meetingDate,
          fundraise: $meetingFundraise || undefined,
          contact_type: $meetingType || undefined,
          pin: $meetingPinned ? "Yes" : undefined,
          useful: $meetingPinned
        });

        console.log("Note created:", newNote);
        $currentNote = newNote;

        // Create relationships if we have a note ID
        if (newNote.id) {
          const lpIds = $selectedLP ? [$selectedLP] : [];
          const gpIds = $selectedGP ? [$selectedGP] : [];
          const participantIds = $selectedParticipants || [];
          const fundIds = $selectedFunds || [];

          console.log("Creating relationships:", { lpIds, gpIds, participantIds, fundIds });

          if (lpIds.length > 0 || gpIds.length > 0 || participantIds.length > 0 || fundIds.length > 0) {
            const result = await createNoteRelationships(newNote.id, lpIds, gpIds, participantIds, fundIds);
            console.log("Relationships created:", result);
          }
        }

        alert(`Note saved successfully as: ${noteName}`);
      }

      $hasUnsavedChanges = false;
      $lastSaved = new Date();
    } catch (err) {
      console.error("Failed to save note:", err);
      alert("Failed to save note: " + err);
    }
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
