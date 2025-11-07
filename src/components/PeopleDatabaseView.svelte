<script lang="ts">
  import { onMount } from "svelte";
  import { fetchPeople, fetchPersonLPs, fetchPersonGPs, type Person, type LP, type GP } from "../lib/api";
  import PersonDetailCard from "./PersonDetailCard.svelte";

  let allPeople: Person[] = [];
  let filteredPeople: Person[] = [];
  let loading = true;

  // Map to store related firm names for each person
  let personFirms: Map<number, string> = new Map();

  // Detail card state
  let selectedPerson: Person | null = null;
  let showDetailCard = false;

  // Search
  let searchQuery = "";

  // Filter
  let showFilterMenu = false;
  let activeFilters: {[key: string]: string[]} = {};
  let availableFilters = {
    people_type: [] as string[],
    org_type: [] as string[],
    location: [] as string[]
  };

  // Sort
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility and order
  let showColumnsMenu = false;
  let visibleColumns = {
    position: true,
    people_type: true,
    org_type: true,
    location: true,
    email: true,
    phone: true,
    related_firm: true
  };

  // Column order and metadata
  let columnOrder = [
    { key: 'position', label: 'Position' },
    { key: 'people_type', label: 'Type' },
    { key: 'org_type', label: 'Org Type' },
    { key: 'location', label: 'Location' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'related_firm', label: 'Related Firm' }
  ];

  // Drag and drop state
  let draggedColumnIndex: number | null = null;
  let initialized = false;

  // Load settings from localStorage
  function loadSettings() {
    try {
      const savedFilters = localStorage.getItem('peopleDatabase_filters');
      const savedSort = localStorage.getItem('peopleDatabase_sort');
      const savedColumns = localStorage.getItem('peopleDatabase_columns');
      const savedColumnOrder = localStorage.getItem('peopleDatabase_columnOrder');

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
      localStorage.setItem('peopleDatabase_filters', JSON.stringify(activeFilters));
      localStorage.setItem('peopleDatabase_sort', JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem('peopleDatabase_columns', JSON.stringify(visibleColumns));
      localStorage.setItem('peopleDatabase_columnOrder', JSON.stringify(columnOrder));
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
      allPeople = await fetchPeople();

      // Fetch related firms for each person
      const firmPromises = allPeople.map(async (person) => {
        if (!person.id) return;

        try {
          const [lps, gps] = await Promise.all([
            fetchPersonLPs(person.id),
            fetchPersonGPs(person.id)
          ]);

          // Prefer LP, fall back to GP
          if (lps && lps.length > 0) {
            personFirms.set(person.id, lps.map(lp => lp.name).join(', '));
          } else if (gps && gps.length > 0) {
            personFirms.set(person.id, gps.map(gp => gp.name).join(', '));
          }
        } catch (err) {
          console.error(`Failed to load firms for person ${person.id}:`, err);
        }
      });

      await Promise.all(firmPromises);
      personFirms = personFirms; // Trigger reactivity

      // Extract unique values for filters
      const types = new Set<string>();
      const orgTypes = new Set<string>();
      const locations = new Set<string>();

      allPeople.forEach(person => {
        if (person.people_type) types.add(person.people_type);
        if (person.org_type) orgTypes.add(person.org_type);
        if (person.location) locations.add(person.location);
      });

      availableFilters.people_type = Array.from(types).sort();
      availableFilters.org_type = Array.from(orgTypes).sort();
      availableFilters.location = Array.from(locations).sort();

      applyFiltersAndSort();
      loading = false;
    } catch (err) {
      console.error("Failed to load people:", err);
      loading = false;
    }
  });

  function applyFiltersAndSort() {
    let result = [...allPeople];

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(person =>
        person.name.toLowerCase().includes(query) ||
        person.email?.toLowerCase().includes(query) ||
        person.position?.toLowerCase().includes(query)
      );
    }

    // Apply filters
    Object.entries(activeFilters).forEach(([field, values]) => {
      if (values.length > 0) {
        result = result.filter(person => {
          const personValue = person[field as keyof Person];
          if (!personValue) return false;
          return values.includes(String(personValue));
        });
      }
    });

    // Apply sort
    if (sortFields.length > 0) {
      result.sort((a, b) => {
        for (const field of sortFields) {
          const aVal = a[field as keyof Person] || '';
          const bVal = b[field as keyof Person] || '';
          const direction = sortDirections[field] === 'desc' ? -1 : 1;

          if (aVal < bVal) return -1 * direction;
          if (aVal > bVal) return 1 * direction;
        }
        return 0;
      });
    }

    filteredPeople = result;
  }

  // Search handler
  $: {
    searchQuery;
    applyFiltersAndSort();
  }

  // Filter functions
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

    activeFilters = { ...activeFilters };
    applyFiltersAndSort();
  }

  function clearFilters() {
    activeFilters = {};
    applyFiltersAndSort();
  }

  // Sort functions
  function toggleSort(field: string) {
    const index = sortFields.indexOf(field);

    if (index > -1) {
      // Field already sorted, toggle direction or remove
      if (sortDirections[field] === 'asc') {
        sortDirections[field] = 'desc';
      } else {
        sortFields.splice(index, 1);
        delete sortDirections[field];
      }
    } else {
      // Add new sort field
      sortFields.push(field);
      sortDirections[field] = 'asc';
    }

    sortFields = [...sortFields];
    applyFiltersAndSort();
  }

  function clearSort() {
    sortFields = [];
    sortDirections = {};
    applyFiltersAndSort();
  }

  // Column reordering handlers - using arrow buttons
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
  function getCellValue(person: Person, columnKey: string): string {
    switch (columnKey) {
      case 'position':
        return person.position || '-';
      case 'people_type':
        return person.people_type || '-';
      case 'org_type':
        return person.org_type || '-';
      case 'location':
        return person.location || '-';
      case 'email':
        return person.email || '-';
      case 'phone':
        return person.phone || '-';
      case 'related_firm':
        return person.id ? (personFirms.get(person.id) || '-') : '-';
      default:
        return '-';
    }
  }

  // Detail card handlers
  function openDetailCard(person: Person) {
    selectedPerson = person;
    showDetailCard = true;
  }

  function closeDetailCard() {
    showDetailCard = false;
    selectedPerson = null;
  }

  // Count active filters
  $: activeFilterCount = Object.values(activeFilters).reduce((sum, arr) => sum + arr.length, 0);
</script>

<div class="database-view">
  <div class="header">
    <h1>People Database</h1>
    <div class="header-stats">
      {filteredPeople.length} of {allPeople.length} people
    </div>
  </div>

  <div class="controls">
    <div class="search-bar">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search people by name, email, or position..."
        class="search-input"
      />
    </div>

    <div class="action-buttons">
      <button class="btn btn-filter" on:click={() => showFilterMenu = !showFilterMenu}>
        Filter {activeFilterCount > 0 ? `(${activeFilterCount})` : ''}
      </button>
      <button class="btn btn-sort" on:click={() => showSortMenu = !showSortMenu}>
        Sort {sortFields.length > 0 ? `(${sortFields.length})` : ''}
      </button>
      <button class="btn btn-columns" on:click={() => showColumnsMenu = !showColumnsMenu}>
        Columns
      </button>
    </div>
  </div>

  {#if showFilterMenu}
    <div class="filter-panel">
      <div class="filter-header">
        <h3>Filters</h3>
        <button class="btn-clear" on:click={clearFilters}>Clear All</button>
      </div>

      <div class="filter-groups">
        <div class="filter-group">
          <h4>Type</h4>
          <div class="filter-options">
            {#each availableFilters.people_type as type}
              <label class="filter-option">
                <input
                  type="checkbox"
                  checked={activeFilters.people_type?.includes(type)}
                  on:change={() => toggleFilter('people_type', type)}
                />
                <span>{type}</span>
              </label>
            {/each}
          </div>
        </div>

        <div class="filter-group">
          <h4>Organization Type</h4>
          <div class="filter-options">
            {#each availableFilters.org_type as orgType}
              <label class="filter-option">
                <input
                  type="checkbox"
                  checked={activeFilters.org_type?.includes(orgType)}
                  on:change={() => toggleFilter('org_type', orgType)}
                />
                <span>{orgType}</span>
              </label>
            {/each}
          </div>
        </div>

        <div class="filter-group">
          <h4>Location</h4>
          <div class="filter-options">
            {#each availableFilters.location as location}
              <label class="filter-option">
                <input
                  type="checkbox"
                  checked={activeFilters.location?.includes(location)}
                  on:change={() => toggleFilter('location', location)}
                />
                <span>{location}</span>
              </label>
            {/each}
          </div>
        </div>
      </div>
    </div>
  {/if}

  {#if showSortMenu}
    <div class="sort-panel">
      <div class="sort-header">
        <h3>Sort</h3>
        <button class="btn-clear" on:click={clearSort}>Clear All</button>
      </div>

      <div class="sort-options">
        <button
          class="sort-option {sortFields.includes('name') ? 'active' : ''}"
          on:click={() => toggleSort('name')}
        >
          Name
          {#if sortFields.includes('name')}
            <span class="sort-indicator">{sortDirections['name'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

        <button
          class="sort-option {sortFields.includes('position') ? 'active' : ''}"
          on:click={() => toggleSort('position')}
        >
          Position
          {#if sortFields.includes('position')}
            <span class="sort-indicator">{sortDirections['position'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

        <button
          class="sort-option {sortFields.includes('location') ? 'active' : ''}"
          on:click={() => toggleSort('location')}
        >
          Location
          {#if sortFields.includes('location')}
            <span class="sort-indicator">{sortDirections['location'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

        <button
          class="sort-option {sortFields.includes('people_type') ? 'active' : ''}"
          on:click={() => toggleSort('people_type')}
        >
          Type
          {#if sortFields.includes('people_type')}
            <span class="sort-indicator">{sortDirections['people_type'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>
      </div>
    </div>
  {/if}

  {#if showColumnsMenu}
    <div class="columns-panel">
      <div class="columns-header">
        <h3>Visible Columns</h3>
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

  {#if loading}
    <div class="loading">Loading people...</div>
  {:else}
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            {#each columnOrder as column}
              {#if visibleColumns[column.key]}
                <th>{column.label}</th>
              {/if}
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each filteredPeople as person}
            <tr on:click={() => openDetailCard(person)} class="clickable-row">
              <td class="name-cell">{person.name}</td>
              {#each columnOrder as column}
                {#if visibleColumns[column.key]}
                  <td class="{column.key === 'email' ? 'email-cell' : ''}">{getCellValue(person, column.key)}</td>
                {/if}
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

{#if showDetailCard && selectedPerson}
  <PersonDetailCard person={selectedPerson} on:close={closeDetailCard} />
{/if}

<style>
  .database-view {
    padding: 2rem;
    max-width: 1600px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  h1 {
    margin: 0;
    color: #2c3e50;
    font-size: 2rem;
  }

  .header-stats {
    color: #666;
    font-size: 1rem;
  }

  .controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    align-items: center;
  }

  .search-bar {
    flex: 1;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }

  .search-input:focus {
    outline: none;
    border-color: #3498db;
  }

  .action-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s;
  }

  .btn:hover {
    background: #f8f9fa;
    border-color: #3498db;
  }

  .btn-filter {
    background: #3498db;
    color: white;
    border-color: #3498db;
  }

  .btn-filter:hover {
    background: #2980b9;
  }

  .btn-sort {
    background: #27ae60;
    color: white;
    border-color: #27ae60;
  }

  .btn-sort:hover {
    background: #229954;
  }

  .btn-columns {
    background: #9b59b6;
    color: white;
    border-color: #9b59b6;
  }

  .btn-columns:hover {
    background: #8e44ad;
  }

  /* Filter Panel, Sort Panel, Columns Panel */
  .filter-panel, .sort-panel, .columns-panel {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .filter-header, .sort-header, .columns-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .filter-header h3, .sort-header h3, .columns-header h3 {
    margin: 0;
    font-size: 1.2rem;
    color: #2c3e50;
  }

  .btn-clear {
    padding: 0.5rem 1rem;
    border: 1px solid #e74c3c;
    border-radius: 4px;
    background: white;
    color: #e74c3c;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .btn-clear:hover {
    background: #e74c3c;
    color: white;
  }

  .filter-groups {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .filter-group h4 {
    margin: 0 0 0.75rem 0;
    color: #555;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .filter-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 200px;
    overflow-y: auto;
  }

  .filter-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.25rem;
  }

  .filter-option:hover {
    background: #f8f9fa;
  }

  .filter-option input[type="checkbox"] {
    cursor: pointer;
  }

  /* Columns Panel */
  .columns-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .column-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 4px;
    transition: all 0.2s;
    border: 2px solid #e0e0e0;
    background: white;
  }

  .column-option:hover {
    background: #f8f9fa;
    border-color: #9b59b6;
  }

  .column-option input[type="checkbox"] {
    cursor: pointer;
  }

  .reorder-buttons {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .reorder-btn {
    width: 24px;
    height: 20px;
    padding: 0;
    border: 1px solid #ddd;
    background: white;
    cursor: pointer;
    font-size: 0.9rem;
    line-height: 1;
    border-radius: 3px;
    transition: all 0.2s;
    color: #666;
  }

  .reorder-btn:hover:not(:disabled) {
    background: #9b59b6;
    color: white;
    border-color: #9b59b6;
  }

  .reorder-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .drag-hint {
    font-size: 0.85rem;
    color: #666;
    font-style: italic;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
    cursor: pointer;
  }

  /* Sort Panel */
  .sort-options {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .sort-option {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
  }

  .sort-option:hover {
    background: #f8f9fa;
    border-color: #27ae60;
  }

  .sort-option.active {
    background: #27ae60;
    color: white;
    border-color: #27ae60;
  }

  .sort-indicator {
    font-weight: bold;
  }

  /* Table */
  .table-container {
    background: white;
    border-radius: 8px;
    overflow: auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-height: calc(100vh - 400px);
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
  }

  .data-table thead {
    background: #f8f9fa;
    border-bottom: 2px solid #e0e0e0;
  }

  .data-table th {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    color: #2c3e50;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
    min-width: 120px;
    white-space: nowrap;
  }

  .data-table tbody tr {
    border-bottom: 1px solid #e0e0e0;
    transition: background 0.2s;
  }

  .clickable-row {
    cursor: pointer;
  }

  .clickable-row:hover {
    background: #f8f9fa;
  }

  .data-table td {
    padding: 1rem;
    color: #555;
    min-width: 120px;
  }

  .name-cell {
    font-weight: 600;
    color: #2c3e50;
  }

  .email-cell {
    color: #3498db;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #999;
    font-size: 1.2rem;
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
