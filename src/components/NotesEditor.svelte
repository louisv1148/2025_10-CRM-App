<script lang="ts">
  import {
    currentNote,
    hasUnsavedChanges,
    lastSaved,
    selectedLPs,
    selectedGPs,
    selectedParticipants,
    selectedFunds,
    selectedRoadshows,
    meetingDate,
    meetingTitle,
    meetingType,
    meetingPinned
  } from "../lib/stores";
  import { updateNote, createNote, createNoteRelationships } from "../lib/api";

  let notes = "";
  let autoSaveTimer: number;
  let pastedImages: Array<{ id: string; dataUrl: string; timestamp: Date }> = [];
  let textareaElement: HTMLTextAreaElement;

  // Handle paste events for images
  function handlePaste(event: ClipboardEvent) {
    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];

      // Check if the item is an image
      if (item.type.indexOf('image') !== -1) {
        event.preventDefault(); // Prevent default paste behavior

        const file = item.getAsFile();
        if (!file) continue;

        // Read the image as data URL
        const reader = new FileReader();
        reader.onload = (e) => {
          const dataUrl = e.target?.result as string;
          const imageId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

          // Add image to the array
          pastedImages = [...pastedImages, {
            id: imageId,
            dataUrl: dataUrl,
            timestamp: new Date()
          }];

          // Insert image reference in notes at cursor position
          const cursorPos = textareaElement.selectionStart;
          const textBefore = notes.substring(0, cursorPos);
          const textAfter = notes.substring(cursorPos);
          notes = textBefore + `\n[Image: ${imageId}]\n` + textAfter;

          $hasUnsavedChanges = true;
          scheduleAutoSave();
        };
        reader.readAsDataURL(file);
      }
    }
  }

  function removeImage(imageId: string) {
    pastedImages = pastedImages.filter(img => img.id !== imageId);
    // Also remove the reference from notes
    notes = notes.replace(`[Image: ${imageId}]`, '');
    $hasUnsavedChanges = true;
  }

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
          contact_type: $meetingType || undefined,
          pin: $meetingPinned ? "Yes" : undefined,
          useful: $meetingPinned
        });

        console.log("Note created:", newNote);
        $currentNote = newNote;

        // Create relationships if we have a note ID
        if (newNote.id) {
          const lpIds = $selectedLPs || [];
          const gpIds = $selectedGPs || [];
          const participantIds = $selectedParticipants || [];
          const fundIds = $selectedFunds || [];
          const roadshowIds = $selectedRoadshows || [];

          console.log("Creating relationships:", { lpIds, gpIds, participantIds, fundIds, roadshowIds });

          if (lpIds.length > 0 || gpIds.length > 0 || participantIds.length > 0 || fundIds.length > 0 || roadshowIds.length > 0) {
            const result = await createNoteRelationships(newNote.id, lpIds, gpIds, participantIds, fundIds, roadshowIds);
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
    bind:this={textareaElement}
    bind:value={notes}
    on:input={handleInput}
    on:paste={handlePaste}
    placeholder="Type your meeting notes here...

The notes will auto-save every 10 seconds.

You can also:
- Record audio
- Transcribe automatically
- Generate AI summaries
- Paste images directly (Ctrl/Cmd + V)"
  />

  {#if pastedImages.length > 0}
    <div class="pasted-images">
      <h4>Pasted Images ({pastedImages.length})</h4>
      <div class="image-grid">
        {#each pastedImages as image}
          <div class="image-item">
            <img src={image.dataUrl} alt="Pasted image" />
            <div class="image-info">
              <span class="image-id">{image.id}</span>
              <button class="remove-btn" on:click={() => removeImage(image.id)} title="Remove image">
                ✕
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

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

  .pasted-images {
    margin-top: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .pasted-images h4 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 0.95rem;
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .image-item {
    position: relative;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    background: white;
  }

  .image-item img {
    width: 100%;
    height: 200px;
    object-fit: contain;
    background: #fff;
    display: block;
  }

  .image-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    background: #fff;
    border-top: 1px solid #e0e0e0;
  }

  .image-id {
    font-size: 0.75rem;
    color: #666;
    font-family: monospace;
  }

  .remove-btn {
    padding: 0.25rem 0.5rem;
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    font-size: 0.85rem;
    line-height: 1;
  }

  .remove-btn:hover {
    background: #c0392b;
  }
</style>
