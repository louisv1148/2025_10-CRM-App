<script lang="ts">
  import { onMount } from "svelte";
  import { fetchFunds, fetchGPs, type Fund, type GP } from "../lib/api";
  import FundDetailCard from "./FundDetailCard.svelte";

  let allFunds: Fund[] = [];
  let filteredFunds: Fund[] = [];
  let loading = true;

  // GP lookup map (gp_notion_id -> GP name)
  let gpLookup: Map<string, string> = new Map();

  // Detail card state
  let selectedFund: Fund | null = null;
  let showDetailCard = false;
  let isNewEntry = false;

  // Search
  let searchQuery = "";

  // Filter
  let showFilterMenu = false;
  let activeFilters: {[key: string]: string[]} = {};
  let availableFilters = {
    status: [] as string[],
    geography: [] as string[],
    asset_class: [] as string[],
    potential: [] as string[]
  };

  // Sort
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility
  let showColumnsMenu = false;
  let visibleColumns = {
    geography: true,
    status: true,
    asset_class: true,
    target_mn: true,
    hard_cap_mn: true,
    launch: true,
    final_close: true,
    target_irr: true,
    target_multiple: true,
    potential: true,
    roadshow_date: true,
    gp: true
  };

  // Column order and metadata
  let columnOrder = [
    { key: 'geography', label: 'Geography' },
    { key: 'status', label: 'Status' },
    { key: 'asset_class', label: 'Asset Class' },
    { key: 'target_mn', label: 'Target ($M)' },
    { key: 'hard_cap_mn', label: 'Hard Cap ($M)' },
    { key: 'launch', label: 'Launch' },
    { key: 'final_close', label: 'Final Close' },
    { key: 'target_irr', label: 'Target IRR' },
    { key: 'target_multiple', label: 'Target Multiple' },
    { key: 'potential', label: 'Potential' },
    { key: 'roadshow_date', label: 'Roadshow Date' },
    { key: 'gp', label: 'GP' }
  ];

  let initialized = false;

  // Load settings from localStorage
  function loadSettings() {
    try {
      const savedFilters = localStorage.getItem('fundDatabase_filters');
      const savedSort = localStorage.getItem('fundDatabase_sort');
      const savedColumns = localStorage.getItem('fundDatabase_columns');
      const savedColumnOrder = localStorage.getItem('fundDatabase_columnOrder');

      if (savedFilters) {
        activeFilters = JSON.parse(savedFilters);
      }

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
      localStorage.setItem('fundDatabase_filters', JSON.stringify(activeFilters));
      localStorage.setItem('fundDatabase_sort', JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem('fundDatabase_columns', JSON.stringify(visibleColumns));
      localStorage.setItem('fundDatabase_columnOrder', JSON.stringify(columnOrder));
    } catch (err) {
      console.error('Failed to save settings to localStorage:', err);
    }
  }

  // Reactive statements to save settings
  $: if (initialized && activeFilters) saveSettings();
  $: if (initialized && (sortFields || sortDirections)) saveSettings();
  $: if (initialized && visibleColumns) saveSettings();
  $: if (initialized && columnOrder) saveSettings();

  onMount(async () => {
    loadSettings();
    initialized = true;
    try {
      // Fetch funds and GPs in parallel
      const [funds, gps] = await Promise.all([fetchFunds(), fetchGPs()]);
      allFunds = funds;

      // Build GP lookup map
      gps.forEach(gp => {
        if (gp.notion_id) {
          gpLookup.set(gp.notion_id, gp.name);
        }
      });

      // Extract unique values for filters
      const statuses = new Set<string>();
      const geographies = new Set<string>();
      const assetClasses = new Set<string>();
      const potentials = new Set<string>();

      allFunds.forEach(fund => {
        if (fund.status) statuses.add(fund.status);
        if (fund.geography) geographies.add(fund.geography);
        if (fund.asset_class) assetClasses.add(fund.asset_class);
        if (fund.potential) potentials.add(fund.potential);
      });

      availableFilters.status = Array.from(statuses).sort();
      availableFilters.geography = Array.from(geographies).sort();
      availableFilters.asset_class = Array.from(assetClasses).sort();
      availableFilters.potential = Array.from(potentials).sort();

      applyFiltersAndSort();
      loading = false;
    } catch (err) {
      console.error("Failed to load funds:", err);
      loading = false;
    }
  });

  function applyFiltersAndSort() {
    let result = [...allFunds];

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(fund =>
        fund.fund_name.toLowerCase().includes(query)
      );
    }

    // Apply filters
    Object.entries(activeFilters).forEach(([field, values]) => {
      if (values.length > 0) {
        result = result.filter(fund => {
          const fundValue = fund[field as keyof Fund];
          if (!fundValue) return false;
          return values.includes(String(fundValue));
        });
      }
    });

    // Apply sort
    if (sortFields.length > 0) {
      result.sort((a, b) => {
        for (const field of sortFields) {
          const aVal = a[field as keyof Fund] || '';
          const bVal = b[field as keyof Fund] || '';
          const direction = sortDirections[field] === 'desc' ? -1 : 1;

          if (aVal < bVal) return -1 * direction;
          if (aVal > bVal) return 1 * direction;
        }
        return 0;
      });
    }

    filteredFunds = result;
  }

  function toggleFilter(field: string, value: string) {
    if (!activeFilters[field]) {
      activeFilters[field] = [];
    }

    const index = activeFilters[field].indexOf(value);
    if (index > -1) {
      activeFilters[field].splice(index, 1);
    } else {
      activeFilters[field].push(value);
    }

    activeFilters = activeFilters; // Trigger reactivity
    applyFiltersAndSort();
  }

  function clearFilters() {
    activeFilters = {};
    applyFiltersAndSort();
  }

  function addSortField(field: string) {
    if (!sortFields.includes(field)) {
      sortFields = [...sortFields, field];
      sortDirections[field] = 'asc';
      applyFiltersAndSort();
    }
  }

  function toggleSortDirection(field: string) {
    sortDirections[field] = sortDirections[field] === 'asc' ? 'desc' : 'asc';
    applyFiltersAndSort();
  }

  function removeSortField(field: string) {
    sortFields = sortFields.filter(f => f !== field);
    delete sortDirections[field];
    applyFiltersAndSort();
  }

  function clearSort() {
    sortFields = [];
    sortDirections = {};
    applyFiltersAndSort();
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

  // Get cell value based on column key
  function getCellValue(fund: Fund, columnKey: string): string {
    switch (columnKey) {
      case 'geography':
        return fund.geography || '-';
      case 'status':
        return fund.status || '-';
      case 'asset_class':
        return fund.asset_class || '-';
      case 'target_mn':
        return fund.target_mn ? `$${fund.target_mn}M` : '-';
      case 'hard_cap_mn':
        return fund.hard_cap_mn ? `$${fund.hard_cap_mn}M` : '-';
      case 'launch':
        return fund.launch ? new Date(fund.launch).toLocaleDateString() : '-';
      case 'final_close':
        return fund.final_close ? new Date(fund.final_close).toLocaleDateString() : '-';
      case 'target_irr':
        return fund.target_irr || '-';
      case 'target_multiple':
        return fund.target_multiple ? `${fund.target_multiple}x` : '-';
      case 'potential':
        return fund.potential || '-';
      case 'roadshow_date':
        return fund.roadshow_date ? new Date(fund.roadshow_date).toLocaleDateString() : '-';
      case 'gp':
        return fund.gp_notion_id ? (gpLookup.get(fund.gp_notion_id) || '-') : '-';
      default:
        return '-';
    }
  }

  // Reactive statement for search
  $: if (searchQuery !== undefined) {
    applyFiltersAndSort();
  }

  function getActiveFilterCount(): number {
    return Object.values(activeFilters).reduce((sum, arr) => sum + arr.length, 0);
  }

  function getFieldLabel(field: string): string {
    const labels: {[key: string]: string} = {
      'fund_name': 'Fund Name',
      'geography': 'Geography',
      'status': 'Status',
      'asset_class': 'Asset Class',
      'target_mn': 'Target',
      'hard_cap_mn': 'Hard Cap',
      'potential': 'Potential'
    };
    return labels[field] || field;
  }

  // Detail card handlers
  function openDetailCard(fund: Fund) {
    selectedFund = fund;
    isNewEntry = false;
    showDetailCard = true;
  }

  function openNewEntryCard() {
    // Create a blank Fund object
    selectedFund = {
      fund_name: '',
      geography: '',
      status: '',
      asset_class: '',
      target_mn: undefined,
      hard_cap_mn: undefined,
      launch: '',
      final_close: '',
      target_irr: '',
      target_multiple: undefined,
      potential: '',
      roadshow_date: '',
      sectors: '',
      note: '',
      current_lps: '',
      roadshows: '',
      closed: false,
      gp_notion_id: ''
    } as Fund;
    isNewEntry = true;
    showDetailCard = true;
  }

  function closeDetailCard() {
    showDetailCard = false;
    isNewEntry = false;
    selectedFund = null;
  }

  function handleFundCreated(event: CustomEvent<Fund>) {
    const created = event.detail;
    if (!created?.id) return;

    // Add the new fund to the array
    allFunds = [...allFunds, created];
    console.log("Added new fund to allFunds array:", created);

    // Reapply filters and sort
    applyFiltersAndSort();
  }

  function handleFundUpdated(event: CustomEvent<Fund>) {
    console.log("handleFundUpdated called, event detail:", event.detail);

    const updated = event.detail;
    if (!updated?.id) return;

    // Update the fund in the allFunds array
    const index = allFunds.findIndex(f => f.id === updated.id);
    if (index !== -1) {
      allFunds[index] = updated;
      allFunds = [...allFunds];
      console.log("Updated fund in allFunds array at index", index);
    }

    // Update selectedFund to reflect changes in the detail card
    selectedFund = updated;

    // Reapply filters and sort
    applyFiltersAndSort();
  }
</script>

<div class="fund-database-view">
  <div class="header">
    <h2>Funds</h2>
    <div class="header-actions">
      <button class="new-entry-btn" on:click={openNewEntryCard}>+ New Entry</button>
      <div class="results-count">
        {filteredFunds.length} of {allFunds.length} records
      </div>
    </div>
  </div>

  <div class="toolbar">
    <div class="search-bar">
      <input
        type="text"
        placeholder="Search by fund name..."
        bind:value={searchQuery}
      />
    </div>

    <div class="filter-container">
      <button
        class="filter-btn"
        class:active={getActiveFilterCount() > 0}
        on:click={() => showFilterMenu = !showFilterMenu}
      >
        Filter
        {#if getActiveFilterCount() > 0}
          <span class="badge">{getActiveFilterCount()}</span>
        {/if}
      </button>

      {#if showFilterMenu}
        <div class="filter-menu">
          <div class="filter-header">
            <h4>Filter by</h4>
            <button class="clear-btn" on:click={clearFilters}>Clear all</button>
          </div>

          <div class="filter-section">
            <h5>Status</h5>
            {#each availableFilters.status as status}
              <label>
                <input
                  type="checkbox"
                  checked={activeFilters.status?.includes(status)}
                  on:change={() => toggleFilter('status', status)}
                />
                {status}
              </label>
            {/each}
          </div>

          <div class="filter-section">
            <h5>Geography</h5>
            {#each availableFilters.geography as geography}
              <label>
                <input
                  type="checkbox"
                  checked={activeFilters.geography?.includes(geography)}
                  on:change={() => toggleFilter('geography', geography)}
                />
                {geography}
              </label>
            {/each}
          </div>

          <div class="filter-section">
            <h5>Asset Class</h5>
            {#each availableFilters.asset_class as assetClass}
              <label>
                <input
                  type="checkbox"
                  checked={activeFilters.asset_class?.includes(assetClass)}
                  on:change={() => toggleFilter('asset_class', assetClass)}
                />
                {assetClass}
              </label>
            {/each}
          </div>

          <div class="filter-section">
            <h5>Potential</h5>
            {#each availableFilters.potential as potential}
              <label>
                <input
                  type="checkbox"
                  checked={activeFilters.potential?.includes(potential)}
                  on:change={() => toggleFilter('potential', potential)}
                />
                {potential}
              </label>
            {/each}
          </div>
        </div>
      {/if}
    </div>

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
            <button on:click={() => addSortField('fund_name')}>+ Fund Name</button>
            <button on:click={() => addSortField('geography')}>+ Geography</button>
            <button on:click={() => addSortField('status')}>+ Status</button>
            <button on:click={() => addSortField('target_mn')}>+ Target</button>
            <button on:click={() => addSortField('roadshow_date')}>+ Roadshow Date</button>
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

  <div class="table-container">
    {#if loading}
      <div class="loading">Loading Funds...</div>
    {:else}
      <table>
        <thead>
          <tr>
            <th>Fund Name</th>
            {#each columnOrder as column}
              {#if visibleColumns[column.key]}
                <th>{column.label}</th>
              {/if}
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each filteredFunds as fund}
            <tr on:click={() => openDetailCard(fund)} class="clickable-row">
              <td class="name-cell">{fund.fund_name}</td>
              {#each columnOrder as column}
                {#if visibleColumns[column.key]}
                  <td>{getCellValue(fund, column.key)}</td>
                {/if}
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>

      {#if filteredFunds.length === 0}
        <div class="no-results">
          No funds match your search and filters
        </div>
      {/if}
    {/if}
  </div>
</div>

{#if showDetailCard && selectedFund}
  <FundDetailCard
    fund={selectedFund}
    isNew={isNewEntry}
    on:close={closeDetailCard}
    on:created={handleFundCreated}
    on:updated={handleFundUpdated}
  />
{/if}

<style>
  .fund-database-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: white;
  }

  .header {
    padding: 1.5rem 2rem;
    border-bottom: 2px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h2 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.75rem;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .new-entry-btn {
    padding: 0.5rem 1rem;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: background 0.2s;
  }

  .new-entry-btn:hover {
    background: #229954;
  }

  .results-count {
    color: #666;
    font-size: 0.9rem;
  }

  .toolbar {
    display: flex;
    gap: 1rem;
    padding: 1rem 2rem;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
  }

  .search-bar {
    flex: 1;
  }

  .search-bar input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.95rem;
  }

  .search-bar input:focus {
    outline: none;
    border-color: #3498db;
  }

  .filter-container,
  .sort-container,
  .columns-container {
    position: relative;
  }

  .filter-btn,
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

  .filter-btn:hover,
  .sort-btn:hover,
  .columns-btn:hover {
    border-color: #3498db;
    background: #f0f8ff;
  }

  .filter-btn.active,
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

  .filter-btn.active .badge,
  .sort-btn.active .badge {
    background: #2980b9;
    color: white;
  }

  .filter-menu,
  .sort-menu,
  .columns-menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 250px;
    max-height: 70vh;
    overflow-y: auto;
  }

  .filter-header,
  .sort-header,
  .columns-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
  }

  .filter-header h4,
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

  .filter-section {
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
  }

  .filter-section:last-child {
    border-bottom: none;
  }

  .filter-section h5 {
    margin: 0 0 0.5rem 0;
    font-size: 0.85rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .filter-section label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0;
    cursor: pointer;
  }

  .filter-section input[type="checkbox"] {
    cursor: pointer;
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

  .table-container {
    flex: 1;
    overflow: auto;
    padding: 0 2rem 2rem 2rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  thead {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
  }

  th {
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 2px solid #e0e0e0;
    font-weight: 600;
    color: #2c3e50;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    min-width: 120px;
    white-space: nowrap;
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    color: #555;
    min-width: 120px;
  }

  .name-cell {
    font-weight: 500;
    color: #2c3e50;
  }

  tbody tr {
    transition: background 0.2s;
  }

  tbody tr:hover {
    background: #f8f9fa;
    cursor: pointer;
  }

  .loading,
  .no-results {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: #999;
    font-size: 1.1rem;
  }

  /* Custom Scrollbar Styling */
  .table-container::-webkit-scrollbar {
    width: 12px;
    height: 12px;
  }

  .table-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb:hover {
    background: #555;
  }

  .table-container::-webkit-scrollbar-corner {
    background: #f1f1f1;
  }
</style>
