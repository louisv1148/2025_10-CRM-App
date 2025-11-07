<script lang="ts">
  import { onMount } from "svelte";
  import { fetchGPs, deleteGP, type GP } from "../lib/api";
  import GPDetailCard from "./GPDetailCard.svelte";

  let allGPs: GP[] = [];
  let filteredGPs: GP[] = [];
  let loading = true;

  // Detail card state
  let selectedGP: GP | null = null;
  let showDetailCard = false;

  // Search
  let searchQuery = "";

  // Filter
  let showFilterMenu = false;
  let activeFilters: {[key: string]: string[]} = {};
  let availableFilters = {
    contact_level: [] as string[],
    location: [] as string[]
  };

  // Sort
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility and order
  let showColumnsMenu = false;
  let visibleColumns = {
    location: true,
    contact_level: true,
    flagship_strategy: true,
    other_strategies: true,
    note: true
  };

  // Column order and metadata
  let columnOrder = [
    { key: 'location', label: 'Location' },
    { key: 'contact_level', label: 'Contact Level' },
    { key: 'flagship_strategy', label: 'Flagship Strategy' },
    { key: 'other_strategies', label: 'Other Strategies' },
    { key: 'note', label: 'Note' }
  ];

  // Initialization flag
  let initialized = false;

  // Load settings from localStorage
  function loadSettings() {
    try {
      const savedFilters = localStorage.getItem('gpDatabase_filters');
      const savedSort = localStorage.getItem('gpDatabase_sort');
      const savedColumns = localStorage.getItem('gpDatabase_columns');
      const savedColumnOrder = localStorage.getItem('gpDatabase_columnOrder');

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
      localStorage.setItem('gpDatabase_filters', JSON.stringify(activeFilters));
      localStorage.setItem('gpDatabase_sort', JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem('gpDatabase_columns', JSON.stringify(visibleColumns));
      localStorage.setItem('gpDatabase_columnOrder', JSON.stringify(columnOrder));
    } catch (err) {
      console.error('Failed to save settings to localStorage:', err);
    }
  }

  // Reactive statements to save settings when they change (only after initialization)
  $: if (initialized && activeFilters) saveSettings();
  $: if (initialized && (sortFields || sortDirections)) saveSettings();
  $: if (initialized && visibleColumns) saveSettings();
  $: if (initialized && columnOrder) saveSettings();

  onMount(async () => {
    loadSettings();
    initialized = true;
    try {
      allGPs = await fetchGPs();

      // Extract unique values for filters
      const contactLevels = new Set<string>();
      const locations = new Set<string>();

      allGPs.forEach(gp => {
        if (gp.contact_level) contactLevels.add(gp.contact_level);
        if (gp.location) {
          // Handle comma-separated locations
          gp.location.split(',').forEach(loc => locations.add(loc.trim()));
        }
      });

      availableFilters.contact_level = Array.from(contactLevels).sort();
      availableFilters.location = Array.from(locations).sort();

      applyFiltersAndSort();
      loading = false;
    } catch (err) {
      console.error("Failed to load GPs:", err);
      loading = false;
    }
  });

  function applyFiltersAndSort() {
    let result = [...allGPs];

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(gp =>
        gp.name.toLowerCase().includes(query)
      );
    }

    // Apply filters
    Object.entries(activeFilters).forEach(([field, values]) => {
      if (values.length > 0) {
        result = result.filter(gp => {
          const gpValue = gp[field as keyof GP];
          if (!gpValue) return false;

          // Handle comma-separated values (like location)
          if (field === 'location' && typeof gpValue === 'string') {
            const gpLocations = gpValue.split(',').map(l => l.trim());
            return values.some(v => gpLocations.includes(v));
          }

          return values.includes(String(gpValue));
        });
      }
    });

    // Apply sort
    if (sortFields.length > 0) {
      result.sort((a, b) => {
        for (const field of sortFields) {
          const aVal = a[field as keyof GP] || '';
          const bVal = b[field as keyof GP] || '';
          const direction = sortDirections[field] === 'desc' ? -1 : 1;

          if (aVal < bVal) return -1 * direction;
          if (aVal > bVal) return 1 * direction;
        }
        return 0;
      });
    }

    filteredGPs = result;
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

  // Reactive statement to update when search changes
  $: if (searchQuery !== undefined) {
    applyFiltersAndSort();
  }

  function getActiveFilterCount(): number {
    return Object.values(activeFilters).reduce((sum, arr) => sum + arr.length, 0);
  }

  function getFieldLabel(field: string): string {
    const labels: {[key: string]: string} = {
      'name': 'Name',
      'location': 'Location',
      'contact_level': 'Contact Level',
      'flagship_strategy': 'Flagship Strategy'
    };
    return labels[field] || field;
  }

  // Column reordering functions
  function moveColumnUp(index: number) {
    if (index === 0) return; // Already at top

    // Swap with the item above
    [columnOrder[index - 1], columnOrder[index]] = [columnOrder[index], columnOrder[index - 1]];

    // Force Svelte to detect the change by creating a new array reference
    columnOrder = [...columnOrder];
  }

  function moveColumnDown(index: number) {
    if (index === columnOrder.length - 1) return; // Already at bottom

    // Swap with the item below
    [columnOrder[index], columnOrder[index + 1]] = [columnOrder[index + 1], columnOrder[index]];

    // Force Svelte to detect the change by creating a new array reference
    columnOrder = [...columnOrder];
  }

  // Get cell value based on column key
  function getCellValue(gp: GP, columnKey: string): string {
    switch (columnKey) {
      case 'location':
        return gp.location || '-';
      case 'contact_level':
        return gp.contact_level || '-';
      case 'flagship_strategy':
        return gp.flagship_strategy || '-';
      case 'other_strategies':
        return gp.other_strategies || '-';
      case 'note':
        return gp.note || '-';
      default:
        return '-';
    }
  }

  // Detail card functions
  function openDetailCard(gp: GP) {
    selectedGP = gp;
    showDetailCard = true;
  }

  function closeDetailCard() {
    selectedGP = null;
    showDetailCard = false;
  }

  function handleEdit(event: CustomEvent) {
    const gp = event.detail;
    console.log("Edit GP:", gp);
    // TODO: Implement edit functionality
    alert("Edit functionality coming soon!");
  }

  async function handleDelete(event: CustomEvent) {
    const gpId = event.detail;
    try {
      await deleteGP(gpId);
      // Refresh the list
      allGPs = await fetchGPs();
      applyFiltersAndSort();
      closeDetailCard();
    } catch (err) {
      console.error("Failed to delete GP:", err);
      alert("Failed to delete GP");
    }
  }
</script>

<div class="gp-database-view">
  <div class="header">
    <h2>GPs</h2>
    <div class="results-count">
      {filteredGPs.length} of {allGPs.length} records
    </div>
  </div>

  <div class="toolbar">
    <div class="search-bar">
      <input
        type="text"
        placeholder="Search by name..."
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
            <h5>Contact Level</h5>
            {#each availableFilters.contact_level as level}
              <label>
                <input
                  type="checkbox"
                  checked={activeFilters.contact_level?.includes(level)}
                  on:change={() => toggleFilter('contact_level', level)}
                />
                {level}
              </label>
            {/each}
          </div>

          <div class="filter-section">
            <h5>Location</h5>
            {#each availableFilters.location as location}
              <label>
                <input
                  type="checkbox"
                  checked={activeFilters.location?.includes(location)}
                  on:change={() => toggleFilter('location', location)}
                />
                {location}
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
            <button on:click={() => addSortField('name')}>+ Name</button>
            <button on:click={() => addSortField('location')}>+ Location</button>
            <button on:click={() => addSortField('contact_level')}>+ Contact Level</button>
            <button on:click={() => addSortField('flagship_strategy')}>+ Flagship Strategy</button>
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
      <div class="loading">Loading GPs...</div>
    {:else}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Location</th>
            <th>Contact Level</th>
            <th>Flagship Strategy</th>
            <th>Last Contact</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredGPs as gp}
            <tr on:click={() => openDetailCard(gp)}>
              <td class="name-cell">{gp.name}</td>
              <td>{gp.location || "-"}</td>
              <td>{gp.contact_level || "-"}</td>
              <td>{gp.flagship_strategy || "-"}</td>
              <td>-</td>
            </tr>
          {/each}
        </tbody>
      </table>

      {#if filteredGPs.length === 0}
        <div class="no-results">
          No GPs match your search and filters
        </div>
      {/if}
    {/if}
  </div>

  <!-- GP Detail Card Modal -->
  {#if showDetailCard && selectedGP}
    <GPDetailCard
      gp={selectedGP}
      on:close={closeDetailCard}
      on:edit={handleEdit}
      on:delete={handleDelete}
    />
  {/if}
</div>

<style>
  .gp-database-view {
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
  .sort-container {
    position: relative;
  }

  .filter-btn,
  .sort-btn {
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
  .sort-btn:hover {
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
  .sort-menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 250px;
    max-height: 400px;
    overflow-y: auto;
  }

  .filter-header,
  .sort-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #e0e0e0;
  }

  .filter-header h4,
  .sort-header h4 {
    margin: 0;
    font-size: 1rem;
    color: #2c3e50;
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

  .table-container {
    flex: 1;
    overflow-y: auto;
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
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    color: #555;
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
</style>
