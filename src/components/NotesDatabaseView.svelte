<script lang="ts">
  import { onMount } from "svelte";
  import { fetchNotes, fetchNoteLPs, fetchNoteGPs, type Note, type LP, type GP } from "../lib/api";
  import NoteDetailCard from "./NoteDetailCard.svelte";

  let allNotes: Note[] = [];
  let filteredNotes: Note[] = [];
  let loading = true;

  // Related entities
  let noteLPs: Map<number, string> = new Map();
  let noteGPs: Map<number, string> = new Map();

  // Detail card state
  let selectedNote: Note | null = null;
  let showDetailCard = false;

  // Search
  let searchQuery = "";

  // Filter
  let showFilterMenu = false;
  let activeFilters: {[key: string]: string[]} = {};
  let availableFilters = {
    interest: [] as string[],
    fundraise: [] as string[]
  };

  // Sort
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility and order
  let showColumnsMenu = false;
  let visibleColumns = {
    date: true,
    name: true,
    interest: true,
    fundraise: true,
    summary: true,
    related_lps: true,
    related_gps: true,
    contact_type: true,
    useful: true
  };

  // Column order and metadata
  let columnOrder = [
    { key: 'date', label: 'Date' },
    { key: 'name', label: 'Name' },
    { key: 'interest', label: 'Interest' },
    { key: 'fundraise', label: 'Fundraise' },
    { key: 'summary', label: 'Summary' },
    { key: 'related_lps', label: 'Related LPs' },
    { key: 'related_gps', label: 'Related GPs' },
    { key: 'contact_type', label: 'Contact Type' },
    { key: 'useful', label: 'Useful' }
  ];

  // Drag and drop state
  let draggedColumnIndex: number | null = null;
  let initialized = false;

  // Load settings from localStorage
  function loadSettings() {
    try {
      const savedFilters = localStorage.getItem('notesDatabase_filters');
      const savedSort = localStorage.getItem('notesDatabase_sort');
      const savedColumns = localStorage.getItem('notesDatabase_columns');
      const savedColumnOrder = localStorage.getItem('notesDatabase_columnOrder');

      if (savedFilters) {
        activeFilters = JSON.parse(savedFilters);
      }

      if (savedSort) {
        const sortData = JSON.parse(savedSort);
        sortFields = sortData.fields || [];
        sortDirections = sortData.directions || {};
      }

      if (savedColumns) {
        const saved = JSON.parse(savedColumns);
        // Merge saved with defaults, ensuring all new columns are visible
        visibleColumns = { ...visibleColumns, ...saved };
      }

      if (savedColumnOrder) {
        const saved = JSON.parse(savedColumnOrder);
        // Migrate: add missing columns to the end
        const savedKeys = saved.map((col: any) => col.key);
        const missingColumns = columnOrder.filter(col => !savedKeys.includes(col.key));
        if (missingColumns.length > 0) {
          columnOrder = [...saved, ...missingColumns];
          // Save the updated order
          saveSettings();
        } else {
          columnOrder = saved;
        }
      }
    } catch (err) {
      console.error('Failed to load settings from localStorage:', err);
    }
  }

  // Save settings to localStorage
  function saveSettings() {
    try {
      localStorage.setItem('notesDatabase_filters', JSON.stringify(activeFilters));
      localStorage.setItem('notesDatabase_sort', JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem('notesDatabase_columns', JSON.stringify(visibleColumns));
      localStorage.setItem('notesDatabase_columnOrder', JSON.stringify(columnOrder));
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
      allNotes = await fetchNotes();

      // Fetch related LPs and GPs for each note
      const relatedPromises = allNotes.map(async (note) => {
        if (!note.id) return;

        try {
          const [lps, gps] = await Promise.all([
            fetchNoteLPs(note.id),
            fetchNoteGPs(note.id)
          ]);

          if (lps && lps.length > 0) {
            noteLPs.set(note.id, lps.map(lp => lp.name).join(', '));
          }

          if (gps && gps.length > 0) {
            noteGPs.set(note.id, gps.map(gp => gp.name).join(', '));
          }
        } catch (err) {
          console.error(`Failed to load related data for note ${note.id}:`, err);
        }
      });

      await Promise.all(relatedPromises);
      noteLPs = noteLPs;
      noteGPs = noteGPs;

      // Extract unique values for filters
      const interests = new Set<string>();
      const fundraises = new Set<string>();

      allNotes.forEach(note => {
        if (note.interest) interests.add(note.interest);
        if (note.fundraise) fundraises.add(note.fundraise);
      });

      availableFilters.interest = Array.from(interests).sort();
      availableFilters.fundraise = Array.from(fundraises).sort();

      applyFiltersAndSort();
      loading = false;
    } catch (err) {
      console.error("Failed to load notes:", err);
      loading = false;
    }
  });

  function applyFiltersAndSort() {
    let result = [...allNotes];

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(note =>
        note.name?.toLowerCase().includes(query) ||
        note.summary?.toLowerCase().includes(query)
      );
    }

    // Apply filters
    Object.entries(activeFilters).forEach(([field, values]) => {
      if (values.length > 0) {
        result = result.filter(note => {
          const noteValue = note[field as keyof Note];
          if (!noteValue) return false;
          return values.includes(String(noteValue));
        });
      }
    });

    // Apply sort
    if (sortFields.length > 0) {
      result.sort((a, b) => {
        for (const field of sortFields) {
          const aVal = a[field as keyof Note] || '';
          const bVal = b[field as keyof Note] || '';
          const direction = sortDirections[field] === 'desc' ? -1 : 1;

          if (aVal < bVal) return -1 * direction;
          if (aVal > bVal) return 1 * direction;
        }
        return 0;
      });
    }

    filteredNotes = result;
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
  function getCellValue(note: Note, columnKey: string): string {
    switch (columnKey) {
      case 'date':
        return formatDate(note.date);
      case 'name':
        return note.name || 'Untitled';
      case 'interest':
        return note.interest || '-';
      case 'fundraise':
        return note.fundraise || '-';
      case 'summary':
        return note.summary || '-';
      case 'related_lps':
        return note.id ? (noteLPs.get(note.id) || '-') : '-';
      case 'related_gps':
        return note.id ? (noteGPs.get(note.id) || '-') : '-';
      case 'contact_type':
        return note.contact_type || '-';
      case 'useful':
        return note.useful ? '✓' : '-';
      default:
        return '-';
    }
  }

  // Detail card handlers
  function openDetailCard(note: Note) {
    selectedNote = note;
    showDetailCard = true;
  }

  function closeDetailCard() {
    showDetailCard = false;
    selectedNote = null;
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  // Count active filters
  $: activeFilterCount = Object.values(activeFilters).reduce((sum, arr) => sum + arr.length, 0);
</script>

<div class="database-view">
  <div class="header">
    <h1>Notes Database</h1>
    <div class="header-stats">
      {filteredNotes.length} of {allNotes.length} notes
    </div>
  </div>

  <div class="controls">
    <div class="search-bar">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search notes by name or summary..."
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
          <h4>Interest</h4>
          <div class="filter-options">
            {#each availableFilters.interest as interest}
              <label class="filter-option">
                <input
                  type="checkbox"
                  checked={activeFilters.interest?.includes(interest)}
                  on:change={() => toggleFilter('interest', interest)}
                />
                <span>{interest}</span>
              </label>
            {/each}
          </div>
        </div>

        <div class="filter-group">
          <h4>Fundraise</h4>
          <div class="filter-options">
            {#each availableFilters.fundraise as fundraise}
              <label class="filter-option">
                <input
                  type="checkbox"
                  checked={activeFilters.fundraise?.includes(fundraise)}
                  on:change={() => toggleFilter('fundraise', fundraise)}
                />
                <span>{fundraise}</span>
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
          class="sort-option {sortFields.includes('date') ? 'active' : ''}"
          on:click={() => toggleSort('date')}
        >
          Date
          {#if sortFields.includes('date')}
            <span class="sort-indicator">{sortDirections['date'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

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
          class="sort-option {sortFields.includes('interest') ? 'active' : ''}"
          on:click={() => toggleSort('interest')}
        >
          Interest
          {#if sortFields.includes('interest')}
            <span class="sort-indicator">{sortDirections['interest'] === 'asc' ? '↑' : '↓'}</span>
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
    <div class="loading">Loading notes...</div>
  {:else}
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            {#each columnOrder as column}
              {#if visibleColumns[column.key]}
                <th>{column.label}</th>
              {/if}
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each filteredNotes as note}
            <tr on:click={() => openDetailCard(note)} class="clickable-row">
              {#each columnOrder as column}
                {#if visibleColumns[column.key]}
                  <td class={column.key === 'name' ? 'name-cell' : (column.key === 'summary' ? 'summary-cell' : '')}>
                    {getCellValue(note, column.key)}
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

{#if showDetailCard && selectedNote}
  <NoteDetailCard note={selectedNote} on:close={closeDetailCard} />
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

  /* Filter Panel */
  .filter-panel, .sort-panel {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .filter-header, .sort-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .filter-header h3, .sort-header h3 {
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

  /* Columns Panel */
  .btn-columns {
    background: #9b59b6;
    color: white;
    border-color: #9b59b6;
  }

  .btn-columns:hover {
    background: #8e44ad;
  }

  .columns-panel {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .columns-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .columns-header h3 {
    margin: 0;
    font-size: 1.2rem;
    color: #2c3e50;
  }

  .drag-hint {
    font-size: 0.85rem;
    color: #999;
    font-style: italic;
  }

  .columns-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .column-option {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 4px;
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
    border: 1px solid #ccc;
    background: white;
    cursor: pointer;
    font-size: 0.75rem;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .reorder-btn:hover:not(:disabled) {
    background: #e9ecef;
    border-color: #999;
  }

  .reorder-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    flex: 1;
  }

  .checkbox-label input[type="checkbox"] {
    cursor: pointer;
  }

  .checkbox-label span {
    user-select: none;
  }

  /* Table */
  .table-container {
    background: white;
    border-radius: 8px;
    overflow: auto;
    max-height: calc(100vh - 400px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

  .summary-cell {
    max-width: 400px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #999;
    font-size: 1.2rem;
  }

  /* Custom scrollbar styling */
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
