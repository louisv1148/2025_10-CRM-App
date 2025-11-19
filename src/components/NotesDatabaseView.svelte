<script lang="ts">
  import { onMount } from "svelte";
  import { fetchNotes, fetchNote, fetchNoteLPs, fetchNoteGPs, fetchNoteFunds, type Note, type LP, type GP, type Fund } from "../lib/api";
  import NoteDetailCard from "./NoteDetailCard.svelte";

  let allNotes: Note[] = [];
  let filteredNotes: Note[] = [];
  let loading = true;

  // Related entities
  let noteLPs: Map<number, string> = new Map();
  let noteGPs: Map<number, string> = new Map();
  let noteFunds: Map<number, string> = new Map();

  // Detail card state
  let selectedNote: Note | null = null;
  let showDetailCard = false;
  let isNewEntry = false;

  // Search
  let searchQuery = "";

  // Filter - New comprehensive filtering system
  let showFilterMenu = false;

  // Define filter types for each column
  type FilterCondition = {
    type: 'contains' | 'not_contains' | 'is_empty' | 'is_not_empty' | 'equals' | 'date_range' | 'checkbox';
    value?: string;
    startDate?: string;
    endDate?: string;
    checked?: boolean;
  };

  let activeFilters: {[key: string]: FilterCondition} = {};

  // Temporary filter state for building new filters
  let tempFilters = {
    date: { startDate: '', endDate: '' },
    name: { type: 'contains', value: '' },
    summary: { type: 'contains', value: '' },
    contact_type: { type: 'equals', value: '' },
    interest: { type: 'equals', value: '' },
    related_lps: { type: 'contains', value: '' },
    related_gps: { type: 'contains', value: '' },
    fundraise: { type: 'contains', value: '' },
    useful: { checked: true }
  };

  // Available unique values for certain fields
  let availableContactTypes: string[] = [];
  let availableInterests: string[] = [];

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

      // Fetch related LPs, GPs, and Funds for each note
      const relatedPromises = allNotes.map(async (note) => {
        if (!note.id) return;

        try {
          const [lps, gps, funds] = await Promise.all([
            fetchNoteLPs(note.id),
            fetchNoteGPs(note.id),
            fetchNoteFunds(note.id)
          ]);

          if (lps && lps.length > 0) {
            noteLPs.set(note.id, lps.map(lp => lp.name).join(', '));
          }

          if (gps && gps.length > 0) {
            noteGPs.set(note.id, gps.map(gp => gp.name).join(', '));
          }

          if (funds && funds.length > 0) {
            noteFunds.set(note.id, funds.map(fund => fund.fund_name).join(', '));
          }
        } catch (err) {
          console.error(`Failed to load related data for note ${note.id}:`, err);
        }
      });

      await Promise.all(relatedPromises);
      noteLPs = noteLPs;
      noteGPs = noteGPs;
      noteFunds = noteFunds;

      // Extract unique values for certain filters
      const contactTypes = new Set<string>();
      const interests = new Set<string>();

      allNotes.forEach(note => {
        if (note.contact_type) contactTypes.add(note.contact_type);
        if (note.interest) interests.add(note.interest);
      });

      availableContactTypes = Array.from(contactTypes).sort();
      availableInterests = Array.from(interests).sort();

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
    Object.entries(activeFilters).forEach(([field, condition]) => {
      result = result.filter(note => {
        let noteValue: any;

        // Get the value based on field
        if (field === 'related_lps') {
          noteValue = note.id ? noteLPs.get(note.id) : '';
        } else if (field === 'related_gps') {
          noteValue = note.id ? noteGPs.get(note.id) : '';
        } else if (field === 'fundraise') {
          noteValue = note.id ? noteFunds.get(note.id) : '';
        } else {
          noteValue = note[field as keyof Note];
        }

        // Apply filter based on condition type
        switch (condition.type) {
          case 'contains':
            if (!condition.value) return true;
            return noteValue?.toString().toLowerCase().includes(condition.value.toLowerCase()) || false;

          case 'not_contains':
            if (!condition.value) return true;
            return !noteValue?.toString().toLowerCase().includes(condition.value.toLowerCase());

          case 'is_empty':
            return !noteValue || noteValue === '';

          case 'is_not_empty':
            return noteValue && noteValue !== '';

          case 'equals':
            if (!condition.value) return true;
            return noteValue?.toString().toLowerCase() === condition.value.toLowerCase();

          case 'date_range':
            if (!noteValue || !condition.startDate || !condition.endDate) return true;
            const noteDate = new Date(noteValue as string);
            const startDate = new Date(condition.startDate);
            const endDate = new Date(condition.endDate);
            return noteDate >= startDate && noteDate <= endDate;

          case 'checkbox':
            if (condition.checked === undefined) return true;
            return condition.checked ? (noteValue === true) : (!noteValue || noteValue === false);

          default:
            return true;
        }
      });
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
  function addFilter(field: string, condition: FilterCondition) {
    activeFilters[field] = condition;
    activeFilters = { ...activeFilters };
    applyFiltersAndSort();
  }

  function removeFilter(field: string) {
    delete activeFilters[field];
    activeFilters = { ...activeFilters };
    applyFiltersAndSort();
  }

  function clearFilters() {
    activeFilters = {};
    applyFiltersAndSort();
  }

  function getActiveFilterCount(): number {
    return Object.keys(activeFilters).length;
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
        return note.id ? (noteFunds.get(note.id) || '-') : '-';
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
    isNewEntry = false;
    showDetailCard = true;
  }

  function openNewEntryCard() {
    // Create a blank Note object
    selectedNote = {
      name: '',
      date: new Date().toISOString().split('T')[0], // Default to today's date
      summary: '',
      contact_type: '',
      interest: '',
      raw_notes: '',
      content_text: '',
      useful: false
    } as Note;
    isNewEntry = true;
    showDetailCard = true;
  }

  function closeDetailCard() {
    showDetailCard = false;
    isNewEntry = false;
    selectedNote = null;
  }

  async function handleNoteCreated(event: CustomEvent<Note>) {
    const created = event.detail;
    if (!created?.id) return;

    // Add the new note to the array
    allNotes = [...allNotes, created];
    console.log("Added new note to allNotes array:", created);

    // Reapply filters and sort
    applyFiltersAndSort();
  }

  async function handleNoteUpdated() {
    console.log("handleNoteUpdated called for note:", selectedNote?.id);
    if (!selectedNote?.id) return;

    try {
      // Fetch the updated note data from the API
      const updatedNote = await fetchNote(selectedNote.id);
      console.log("Fetched updated note:", updatedNote);

      // Update the note in the allNotes array
      const noteIndex = allNotes.findIndex(n => n.id === selectedNote.id);
      if (noteIndex !== -1) {
        allNotes[noteIndex] = updatedNote;
        allNotes = [...allNotes]; // Create new array to trigger reactivity
        console.log("Updated note in allNotes array at index", noteIndex);
      }

      // Update selectedNote to reflect changes in the detail card
      selectedNote = updatedNote;

      // Fetch and update related LPs, GPs, and Funds
      const [lps, gps, funds] = await Promise.all([
        fetchNoteLPs(selectedNote.id),
        fetchNoteGPs(selectedNote.id),
        fetchNoteFunds(selectedNote.id)
      ]);
      console.log("Fetched related data - LPs:", lps, "GPs:", gps, "Funds:", funds);

      // Create new Maps to trigger reactivity
      const newNoteLPs = new Map(noteLPs);
      const newNoteGPs = new Map(noteGPs);
      const newNoteFunds = new Map(noteFunds);

      // Update LPs
      if (lps && lps.length > 0) {
        newNoteLPs.set(selectedNote.id, lps.map(lp => lp.name).join(', '));
      } else {
        newNoteLPs.delete(selectedNote.id);
      }

      // Update GPs
      if (gps && gps.length > 0) {
        newNoteGPs.set(selectedNote.id, gps.map(gp => gp.name).join(', '));
      } else {
        newNoteGPs.delete(selectedNote.id);
      }

      // Update Funds
      if (funds && funds.length > 0) {
        newNoteFunds.set(selectedNote.id, funds.map(fund => fund.fund_name).join(', '));
      } else {
        newNoteFunds.delete(selectedNote.id);
      }

      // Assign new Maps to trigger reactivity
      noteLPs = newNoteLPs;
      noteGPs = newNoteGPs;
      noteFunds = newNoteFunds;

      console.log("All data updated, reactivity triggered");

      // Re-apply filters and sort to update the filtered view
      applyFiltersAndSort();
    } catch (err) {
      console.error(`Failed to refresh note data for note ${selectedNote.id}:`, err);
    }
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  // Count active filters
  $: activeFilterCount = getActiveFilterCount();
</script>

<div class="database-view">
  <div class="header">
    <h1>Notes Database</h1>
    <div class="header-actions">
      <button class="new-entry-btn" on:click={openNewEntryCard}>+ New Entry</button>
      <div class="header-stats">
        {filteredNotes.length} of {allNotes.length} notes
      </div>
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
        <h3>Advanced Filters</h3>
        <button class="btn-clear" on:click={clearFilters}>Clear All</button>
      </div>

      <div class="active-filters">
        {#if Object.keys(activeFilters).length > 0}
          <h4>Active Filters:</h4>
          {#each Object.entries(activeFilters) as [field, condition]}
            <div class="active-filter-item">
              <span class="filter-field">{columnOrder.find(c => c.key === field)?.label || field}</span>
              <span class="filter-condition">
                {#if condition.type === 'contains'}
                  contains "{condition.value}"
                {:else if condition.type === 'not_contains'}
                  does not contain "{condition.value}"
                {:else if condition.type === 'is_empty'}
                  is empty
                {:else if condition.type === 'is_not_empty'}
                  is not empty
                {:else if condition.type === 'equals'}
                  equals "{condition.value}"
                {:else if condition.type === 'date_range'}
                  between {condition.startDate} and {condition.endDate}
                {:else if condition.type === 'checkbox'}
                  is {condition.checked ? 'checked' : 'unchecked'}
                {/if}
              </span>
              <button class="btn-remove-filter" on:click={() => removeFilter(field)}>✕</button>
            </div>
          {/each}
        {:else}
          <p class="no-filters">No active filters. Add a filter below.</p>
        {/if}
      </div>

      <div class="add-filter-section">
        <h4>Add Filter:</h4>

        <!-- Date Filter -->
        <div class="filter-builder">
          <label>Date</label>
          <div class="filter-inputs">
            <input type="date" bind:value={tempFilters.date.startDate} placeholder="Start date" />
            <span>to</span>
            <input type="date" bind:value={tempFilters.date.endDate} placeholder="End date" />
            <button class="btn-add" on:click={() => {
              if (tempFilters.date.startDate && tempFilters.date.endDate) {
                addFilter('date', { type: 'date_range', startDate: tempFilters.date.startDate, endDate: tempFilters.date.endDate });
                tempFilters.date = { startDate: '', endDate: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Name Filter -->
        <div class="filter-builder">
          <label>Name</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.name.type}>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.name.type === 'contains' || tempFilters.name.type === 'not_contains'}
              <input type="text" bind:value={tempFilters.name.value} placeholder="Enter text..." />
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.name.type === 'is_empty' || tempFilters.name.type === 'is_not_empty' || tempFilters.name.value) {
                addFilter('name', { type: tempFilters.name.type, value: tempFilters.name.value });
                tempFilters.name = { type: 'contains', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Summary Filter -->
        <div class="filter-builder">
          <label>Summary</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.summary.type}>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.summary.type === 'contains' || tempFilters.summary.type === 'not_contains'}
              <input type="text" bind:value={tempFilters.summary.value} placeholder="Enter text..." />
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.summary.type === 'is_empty' || tempFilters.summary.type === 'is_not_empty' || tempFilters.summary.value) {
                addFilter('summary', { type: tempFilters.summary.type, value: tempFilters.summary.value });
                tempFilters.summary = { type: 'contains', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Contact Type Filter -->
        <div class="filter-builder">
          <label>Contact Type</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.contact_type.type}>
              <option value="equals">Equals</option>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.contact_type.type === 'contains' || tempFilters.contact_type.type === 'not_contains' || tempFilters.contact_type.type === 'equals'}
              {#if availableContactTypes.length > 0 && (tempFilters.contact_type.type === 'equals')}
                <select bind:value={tempFilters.contact_type.value}>
                  <option value="">Select...</option>
                  {#each availableContactTypes as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              {:else}
                <input type="text" bind:value={tempFilters.contact_type.value} placeholder="Enter text..." />
              {/if}
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.contact_type.type === 'is_empty' || tempFilters.contact_type.type === 'is_not_empty' || tempFilters.contact_type.value) {
                addFilter('contact_type', { type: tempFilters.contact_type.type, value: tempFilters.contact_type.value });
                tempFilters.contact_type = { type: 'equals', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Interest Filter -->
        <div class="filter-builder">
          <label>Interest</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.interest.type}>
              <option value="equals">Equals</option>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.interest.type === 'contains' || tempFilters.interest.type === 'not_contains' || tempFilters.interest.type === 'equals'}
              {#if availableInterests.length > 0 && (tempFilters.interest.type === 'equals')}
                <select bind:value={tempFilters.interest.value}>
                  <option value="">Select...</option>
                  {#each availableInterests as interest}
                    <option value={interest}>{interest}</option>
                  {/each}
                </select>
              {:else}
                <input type="text" bind:value={tempFilters.interest.value} placeholder="Enter text..." />
              {/if}
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.interest.type === 'is_empty' || tempFilters.interest.type === 'is_not_empty' || tempFilters.interest.value) {
                addFilter('interest', { type: tempFilters.interest.type, value: tempFilters.interest.value });
                tempFilters.interest = { type: 'equals', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Related LPs Filter -->
        <div class="filter-builder">
          <label>Related LPs</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.related_lps.type}>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.related_lps.type === 'contains' || tempFilters.related_lps.type === 'not_contains'}
              <input type="text" bind:value={tempFilters.related_lps.value} placeholder="Enter text..." />
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.related_lps.type === 'is_empty' || tempFilters.related_lps.type === 'is_not_empty' || tempFilters.related_lps.value) {
                addFilter('related_lps', { type: tempFilters.related_lps.type, value: tempFilters.related_lps.value });
                tempFilters.related_lps = { type: 'contains', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Related GPs Filter -->
        <div class="filter-builder">
          <label>Related GPs</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.related_gps.type}>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.related_gps.type === 'contains' || tempFilters.related_gps.type === 'not_contains'}
              <input type="text" bind:value={tempFilters.related_gps.value} placeholder="Enter text..." />
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.related_gps.type === 'is_empty' || tempFilters.related_gps.type === 'is_not_empty' || tempFilters.related_gps.value) {
                addFilter('related_gps', { type: tempFilters.related_gps.type, value: tempFilters.related_gps.value });
                tempFilters.related_gps = { type: 'contains', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Fundraise Filter -->
        <div class="filter-builder">
          <label>Fundraise</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.fundraise.type}>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.fundraise.type === 'contains' || tempFilters.fundraise.type === 'not_contains'}
              <input type="text" bind:value={tempFilters.fundraise.value} placeholder="Enter fund name..." />
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.fundraise.type === 'is_empty' || tempFilters.fundraise.type === 'is_not_empty' || tempFilters.fundraise.value) {
                addFilter('fundraise', { type: tempFilters.fundraise.type, value: tempFilters.fundraise.value });
                tempFilters.fundraise = { type: 'contains', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Useful Filter (Checkbox) -->
        <div class="filter-builder">
          <label>Useful</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.useful.checked}>
              <option value={true}>Checked</option>
              <option value={false}>Unchecked</option>
            </select>
            <button class="btn-add" on:click={() => {
              addFilter('useful', { type: 'checkbox', checked: tempFilters.useful.checked });
            }}>Add</button>
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
  <NoteDetailCard
    note={selectedNote}
    isNew={isNewEntry}
    on:close={closeDetailCard}
    on:created={handleNoteCreated}
    on:updated={handleNoteUpdated}
  />
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
    max-height: 70vh;
    overflow-y: auto;
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

  /* Active Filters Section */
  .active-filters {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
  }

  .active-filters h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.95rem;
    color: #2c3e50;
  }

  .no-filters {
    color: #999;
    font-style: italic;
    margin: 0;
  }

  .active-filter-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .filter-field {
    font-weight: 600;
    color: #3498db;
  }

  .filter-condition {
    flex: 1;
    color: #555;
  }

  .btn-remove-filter {
    padding: 0.25rem 0.5rem;
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    font-size: 0.85rem;
  }

  .btn-remove-filter:hover {
    background: #c0392b;
  }

  /* Add Filter Section */
  .add-filter-section {
    border-top: 1px solid #ddd;
    padding-top: 1rem;
  }

  .add-filter-section h4 {
    margin: 0 0 1rem 0;
    font-size: 0.95rem;
    color: #2c3e50;
  }

  .filter-builder {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 4px;
  }

  .filter-builder label {
    font-weight: 600;
    font-size: 0.9rem;
    color: #2c3e50;
  }

  .filter-inputs {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .filter-inputs select,
  .filter-inputs input[type="text"],
  .filter-inputs input[type="date"] {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .filter-inputs select {
    min-width: 150px;
  }

  .filter-inputs input[type="text"] {
    flex: 1;
    min-width: 200px;
  }

  .filter-inputs input[type="date"] {
    min-width: 140px;
  }

  .btn-add {
    padding: 0.5rem 1rem;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .btn-add:hover {
    background: #229954;
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
