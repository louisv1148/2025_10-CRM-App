<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import type { Roadshow, Fund } from "../lib/api";
  import { createRoadshow, updateRoadshow, deleteRoadshow, fetchFunds } from "../lib/api";

  export let roadshow: Roadshow;
  export let isNew: boolean = false;

  const dispatch = createEventDispatcher();

  let isEditing = isNew;
  let editedRoadshow: Partial<Roadshow> = { ...roadshow };
  let funds: Fund[] = [];
  let pastedImages: Array<{ dataUrl: string; timestamp: Date }> = [];
  let imageInputArea: HTMLDivElement;

  const logisticsOptions = ["None", "Needed", "Done"];

  onMount(async () => {
    try {
      funds = await fetchFunds();

      // Parse existing flight images if any
      if (roadshow.flight_images) {
        try {
          const parsed = JSON.parse(roadshow.flight_images);
          pastedImages = parsed.map((img: any) => ({
            dataUrl: img.dataUrl || img,
            timestamp: img.timestamp ? new Date(img.timestamp) : new Date()
          }));
        } catch (err) {
          console.error("Failed to parse flight images:", err);
        }
      }
    } catch (err) {
      console.error("Failed to fetch funds:", err);
    }
  });

  function close() {
    dispatch("close");
  }

  function handleEdit() {
    isEditing = true;
    editedRoadshow = { ...roadshow };
  }

  function cancelEdit() {
    isEditing = false;
    editedRoadshow = { ...roadshow };
  }

  async function saveEdit() {
    try {
      // Validate required fields
      if (!editedRoadshow.name || !editedRoadshow.name.trim()) {
        alert("Roadshow Name is required");
        return;
      }

      if (!editedRoadshow.fund_id) {
        alert("Fund is required");
        return;
      }

      // Clean up the data - remove empty string values for optional fields
      const cleanedData = { ...editedRoadshow };

      // Convert empty strings to undefined for optional date fields
      if (!cleanedData.arrival || cleanedData.arrival === '') {
        cleanedData.arrival = undefined;
      }
      if (!cleanedData.second_arrival || cleanedData.second_arrival === '') {
        cleanedData.second_arrival = undefined;
      }
      if (!cleanedData.departure || cleanedData.departure === '') {
        cleanedData.departure = undefined;
      }

      // Convert empty strings to undefined for optional text fields
      if (!cleanedData.arrival_city || cleanedData.arrival_city.trim() === '') {
        cleanedData.arrival_city = undefined;
      }
      if (!cleanedData.second_city || cleanedData.second_city.trim() === '') {
        cleanedData.second_city = undefined;
      }
      if (!cleanedData.notes || cleanedData.notes.trim() === '') {
        cleanedData.notes = undefined;
      }

      // Save images as JSON string
      if (pastedImages.length > 0) {
        cleanedData.flight_images = JSON.stringify(pastedImages);
      }

      if (isNew) {
        const created = await createRoadshow(cleanedData as Roadshow);
        dispatch("created", created);
        alert("Roadshow created successfully");
      } else if (roadshow.id) {
        await updateRoadshow(roadshow.id, cleanedData);
        dispatch("updated", { ...roadshow, ...cleanedData });
        alert("Roadshow updated successfully");
      }

      isEditing = false;
    } catch (err) {
      console.error("Failed to save roadshow:", err);
      alert(`Failed to save roadshow: ${err}`);
    }
  }

  async function handleDelete() {
    if (!roadshow.id) return;

    if (confirm("Are you sure you want to delete this roadshow?")) {
      try {
        await deleteRoadshow(roadshow.id);
        dispatch("deleted", roadshow.id);
        close();
      } catch (err) {
        console.error("Failed to delete roadshow:", err);
        alert("Failed to delete roadshow");
      }
    }
  }

  // Handle image paste
  function handlePaste(event: ClipboardEvent) {
    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];

      if (item.type.indexOf('image') !== -1) {
        event.preventDefault();

        const file = item.getAsFile();
        if (!file) continue;

        const reader = new FileReader();
        reader.onload = (e) => {
          const dataUrl = e.target?.result as string;
          pastedImages = [...pastedImages, {
            dataUrl: dataUrl,
            timestamp: new Date()
          }];
        };
        reader.readAsDataURL(file);
      }
    }
  }

  function removeImage(index: number) {
    pastedImages = pastedImages.filter((_, i) => i !== index);
  }

  function viewImage(dataUrl: string) {
    // Open image in new window
    const win = window.open();
    if (win) {
      win.document.write(`<img src="${dataUrl}" style="max-width: 100%; height: auto;" />`);
    }
  }

  function getFundName(fundId: number | undefined): string {
    if (!fundId) return "-";
    const fund = funds.find(f => f.id === fundId);
    return fund?.fund_name || "-";
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "";
    return dateStr.split('T')[0]; // Return YYYY-MM-DD format
  }

  function getLogisticsColor(status: string): string {
    if (status === "Needed") return "#e74c3c";
    if (status === "Done") return "#27ae60";
    return "#27ae60"; // None is also green
  }
</script>

<div class="modal-overlay" on:click={close}>
  <div class="detail-card" on:click|stopPropagation>
    <div class="card-header">
      <h2>{isNew ? "New Roadshow" : roadshow.name || "Roadshow Details"}</h2>
      <button class="close-btn" on:click={close}>✕</button>
    </div>

    <div class="card-content">
      {#if isEditing}
        <!-- Edit Mode -->
        <div class="form-grid">
          <div class="form-group full-width">
            <label for="name">Roadshow Name *</label>
            <input
              id="name"
              type="text"
              bind:value={editedRoadshow.name}
              placeholder="e.g., Q1 2025 Mexico Roadshow"
            />
          </div>

          <div class="form-group full-width">
            <label for="fund">Fund *</label>
            <select id="fund" bind:value={editedRoadshow.fund_id}>
              <option value={undefined}>Select Fund...</option>
              {#each funds as fund}
                <option value={fund.id}>{fund.fund_name}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="arrival">Arrival Date</label>
            <input
              id="arrival"
              type="date"
              value={formatDate(editedRoadshow.arrival)}
              on:change={(e) => editedRoadshow.arrival = e.currentTarget.value}
            />
          </div>

          <div class="form-group">
            <label for="arrival_city">Arrival City</label>
            <input
              id="arrival_city"
              type="text"
              bind:value={editedRoadshow.arrival_city}
              placeholder="e.g., Monterrey"
            />
          </div>

          <div class="form-group">
            <label for="second_arrival">2nd City Arrival</label>
            <input
              id="second_arrival"
              type="date"
              value={formatDate(editedRoadshow.second_arrival)}
              on:change={(e) => editedRoadshow.second_arrival = e.currentTarget.value}
            />
          </div>

          <div class="form-group">
            <label for="second_city">2nd City</label>
            <input
              id="second_city"
              type="text"
              bind:value={editedRoadshow.second_city}
              placeholder="e.g., Mexico City"
            />
          </div>

          <div class="form-group">
            <label for="departure">Departure Date</label>
            <input
              id="departure"
              type="date"
              value={formatDate(editedRoadshow.departure)}
              on:change={(e) => editedRoadshow.departure = e.currentTarget.value}
            />
          </div>

          <!-- Logistics Section -->
          <div class="form-section full-width">
            <h3>Logistics</h3>
          </div>

          <div class="form-group">
            <label for="lv_flight">LV Flight</label>
            <select id="lv_flight" bind:value={editedRoadshow.lv_flight} style="background-color: {getLogisticsColor(editedRoadshow.lv_flight || 'None')}; color: white;">
              {#each logisticsOptions as option}
                <option value={option}>{option}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="lv_hotel">LV Hotel</label>
            <select id="lv_hotel" bind:value={editedRoadshow.lv_hotel} style="background-color: {getLogisticsColor(editedRoadshow.lv_hotel || 'None')}; color: white;">
              {#each logisticsOptions as option}
                <option value={option}>{option}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="mty_driver">MTY Driver</label>
            <select id="mty_driver" bind:value={editedRoadshow.mty_driver} style="background-color: {getLogisticsColor(editedRoadshow.mty_driver || 'None')}; color: white;">
              {#each logisticsOptions as option}
                <option value={option}>{option}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="cdmx_driver">CDMX Driver</label>
            <select id="cdmx_driver" bind:value={editedRoadshow.cdmx_driver} style="background-color: {getLogisticsColor(editedRoadshow.cdmx_driver || 'None')}; color: white;">
              {#each logisticsOptions as option}
                <option value={option}>{option}</option>
              {/each}
            </select>
          </div>

          <!-- Flight Images Section -->
          <div class="form-section full-width">
            <h3>Flight Details Images</h3>
            <p class="help-text">Paste flight booking images here (Ctrl/Cmd + V)</p>
            <div
              bind:this={imageInputArea}
              class="image-paste-area"
              on:paste={handlePaste}
              contenteditable="true"
              data-placeholder="Click here and paste images (Ctrl/Cmd + V)..."
            ></div>

            {#if pastedImages.length > 0}
              <div class="pasted-images-grid">
                {#each pastedImages as image, index}
                  <div class="image-preview">
                    <img src={image.dataUrl} alt="Flight details" on:click={() => viewImage(image.dataUrl)} />
                    <button class="remove-image-btn" on:click={() => removeImage(index)}>✕</button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-group full-width">
            <label for="notes">Notes</label>
            <textarea
              id="notes"
              bind:value={editedRoadshow.notes}
              rows="4"
              placeholder="Additional notes about this roadshow..."
            />
          </div>
        </div>

        <div class="card-actions">
          <button class="btn-primary" on:click={saveEdit}>
            {isNew ? "Create Roadshow" : "Save Changes"}
          </button>
          <button class="btn-secondary" on:click={cancelEdit}>Cancel</button>
          {#if !isNew}
            <button class="btn-danger" on:click={handleDelete}>Delete</button>
          {/if}
        </div>
      {:else}
        <!-- View Mode -->
        <div class="info-grid">
          <div class="info-item full-width">
            <strong>Name:</strong> {roadshow.name}
          </div>

          <div class="info-item full-width">
            <strong>Fund:</strong> {getFundName(roadshow.fund_id)}
          </div>

          <div class="info-item">
            <strong>Arrival:</strong> {roadshow.arrival ? new Date(roadshow.arrival).toLocaleDateString() : "-"}
          </div>

          <div class="info-item">
            <strong>Arrival City:</strong> {roadshow.arrival_city || "-"}
          </div>

          <div class="info-item">
            <strong>2nd City Arrival:</strong> {roadshow.second_arrival ? new Date(roadshow.second_arrival).toLocaleDateString() : "-"}
          </div>

          <div class="info-item">
            <strong>2nd City:</strong> {roadshow.second_city || "-"}
          </div>

          <div class="info-item">
            <strong>Departure:</strong> {roadshow.departure ? new Date(roadshow.departure).toLocaleDateString() : "-"}
          </div>

          <!-- Logistics Display -->
          <div class="info-section full-width">
            <h3>Logistics</h3>
            <div class="logistics-grid">
              <div class="logistics-badge" style="background-color: {getLogisticsColor(roadshow.lv_flight)}">
                LV Flight: {roadshow.lv_flight}
              </div>
              <div class="logistics-badge" style="background-color: {getLogisticsColor(roadshow.lv_hotel)}">
                LV Hotel: {roadshow.lv_hotel}
              </div>
              <div class="logistics-badge" style="background-color: {getLogisticsColor(roadshow.mty_driver)}">
                MTY Driver: {roadshow.mty_driver}
              </div>
              <div class="logistics-badge" style="background-color: {getLogisticsColor(roadshow.cdmx_driver)}">
                CDMX Driver: {roadshow.cdmx_driver}
              </div>
            </div>
          </div>

          {#if pastedImages.length > 0}
            <div class="info-section full-width">
              <h3>Flight Details Images ({pastedImages.length})</h3>
              <div class="pasted-images-grid">
                {#each pastedImages as image}
                  <div class="image-preview">
                    <img src={image.dataUrl} alt="Flight details" on:click={() => viewImage(image.dataUrl)} />
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          {#if roadshow.notes}
            <div class="info-item full-width">
              <strong>Notes:</strong>
              <p>{roadshow.notes}</p>
            </div>
          {/if}
        </div>

        <div class="card-actions">
          <button class="btn-primary" on:click={handleEdit}>Edit</button>
          <button class="btn-secondary" on:click={close}>Close</button>
        </div>
      {/if}
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
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .detail-card {
    background: white;
    border-radius: 8px;
    max-width: 900px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e0e0e0;
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
  }

  .card-header h2 {
    margin: 0;
    color: #2c3e50;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
    padding: 0.25rem 0.5rem;
  }

  .close-btn:hover {
    color: #e74c3c;
  }

  .card-content {
    padding: 1.5rem;
  }

  .form-grid, .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .form-group, .info-item {
    display: flex;
    flex-direction: column;
  }

  .full-width {
    grid-column: 1 / -1;
  }

  .form-section, .info-section {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
  }

  .form-section h3, .info-section h3 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 1.1rem;
  }

  label {
    font-weight: 600;
    margin-bottom: 0.25rem;
    color: #555;
    font-size: 0.9rem;
  }

  input, select, textarea {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.95rem;
  }

  textarea {
    resize: vertical;
    font-family: inherit;
  }

  .help-text {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.5rem;
  }

  .image-paste-area {
    min-height: 60px;
    border: 2px dashed #ddd;
    border-radius: 4px;
    padding: 1rem;
    cursor: text;
    color: #999;
  }

  .image-paste-area:empty:before {
    content: attr(data-placeholder);
  }

  .image-paste-area:focus {
    outline: none;
    border-color: #3498db;
  }

  .pasted-images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .image-preview {
    position: relative;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    background: #f8f9fa;
    cursor: pointer;
  }

  .image-preview img {
    width: 100%;
    height: 150px;
    object-fit: contain;
    display: block;
    background: white;
  }

  .image-preview:hover {
    border-color: #3498db;
  }

  .remove-image-btn {
    position: absolute;
    top: 0.25rem;
    right: 0.25rem;
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .remove-image-btn:hover {
    background: #c0392b;
  }

  .logistics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.75rem;
  }

  .logistics-badge {
    padding: 0.75rem;
    border-radius: 4px;
    color: white;
    font-weight: 600;
    text-align: center;
    font-size: 0.9rem;
  }

  .info-item strong {
    color: #666;
    margin-bottom: 0.25rem;
  }

  .info-item p {
    margin: 0.5rem 0 0 0;
    color: #2c3e50;
    white-space: pre-wrap;
  }

  .card-actions {
    display: flex;
    gap: 0.75rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
  }

  .btn-primary, .btn-secondary, .btn-danger {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 600;
    transition: background 0.2s;
  }

  .btn-primary {
    background: #27ae60;
    color: white;
  }

  .btn-primary:hover {
    background: #229954;
  }

  .btn-secondary {
    background: #95a5a6;
    color: white;
  }

  .btn-secondary:hover {
    background: #7f8c8d;
  }

  .btn-danger {
    background: #e74c3c;
    color: white;
    margin-left: auto;
  }

  .btn-danger:hover {
    background: #c0392b;
  }
</style>
