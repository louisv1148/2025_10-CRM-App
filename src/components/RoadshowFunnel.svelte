<script lang="ts">
  import { onMount } from "svelte";
  import { fetchRoadshows, fetchRoadshowLPStatus, updateLPRoadshowStatus, updateLP, fetchFunds, type Roadshow, type RoadshowLPStatus, type Fund } from "../lib/api";
  import { roadshows, funds } from "../lib/stores";
  import RoadshowDetailCard from "./RoadshowDetailCard.svelte";

  let roadshowList: Roadshow[] = [];
  let selectedRoadshowId: number | null = null;
  let funnelData: RoadshowLPStatus[] = [];
  let sortedFunnelData: RoadshowLPStatus[] = [];
  let loading = true;
  let loadingFunnel = false;

  // Meeting status stages for roadshows
  let stages = [
    { key: "confirmed", label: "Confirmed", color: "#27ae60", count: 0 },
    { key: "interested", label: "Interested", color: "#3498db", count: 0 },
    { key: "offered", label: "Offered", color: "#f39c12", count: 0 },
    { key: "declined", label: "Declined", color: "#e74c3c", count: 0 },
    { key: "inactive", label: "Inactive", color: "#95a5a6", count: 0 }
  ];

  let expandedStages: Set<string> = new Set(["confirmed", "interested", "offered"]);

  // Sort state
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility and order
  let showColumnsMenu = false;
  let visibleColumns: {[key: string]: boolean} = {
    priority: true,
    location: true,
    status: true,
    last_contact: true,
    aum: true,
    type: true,
    advisor: true,
    inv_low: true,
    inv_high: true
  };

  let columnOrder = [
    { key: 'priority', label: 'Priority' },
    { key: 'location', label: 'Location' },
    { key: 'status', label: 'Status' },
    { key: 'last_contact', label: 'Last Contact' },
    { key: 'aum', label: 'AUM' },
    { key: 'inv_low', label: 'Inv. LOW' },
    { key: 'inv_high', label: 'Inv. HIGH' },
    { key: 'type', label: 'Type' },
    { key: 'advisor', label: 'Advisor' }
  ];

  let initialized = false;

  // Detail card state
  let selectedRoadshow: Roadshow | null = null;
  let showDetailCard = false;

  // Load settings from localStorage
  function loadSettings() {
    if (!selectedRoadshowId) return;
    try {
      const savedSort = localStorage.getItem(`roadshowFunnel_${selectedRoadshowId}_sort`);
      const savedColumns = localStorage.getItem(`roadshowFunnel_${selectedRoadshowId}_columns`);
      const savedColumnOrder = localStorage.getItem(`roadshowFunnel_${selectedRoadshowId}_columnOrder`);

      if (savedSort) {
        const sortData = JSON.parse(savedSort);
        sortFields = sortData.fields || [];
        sortDirections = sortData.directions || {};
      }

      if (savedColumns) {
        // Merge saved columns with defaults - this ensures new columns appear even if not in saved settings
        const saved = JSON.parse(savedColumns);
        visibleColumns = { ...visibleColumns, ...saved };
      }

      if (savedColumnOrder) {
        const savedOrder = JSON.parse(savedColumnOrder);
        // Merge saved order with defaults - add any new columns that aren't in saved order
        const savedKeys = new Set(savedOrder.map((col: any) => col.key));
        const newColumns = columnOrder.filter(col => !savedKeys.has(col.key));
        columnOrder = [...savedOrder, ...newColumns];
      }
    } catch (err) {
      console.error('Failed to load settings from localStorage:', err);
    }
  }

  // Save settings to localStorage
  function saveSettings() {
    if (!selectedRoadshowId) return;
    try {
      localStorage.setItem(`roadshowFunnel_${selectedRoadshowId}_sort`, JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem(`roadshowFunnel_${selectedRoadshowId}_columns`, JSON.stringify(visibleColumns));
      localStorage.setItem(`roadshowFunnel_${selectedRoadshowId}_columnOrder`, JSON.stringify(columnOrder));
    } catch (err) {
      console.error('Failed to save settings to localStorage:', err);
    }
  }

  // Reactive statements to save settings
  $: if (initialized && (sortFields || sortDirections)) saveSettings();
  $: if (initialized && visibleColumns) saveSettings();
  $: if (initialized && columnOrder) saveSettings();

  onMount(async () => {
    await loadData();
  });

  async function loadData() {
    try {
      loading = true;

      // Load roadshows and funds in parallel
      const [loadedRoadshows, loadedFunds] = await Promise.all([
        fetchRoadshows(),
        fetchFunds()
      ]);

      roadshowList = loadedRoadshows;
      $roadshows = loadedRoadshows;
      $funds = loadedFunds;

      // Select first roadshow if available
      if (roadshowList.length > 0 && !selectedRoadshowId) {
        selectedRoadshowId = roadshowList[0].id!;
        loadSettings();
        initialized = true;
        await loadFunnelData();
      }

      loading = false;
    } catch (err) {
      console.error("Failed to load roadshow data:", err);
      loading = false;
    }
  }

  async function loadFunnelData() {
    if (!selectedRoadshowId) return;

    try {
      loadingFunnel = true;
      funnelData = await fetchRoadshowLPStatus(selectedRoadshowId);
      applySorting();
      loadingFunnel = false;
    } catch (err) {
      console.error("Failed to load roadshow LP status:", err);
      loadingFunnel = false;
    }
  }

  function updateStageCounts() {
    // Reset counts
    stages.forEach(stage => stage.count = 0);

    // Count LPs in each stage
    sortedFunnelData.forEach(item => {
      const stage = stages.find(s => s.key === item.status);
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
            case 'lp_name':
              aVal = a.lp_name || '';
              bVal = b.lp_name || '';
              break;
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

  function getStageItems(stageKey: string): RoadshowLPStatus[] {
    return sortedFunnelData.filter(item => item.status === stageKey);
  }

  function toggleStage(stageKey: string) {
    if (expandedStages.has(stageKey)) {
      expandedStages.delete(stageKey);
    } else {
      expandedStages.add(stageKey);
    }
    expandedStages = new Set(expandedStages);
  }

  async function handleStatusChange(lpItem: RoadshowLPStatus, newStatus: string) {
    if (!selectedRoadshowId) return;

    try {
      await updateLPRoadshowStatus(selectedRoadshowId, lpItem.lp_id, newStatus);
      // Reload data to update counts
      await loadFunnelData();
    } catch (err) {
      console.error("Failed to update LP status:", err);
      alert("Failed to update status");
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

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  function getCellValue(item: RoadshowLPStatus, columnKey: string): string {
    switch (columnKey) {
      case 'priority':
        return ''; // Special handling in template (editable input)
      case 'location':
        return item.location || '-';
      case 'status':
        return ''; // Special handling in template
      case 'last_contact':
        return formatDate(item.last_contact_date);
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

  async function handleRoadshowChange() {
    if (selectedRoadshowId) {
      await loadFunnelData();
    }
  }

  function createNewRoadshow() {
    selectedRoadshow = {
      name: "",
      fund_id: 0,
      lv_flight: "None",
      lv_hotel: "None",
      mty_driver: "None",
      cdmx_driver: "None"
    };
    showDetailCard = true;
  }

  function editRoadshow(roadshow: Roadshow) {
    selectedRoadshow = roadshow;
    showDetailCard = true;
  }

  async function handleRoadshowUpdated() {
    await loadData();
    if (selectedRoadshowId) {
      await loadFunnelData();
    }
    showDetailCard = false;
  }

  async function handleRoadshowCreated() {
    await loadData();
    showDetailCard = false;
  }

  function getFundName(fundId: number | undefined): string {
    if (!fundId) return "-";
    const fund = $funds.find(f => f.id === fundId);
    return fund?.fund_name || "-";
  }

  function getSelectedRoadshow(): Roadshow | undefined {
    return roadshowList.find(r => r.id === selectedRoadshowId);
  }
</script>

<div class="roadshow-funnel">
  <div class="funnel-header">
    <h2>Roadshow LP Meetings</h2>
    <button class="new-btn" on:click={createNewRoadshow}>+ New Roadshow</button>
  </div>

  {#if loading}
    <div class="loading">Loading roadshows...</div>
  {:else if roadshowList.length === 0}
    <div class="empty-state">
      <p>No roadshows created yet.</p>
      <button on:click={createNewRoadshow}>Create First Roadshow</button>
    </div>
  {:else}
    {@const selectedRoadshowData = getSelectedRoadshow()}
    <!-- Roadshow Selector -->
    <div class="roadshow-selector">
      <div class="selector-row">
        <label for="roadshow-select">Select Roadshow:</label>
        <select id="roadshow-select" bind:value={selectedRoadshowId} on:change={handleRoadshowChange}>
          {#each roadshowList as roadshow}
            <option value={roadshow.id}>{roadshow.name} - {getFundName(roadshow.fund_id)}</option>
          {/each}
        </select>
        {#if selectedRoadshowId && selectedRoadshowData}
          <button class="edit-btn" on:click={() => editRoadshow(selectedRoadshowData)}>Edit Roadshow</button>
        {/if}
      </div>

      {#if selectedRoadshowData}
        <div class="roadshow-info">
          <div class="info-item">
            <strong>Fund:</strong> {getFundName(selectedRoadshowData.fund_id)}
          </div>
          <div class="info-item">
            <strong>Arrival:</strong> {formatDate(selectedRoadshowData.arrival)} {selectedRoadshowData.arrival_city || ""}
          </div>
          {#if selectedRoadshowData.second_city}
            <div class="info-item">
              <strong>2nd City:</strong> {formatDate(selectedRoadshowData.second_arrival)} {selectedRoadshowData.second_city}
            </div>
          {/if}
          {#if selectedRoadshowData.departure}
            <div class="info-item">
              <strong>Departure:</strong> {formatDate(selectedRoadshowData.departure)}
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- LP Meeting Status Funnel -->
    {#if loadingFunnel}
      <div class="loading">Loading LP meeting status...</div>
    {:else}
      <!-- Toolbar with Sort and Column Controls -->
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

      <!-- Funnel Stages with Table Layout -->
      <div class="funnel-stages">
        {#each stages as stage}
          <div class="stage-section" style="border-left: 4px solid {stage.color}">
            <button
              class="stage-header-btn"
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
                            <td class="lp-name">{item.lp_name}</td>
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
                                  {:else if column.key === 'status'}
                                    <select
                                      class="status-select"
                                      value={item.status}
                                      on:change={(e) => handleStatusChange(item, e.currentTarget.value)}
                                    >
                                      {#each stages as stageOption}
                                        <option value={stageOption.key}>{stageOption.label}</option>
                                      {/each}
                                    </select>
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
  {/if}
</div>

{#if showDetailCard && selectedRoadshow}
  <RoadshowDetailCard
    roadshow={selectedRoadshow}
    isNew={!selectedRoadshow.id}
    on:updated={handleRoadshowUpdated}
    on:created={handleRoadshowCreated}
    on:close={() => showDetailCard = false}
  />
{/if}

<style>
  .roadshow-funnel {
    padding: 1rem;
    height: 100%;
    overflow-y: auto;
    background: white;
  }

  .funnel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .funnel-header h2 {
    margin: 0;
    color: #2c3e50;
  }

  .new-btn {
    padding: 0.75rem 1.5rem;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.2s;
  }

  .new-btn:hover {
    background: #229954;
  }

  .loading, .empty-state {
    text-align: center;
    padding: 3rem;
    color: #7f8c8d;
    font-size: 1.1rem;
  }

  .empty-state button {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
  }

  .roadshow-selector {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .selector-row {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1rem;
  }

  .selector-row label {
    font-weight: 600;
    color: #2c3e50;
    min-width: 140px;
  }

  .selector-row select {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.95rem;
  }

  .edit-btn {
    padding: 0.5rem 1rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .edit-btn:hover {
    background: #2980b9;
  }

  .roadshow-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
    padding-top: 1rem;
    border-top: 1px solid #dee2e6;
  }

  .info-item {
    font-size: 0.9rem;
  }

  .info-item strong {
    color: #666;
    margin-right: 0.5rem;
  }

  /* Toolbar Styles */
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

  /* Funnel Stages - Table Layout */
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

  .stage-header-btn {
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

  .stage-header-btn:hover {
    background: #e9ecef;
  }

  .stage-header-btn.expanded {
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

  .status-select {
    padding: 0.25rem 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.85rem;
    background: white;
    cursor: pointer;
  }

  .status-select:focus {
    outline: none;
    border-color: #3498db;
  }
</style>
