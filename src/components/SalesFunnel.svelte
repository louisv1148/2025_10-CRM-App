<script lang="ts">
  import { onMount } from "svelte";
  import { fetchFundSalesFunnel, updateLPInterest, updateLP, fetchLP, deleteLP, fetchNote, type SalesFunnelItem, type LP, type Note } from "../lib/api";
  import NoteDetailCard from "./NoteDetailCard.svelte";
  import LPDetailCard from "./LPDetailCard.svelte";

  export let fundId: number;

  let funnelData: SalesFunnelItem[] = [];
  let sortedFunnelData: SalesFunnelItem[] = [];
  let loading = true;

  // Group by interest stages
  let stages = [
    { key: "commitment", label: "Commitment", color: "#27ae60", count: 0 },
    { key: "due_diligence", label: "Due Diligence", color: "#3498db", count: 0 },
    { key: "interested", label: "Interested", color: "#9b59b6", count: 0 },
    { key: "meeting", label: "Meeting", color: "#e67e22", count: 0 },
    { key: "meeting_offered", label: "Meeting Offered", color: "#f39c12", count: 0 },
    { key: "no_reply", label: "No reply", color: "#95a5a6", count: 0 },
    { key: "low_probability", label: "Low Probability", color: "#c0392b", count: 0 },
    { key: "inactive", label: "Inactive", color: "#7f8c8d", count: 0 }
  ];

  let expandedStages: Set<string> = new Set(["interested"]);
  let selectedNote: Note | null = null;
  let showNoteDetail = false;

  // LP Detail card state
  let selectedLP: LP | null = null;
  let showLPDetail = false;

  // Sort state
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility and order
  let showColumnsMenu = false;
  let visibleColumns = {
    priority: true,
    location: true,
    stage: true,
    last_contact: true,
    note_summary: false,
    notes_db: true,
    aum: true,
    inv_low: true,
    inv_high: true,
    type: true,
    advisor: true
  };

  let columnOrder = [
    { key: 'priority', label: 'Priority' },
    { key: 'location', label: 'Location' },
    { key: 'stage', label: 'Stage' },
    { key: 'last_contact', label: 'Last Contact' },
    { key: 'note_summary', label: 'Note' },
    { key: 'notes_db', label: 'Notes DB' },
    { key: 'aum', label: 'AUM' },
    { key: 'inv_low', label: 'Inv. LOW' },
    { key: 'inv_high', label: 'Inv. HIGH' },
    { key: 'type', label: 'Type' },
    { key: 'advisor', label: 'Advisor' }
  ];

  let initialized = false;

  // Load settings from localStorage
  function loadSettings() {
    try {
      const savedSort = localStorage.getItem(`salesFunnel_${fundId}_sort`);
      const savedColumns = localStorage.getItem(`salesFunnel_${fundId}_columns`);
      const savedColumnOrder = localStorage.getItem(`salesFunnel_${fundId}_columnOrder`);

      if (savedSort) {
        const sortData = JSON.parse(savedSort);
        sortFields = sortData.fields || [];
        sortDirections = sortData.directions || {};
      }

      if (savedColumns) {
        visibleColumns = { ...visibleColumns, ...JSON.parse(savedColumns) };
      }

      if (savedColumnOrder) {
        columnOrder = JSON.parse(savedColumnOrder);
      }
    } catch (err) {
      console.error('Failed to load settings from localStorage:', err);
    }
  }

  // Save settings to localStorage
  function saveSettings() {
    try {
      localStorage.setItem(`salesFunnel_${fundId}_sort`, JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem(`salesFunnel_${fundId}_columns`, JSON.stringify(visibleColumns));
      localStorage.setItem(`salesFunnel_${fundId}_columnOrder`, JSON.stringify(columnOrder));
    } catch (err) {
      console.error('Failed to save settings to localStorage:', err);
    }
  }

  // Reactive statements to save settings
  $: if (initialized && (sortFields || sortDirections)) saveSettings();
  $: if (initialized && visibleColumns) saveSettings();
  $: if (initialized && columnOrder) saveSettings();

  onMount(async () => {
    loadSettings();
    initialized = true;
    await loadFunnelData();
  });

  async function loadFunnelData() {
    try {
      loading = true;
      funnelData = await fetchFundSalesFunnel(fundId);
      applySorting();
      loading = false;
    } catch (err) {
      console.error("Failed to load sales funnel:", err);
      loading = false;
    }
  }

  function updateStageCounts() {
    // Reset counts
    stages.forEach(stage => stage.count = 0);

    // Count LPs in each stage
    sortedFunnelData.forEach(item => {
      const stage = stages.find(s => s.key === item.interest);
      if (stage) {
        stage.count++;
      }
    });

    // Trigger reactivity
    stages = [...stages];
  }

  function applySorting() {
    let result = [...funnelData];

    // Apply sort
    if (sortFields.length > 0) {
      result.sort((a, b) => {
        for (const field of sortFields) {
          let aVal: any;
          let bVal: any;

          // Map field keys to actual data properties
          switch(field) {
            case 'priority':
              // Treat priority as numeric (0, 1, 2, 3) - empty/null goes to end
              aVal = a.priority !== null && a.priority !== undefined && a.priority !== ''
                ? parseInt(a.priority.toString())
                : 999;
              bVal = b.priority !== null && b.priority !== undefined && b.priority !== ''
                ? parseInt(b.priority.toString())
                : 999;
              break;
            case 'location':
              aVal = a.location || '';
              bVal = b.location || '';
              break;
            case 'aum':
              aVal = a.aum_billions || 0;
              bVal = b.aum_billions || 0;
              break;
            case 'inv_low':
              aVal = a.investment_low || 0;
              bVal = b.investment_low || 0;
              break;
            case 'inv_high':
              aVal = a.investment_high || 0;
              bVal = b.investment_high || 0;
              break;
            case 'type':
              aVal = a.type_of_group || '';
              bVal = b.type_of_group || '';
              break;
            case 'advisor':
              aVal = a.advisor || '';
              bVal = b.advisor || '';
              break;
            case 'last_contact':
              aVal = a.last_contact_date || '';
              bVal = b.last_contact_date || '';
              break;
            case 'lp_name':
              aVal = a.lp_name || '';
              bVal = b.lp_name || '';
              break;
            default:
              aVal = '';
              bVal = '';
          }

          const direction = sortDirections[field] === 'desc' ? -1 : 1;

          if (aVal < bVal) return -1 * direction;
          if (aVal > bVal) return 1 * direction;
        }
        return 0;
      });
    }

    sortedFunnelData = result;
    updateStageCounts();
  }

  function getStageItems(stageKey: string): SalesFunnelItem[] {
    return sortedFunnelData.filter(item => item.interest === stageKey);
  }

  function toggleStage(stageKey: string) {
    if (expandedStages.has(stageKey)) {
      expandedStages.delete(stageKey);
    } else {
      expandedStages.add(stageKey);
    }
    expandedStages = new Set(expandedStages);
  }

  async function changeInterest(lpId: number, newInterest: string) {
    try {
      await updateLPInterest(fundId, lpId, newInterest);
      await loadFunnelData();
    } catch (err) {
      console.error("Failed to update LP interest:", err);
      alert("Failed to update interest level");
    }
  }

  async function updatePriority(lpId: number, newPriority: string) {
    try {
      await updateLP(lpId, { priority: newPriority });
      // Update the local data
      const item = funnelData.find(item => item.lp_id === lpId);
      if (item) {
        item.priority = newPriority;
        funnelData = [...funnelData];
        applySorting();
      }
    } catch (err) {
      console.error("Failed to update LP priority:", err);
      alert("Failed to update priority");
    }
  }

  async function openNote(noteId: number) {
    try {
      selectedNote = await fetchNote(noteId);
      showNoteDetail = true;
    } catch (err) {
      console.error("Failed to fetch note:", err);
      alert("Failed to load note");
    }
  }

  function closeNoteDetail() {
    showNoteDetail = false;
    selectedNote = null;
  }

  async function handleNoteUpdated() {
    // Refresh the funnel data to update last contact dates
    await loadFunnelData();
  }

  // LP Detail card functions
  function openLPDetail(item: SalesFunnelItem) {
    // Convert SalesFunnelItem to LP object
    selectedLP = {
      id: item.lp_id,
      name: item.lp_name,
      aum_billions: item.aum_billions,
      location: item.location,
      priority: item.priority,
      advisor: item.advisor,
      type_of_group: item.type_of_group,
      investment_low: item.investment_low,
      investment_high: item.investment_high
    };
    showLPDetail = true;
  }

  function closeLPDetail() {
    selectedLP = null;
    showLPDetail = false;
  }

  async function handleLPUpdated(event: CustomEvent) {
    console.log("handleLPUpdated called, event detail:", event.detail);

    const updatedLP = event.detail;
    if (!updatedLP?.id) return;

    // Update selectedLP to reflect changes in the detail card
    selectedLP = updatedLP;

    // Refresh the funnel data to get all updated fields
    await loadFunnelData();
  }

  async function handleLPDelete(event: CustomEvent) {
    const lpId = event.detail;
    try {
      await deleteLP(lpId);
      // Refresh the funnel data
      await loadFunnelData();
      closeLPDetail();
    } catch (err) {
      console.error("Failed to delete LP:", err);
      alert("Failed to delete LP");
    }
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  function getCellValue(item: SalesFunnelItem, columnKey: string): string {
    switch (columnKey) {
      case 'priority':
        return ''; // Special handling in template (editable input)
      case 'location':
        return item.location || '-';
      case 'stage':
        return ''; // Special handling in template
      case 'last_contact':
        return formatDate(item.last_contact_date);
      case 'note_summary':
        return 'Coming soon...';
      case 'notes_db':
        return ''; // Special handling in template
      case 'aum':
        return item.aum_billions ? `$${item.aum_billions}B` : '-';
      case 'inv_low':
        return item.investment_low ? `$${item.investment_low}M` : '-';
      case 'inv_high':
        return item.investment_high ? `$${item.investment_high}M` : '-';
      case 'type':
        return item.type_of_group || '-';
      case 'advisor':
        return item.advisor || '-';
      default:
        return '-';
    }
  }

  // Sort functions
  function addSortField(field: string) {
    if (!sortFields.includes(field)) {
      sortFields = [...sortFields, field];
      sortDirections[field] = 'asc';
      applySorting();
    }
  }

  function toggleSortDirection(field: string) {
    sortDirections[field] = sortDirections[field] === 'asc' ? 'desc' : 'asc';
    applySorting();
  }

  function removeSortField(field: string) {
    sortFields = sortFields.filter(f => f !== field);
    delete sortDirections[field];
    applySorting();
  }

  function clearSort() {
    sortFields = [];
    sortDirections = {};
    applySorting();
  }

  // Column reordering
  function moveColumnUp(index: number) {
    if (index === 0) return;
    [columnOrder[index - 1], columnOrder[index]] = [columnOrder[index], columnOrder[index - 1]];
    columnOrder = [...columnOrder];
  }

  function moveColumnDown(index: number) {
    if (index === columnOrder.length - 1) return;
    [columnOrder[index], columnOrder[index + 1]] = [columnOrder[index + 1], columnOrder[index]];
    columnOrder = [...columnOrder];
  }

  function getFieldLabel(field: string): string {
    const column = columnOrder.find(c => c.key === field);
    return column ? column.label : field;
  }
</script>

<div class="sales-funnel">
  {#if loading}
    <div class="loading">Loading sales funnel...</div>
  {:else}
    <div class="toolbar">
      <div class="sort-container">
        <button
          class="sort-btn"
          class:active={sortFields.length > 0}
          on:click={() => showSortMenu = !showSortMenu}
        >
          Sort
          {#if sortFields.length > 0}
            <span class="badge">{sortFields.length}</span>
          {/if}
        </button>

        {#if showSortMenu}
          <div class="sort-menu">
            <div class="sort-header">
              <h4>Sort by</h4>
              <button class="clear-btn" on:click={clearSort}>Clear all</button>
            </div>

            <div class="sort-options">
              <button on:click={() => addSortField('lp_name')}>+ LP Name</button>
              <button on:click={() => addSortField('priority')}>+ Priority</button>
              <button on:click={() => addSortField('location')}>+ Location</button>
              <button on:click={() => addSortField('aum')}>+ AUM</button>
              <button on:click={() => addSortField('last_contact')}>+ Last Contact</button>
            </div>

            {#if sortFields.length > 0}
              <div class="active-sorts">
                <h5>Active sorts:</h5>
                {#each sortFields as field, index}
                  <div class="sort-item">
                    <span class="order-number">{index + 1}.</span>
                    <span class="field-name">{getFieldLabel(field)}</span>
                    <button
                      class="direction-btn"
                      on:click={() => toggleSortDirection(field)}
                    >
                      {sortDirections[field] === 'asc' ? '↑' : '↓'}
                    </button>
                    <button
                      class="remove-btn"
                      on:click={() => removeSortField(field)}
                    >
                      ✕
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <div class="columns-container">
        <button
          class="columns-btn"
          on:click={() => showColumnsMenu = !showColumnsMenu}
        >
          Columns
        </button>

        {#if showColumnsMenu}
          <div class="columns-menu">
            <div class="columns-header">
              <h4>Visible Columns</h4>
              <span class="drag-hint">Use ↑↓ to reorder</span>
            </div>

            <div class="columns-options">
              {#each columnOrder as column, index}
                <div class="column-option">
                  <div class="reorder-buttons">
                    <button
                      class="reorder-btn"
                      disabled={index === 0}
                      on:click={() => moveColumnUp(index)}
                      title="Move up"
                    >
                      ↑
                    </button>
                    <button
                      class="reorder-btn"
                      disabled={index === columnOrder.length - 1}
                      on:click={() => moveColumnDown(index)}
                      title="Move down"
                    >
                      ↓
                    </button>
                  </div>
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      bind:checked={visibleColumns[column.key]}
                    />
                    <span>{column.label}</span>
                  </label>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>

    <div class="funnel-stages">
      {#each stages as stage}
        <div class="stage-section" style="border-left: 4px solid {stage.color}">
          <button
            class="stage-header"
            class:expanded={expandedStages.has(stage.key)}
            on:click={() => toggleStage(stage.key)}
          >
            <span class="stage-icon">{expandedStages.has(stage.key) ? '▼' : '▶'}</span>
            <span class="stage-label">{stage.label}</span>
            <span class="stage-count">{stage.count}</span>
          </button>

          {#if expandedStages.has(stage.key)}
            <div class="stage-content">
              {#if getStageItems(stage.key).length === 0}
                <div class="no-items">No LPs in this stage</div>
              {:else}
                <div class="table-wrapper">
                  <table class="lps-table">
                    <thead>
                      <tr>
                        <th class="name-col">LP Name</th>
                        {#each columnOrder as column}
                          {#if visibleColumns[column.key]}
                            <th>{column.label}</th>
                          {/if}
                        {/each}
                      </tr>
                    </thead>
                    <tbody>
                      {#each getStageItems(stage.key) as item}
                        <tr>
                          <td class="lp-name clickable" on:click={() => openLPDetail(item)}>{item.lp_name}</td>
                          {#each columnOrder as column}
                            {#if visibleColumns[column.key]}
                              <td>
                                {#if column.key === 'priority'}
                                  <input
                                    type="text"
                                    class="priority-input"
                                    value={item.priority || ''}
                                    on:blur={(e) => updatePriority(item.lp_id, e.currentTarget.value)}
                                    on:keydown={(e) => {
                                      if (e.key === 'Enter') {
                                        e.currentTarget.blur();
                                      }
                                    }}
                                    placeholder="-"
                                  />
                                {:else if column.key === 'stage'}
                                  <select
                                    class="interest-select"
                                    value={item.interest}
                                    on:change={(e) => changeInterest(item.lp_id, e.currentTarget.value)}
                                  >
                                    <option value="inactive">Inactive</option>
                                    <option value="commitment">Commitment</option>
                                    <option value="due_diligence">Due Diligence</option>
                                    <option value="interested">Interested</option>
                                    <option value="meeting">Meeting</option>
                                    <option value="meeting_offered">Meeting Offered</option>
                                    <option value="no_reply">No reply</option>
                                    <option value="low_probability">Low Probability</option>
                                  </select>
                                {:else if column.key === 'notes_db'}
                                  {#if item.latest_note_id}
                                    <button class="note-link" on:click={() => openNote(item.latest_note_id)}>
                                      View Note
                                    </button>
                                  {:else}
                                    -
                                  {/if}
                                {:else if column.key === 'note_summary'}
                                  <span class="note-summary">Coming soon...</span>
                                {:else}
                                  {getCellValue(item, column.key)}
                                {/if}
                              </td>
                            {/if}
                          {/each}
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Note Detail Card Modal -->
{#if showNoteDetail && selectedNote}
  <NoteDetailCard
    note={selectedNote}
    on:close={closeNoteDetail}
    on:updated={handleNoteUpdated}
  />
{/if}

<!-- LP Detail Card Modal -->
{#if showLPDetail && selectedLP}
  <LPDetailCard
    lp={selectedLP}
    on:close={closeLPDetail}
    on:updated={handleLPUpdated}
    on:delete={handleLPDelete}
  />
{/if}

<style>
  .sales-funnel {
    padding: 1rem;
    background: white;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #999;
  }

  .toolbar {
    display: flex;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 1rem;
  }

  .sort-container,
  .columns-container {
    position: relative;
  }

  .sort-btn,
  .columns-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.95rem;
    background: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
  }

  .sort-btn:hover,
  .columns-btn:hover {
    border-color: #3498db;
    background: #f0f8ff;
  }

  .sort-btn.active {
    border-color: #3498db;
    background: #3498db;
    color: white;
  }

  .badge {
    background: white;
    color: #3498db;
    padding: 0.1rem 0.4rem;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: bold;
  }

  .sort-btn.active .badge {
    background: #2980b9;
    color: white;
  }

  .sort-menu,
  .columns-menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    left: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 250px;
    max-height: 70vh;
    overflow-y: auto;
  }

  .sort-header,
  .columns-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
  }

  .sort-header h4,
  .columns-header h4 {
    margin: 0;
    font-size: 1rem;
    color: #2c3e50;
  }

  .drag-hint {
    font-size: 0.75rem;
    color: #999;
  }

  .clear-btn {
    background: none;
    border: none;
    color: #3498db;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .clear-btn:hover {
    text-decoration: underline;
  }

  .sort-options {
    padding: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .sort-options button {
    padding: 0.4rem 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .sort-options button:hover {
    border-color: #3498db;
    background: #f0f8ff;
  }

  .active-sorts {
    padding: 1rem;
    border-top: 1px solid #e0e0e0;
  }

  .active-sorts h5 {
    margin: 0 0 0.5rem 0;
    font-size: 0.85rem;
    color: #666;
  }

  .sort-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .order-number {
    font-weight: bold;
    color: #666;
  }

  .field-name {
    flex: 1;
    color: #2c3e50;
  }

  .direction-btn {
    padding: 0.25rem 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 1rem;
  }

  .direction-btn:hover {
    background: #f0f8ff;
  }

  .remove-btn {
    padding: 0.25rem 0.5rem;
    border: none;
    background: none;
    color: #e74c3c;
    cursor: pointer;
    font-size: 1rem;
  }

  .remove-btn:hover {
    color: #c0392b;
  }

  .columns-options {
    padding: 1rem;
  }

  .column-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
  }

  .reorder-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .reorder-btn {
    padding: 0.1rem 0.4rem;
    border: 1px solid #ddd;
    border-radius: 2px;
    background: white;
    cursor: pointer;
    font-size: 0.75rem;
    line-height: 1;
  }

  .reorder-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .reorder-btn:not(:disabled):hover {
    background: #f0f8ff;
    border-color: #3498db;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .checkbox-label input[type="checkbox"] {
    cursor: pointer;
  }

  .funnel-stages {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .stage-section {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
  }

  .stage-header {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #f8f9fa;
    border: none;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: background 0.2s;
  }

  .stage-header:hover {
    background: #e9ecef;
  }

  .stage-header.expanded {
    background: #e9ecef;
  }

  .stage-icon {
    font-size: 0.75rem;
    color: #666;
  }

  .stage-label {
    flex: 1;
    text-align: left;
    color: #2c3e50;
  }

  .stage-count {
    background: #dee2e6;
    color: #495057;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .stage-content {
    padding: 1rem;
    background: white;
  }

  .no-items {
    text-align: center;
    padding: 2rem;
    color: #999;
    font-style: italic;
  }

  .table-wrapper {
    overflow-x: auto;
    max-width: 100%;
  }

  .lps-table {
    width: 100%;
    min-width: 800px;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  .lps-table thead {
    background: #f8f9fa;
  }

  .lps-table th {
    text-align: left;
    padding: 0.5rem;
    font-weight: 600;
    color: #495057;
    border-bottom: 2px solid #dee2e6;
    font-size: 0.85rem;
    white-space: nowrap;
  }

  .lps-table th.name-col {
    min-width: 150px;
    font-weight: 700;
  }

  .lps-table td {
    padding: 0.5rem;
    border-bottom: 1px solid #f0f0f0;
    color: #495057;
  }

  .lps-table tbody tr:hover {
    background: #f8f9fa;
  }

  .lp-name {
    font-weight: 500;
    color: #2c3e50;
  }

  .lp-name.clickable {
    cursor: pointer;
    transition: color 0.2s;
  }

  .lp-name.clickable:hover {
    color: #3498db;
    text-decoration: underline;
  }

  .priority-input {
    padding: 0.25rem 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.85rem;
    background: white;
    width: 100%;
    max-width: 120px;
  }

  .priority-input:focus {
    outline: none;
    border-color: #3498db;
  }

  .interest-select {
    padding: 0.25rem 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.85rem;
    background: white;
    cursor: pointer;
  }

  .interest-select:focus {
    outline: none;
    border-color: #3498db;
  }

  .note-summary {
    font-style: italic;
    color: #999;
  }

  .note-link {
    padding: 0.25rem 0.5rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .note-link:hover {
    background: #2980b9;
  }

  .note-placeholder {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 2rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
  }

  .note-placeholder button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
</style>
