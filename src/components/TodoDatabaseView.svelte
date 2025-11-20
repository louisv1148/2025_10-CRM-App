<script lang="ts">
  import { onMount } from "svelte";
  import {
    fetchTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    createTodoRelationships,
    fetchTodoLPs,
    fetchTodoGPs,
    fetchTodoPeople,
    fetchTodoFunds,
    fetchTodoRoadshows,
    fetchTodoNotes,
    fetchLPs,
    fetchGPs,
    fetchPeople,
    fetchFunds,
    fetchRoadshows,
    fetchNotes,
    type Todo,
    type LP,
    type GP,
    type Person,
    type Fund,
    type Roadshow,
    type Note
  } from "../lib/api";

  let allTodos: Todo[] = [];
  let filteredTodos: Todo[] = [];
  let loading = true;

  // Available entities for relationships
  let allLPs: LP[] = [];
  let allGPs: GP[] = [];
  let allPeople: Person[] = [];
  let allFunds: Fund[] = [];
  let allRoadshows: Roadshow[] = [];
  let allNotes: Note[] = [];

  // Detail card state
  let selectedTodo: Todo | null = null;
  let showDetailModal = false;
  let isNewEntry = false;

  // Selected relationships for current todo
  let selectedLPIds: number[] = [];
  let selectedGPIds: number[] = [];
  let selectedPersonIds: number[] = [];
  let selectedFundIds: number[] = [];
  let selectedRoadshowIds: number[] = [];
  let selectedNoteIds: number[] = [];

  // Search queries for relationship dropdowns
  let lpSearch = "";
  let gpSearch = "";
  let peopleSearch = "";
  let fundSearch = "";
  let roadshowSearch = "";
  let noteSearch = "";

  // Filtered relationship lists
  $: filteredLPs = lpSearch ? allLPs.filter(lp => lp.name.toLowerCase().includes(lpSearch.toLowerCase())) : allLPs;
  $: filteredGPs = gpSearch ? allGPs.filter(gp => gp.name.toLowerCase().includes(gpSearch.toLowerCase())) : allGPs;
  $: filteredPeople = peopleSearch ? allPeople.filter(p => p.name.toLowerCase().includes(peopleSearch.toLowerCase())) : allPeople;
  $: filteredFunds = fundSearch ? allFunds.filter(f => f.fund_name.toLowerCase().includes(fundSearch.toLowerCase())) : allFunds;
  $: filteredRoadshows = roadshowSearch ? allRoadshows.filter(r => r.name.toLowerCase().includes(roadshowSearch.toLowerCase())) : allRoadshows;
  $: filteredNotes = noteSearch ? allNotes.filter(n => n.name?.toLowerCase().includes(noteSearch.toLowerCase())) : allNotes;

  // Search
  let searchQuery = "";

  // Filter
  let showFilterMenu = false;

  type FilterCondition = {
    type: 'contains' | 'not_contains' | 'is_empty' | 'is_not_empty' | 'equals' | 'date_range';
    value?: string;
    startDate?: string;
    endDate?: string;
  };

  let activeFilters: {[key: string]: FilterCondition} = {};

  // Temporary filter state
  let tempFilters = {
    due_date: { startDate: '', endDate: '' },
    created_at: { startDate: '', endDate: '' },
    title: { type: 'contains', value: '' },
    description: { type: 'contains', value: '' },
    status: { type: 'equals', value: '' },
    priority: { type: 'equals', value: '' },
    tags: { type: 'contains', value: '' }
  };

  // Available unique values
  let availableStatuses = ['pending', 'in_progress', 'completed', 'cancelled'];
  let availablePriorities = ['low', 'medium', 'high', 'urgent'];

  // Sort
  let sortFields: string[] = [];
  let sortDirections: {[key: string]: 'asc' | 'desc'} = {};
  let showSortMenu = false;

  // Column visibility
  let showColumnsMenu = false;
  let visibleColumns = {
    status: true,
    priority: true,
    title: true,
    description: true,
    due_date: true,
    tags: true,
    created_at: true
  };

  let columnOrder = [
    { key: 'status', label: 'Status' },
    { key: 'priority', label: 'Priority' },
    { key: 'title', label: 'Title' },
    { key: 'description', label: 'Description' },
    { key: 'due_date', label: 'Due Date' },
    { key: 'tags', label: 'Tags' },
    { key: 'created_at', label: 'Created' }
  ];

  let initialized = false;

  // Load settings from localStorage
  function loadSettings() {
    try {
      const savedFilters = localStorage.getItem('todoDatabase_filters');
      const savedSort = localStorage.getItem('todoDatabase_sort');
      const savedColumns = localStorage.getItem('todoDatabase_columns');
      const savedColumnOrder = localStorage.getItem('todoDatabase_columnOrder');

      if (savedFilters) activeFilters = JSON.parse(savedFilters);
      if (savedSort) {
        const sortData = JSON.parse(savedSort);
        sortFields = sortData.fields || [];
        sortDirections = sortData.directions || {};
      }
      if (savedColumns) {
        const saved = JSON.parse(savedColumns);
        visibleColumns = { ...visibleColumns, ...saved };
      }
      if (savedColumnOrder) {
        const saved = JSON.parse(savedColumnOrder);
        const savedKeys = saved.map((col: any) => col.key);
        const missingColumns = columnOrder.filter(col => !savedKeys.includes(col.key));
        if (missingColumns.length > 0) {
          columnOrder = [...saved, ...missingColumns];
          saveSettings();
        } else {
          columnOrder = saved;
        }
      }
    } catch (err) {
      console.error('Failed to load settings from localStorage:', err);
    }
  }

  function saveSettings() {
    try {
      localStorage.setItem('todoDatabase_filters', JSON.stringify(activeFilters));
      localStorage.setItem('todoDatabase_sort', JSON.stringify({
        fields: sortFields,
        directions: sortDirections
      }));
      localStorage.setItem('todoDatabase_columns', JSON.stringify(visibleColumns));
      localStorage.setItem('todoDatabase_columnOrder', JSON.stringify(columnOrder));
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
    await loadAllData();
  });

  async function loadAllData() {
    try {
      loading = true;
      console.log("=== Loading all data for TodoDatabaseView ===");
      // Load all data in parallel
      [allTodos, allLPs, allGPs, allPeople, allFunds, allRoadshows, allNotes] = await Promise.all([
        fetchTodos(),
        fetchLPs(),
        fetchGPs(),
        fetchPeople(),
        fetchFunds(),
        fetchRoadshows(),
        fetchNotes()
      ]);
      console.log("Loaded LPs:", allLPs.length, allLPs);
      console.log("Loaded GPs:", allGPs.length, allGPs);
      console.log("Loaded People:", allPeople.length, allPeople);
      console.log("Loaded Funds:", allFunds.length, allFunds);
      console.log("Loaded Roadshows:", allRoadshows.length, allRoadshows);
      console.log("Loaded Notes:", allNotes.length, allNotes);
      applyFiltersAndSort();
      loading = false;
    } catch (err) {
      console.error("Failed to load data:", err);
      loading = false;
    }
  }

  async function loadTodos() {
    try {
      allTodos = await fetchTodos();
      applyFiltersAndSort();
    } catch (err) {
      console.error("Failed to load todos:", err);
    }
  }

  function applyFiltersAndSort() {
    let result = [...allTodos];

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(todo =>
        todo.title?.toLowerCase().includes(query) ||
        todo.description?.toLowerCase().includes(query) ||
        todo.tags?.toLowerCase().includes(query)
      );
    }

    // Apply filters
    Object.entries(activeFilters).forEach(([field, condition]) => {
      result = result.filter(todo => {
        let todoValue: any = todo[field as keyof Todo];

        switch (condition.type) {
          case 'contains':
            if (!condition.value) return true;
            return todoValue?.toString().toLowerCase().includes(condition.value.toLowerCase()) || false;

          case 'not_contains':
            if (!condition.value) return true;
            return !todoValue?.toString().toLowerCase().includes(condition.value.toLowerCase());

          case 'is_empty':
            return !todoValue || todoValue === '';

          case 'is_not_empty':
            return todoValue && todoValue !== '';

          case 'equals':
            if (!condition.value) return true;
            return todoValue?.toString().toLowerCase() === condition.value.toLowerCase();

          case 'date_range':
            if (!todoValue || !condition.startDate || !condition.endDate) return true;
            const todoDate = new Date(todoValue as string);
            const startDate = new Date(condition.startDate);
            const endDate = new Date(condition.endDate);
            return todoDate >= startDate && todoDate <= endDate;

          default:
            return true;
        }
      });
    });

    // Apply sort
    if (sortFields.length > 0) {
      result.sort((a, b) => {
        for (const field of sortFields) {
          const aVal = a[field as keyof Todo] || '';
          const bVal = b[field as keyof Todo] || '';
          const direction = sortDirections[field] === 'desc' ? -1 : 1;

          if (aVal < bVal) return -1 * direction;
          if (aVal > bVal) return 1 * direction;
        }
        return 0;
      });
    }

    filteredTodos = result;
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
      if (sortDirections[field] === 'asc') {
        sortDirections[field] = 'desc';
      } else {
        sortFields.splice(index, 1);
        delete sortDirections[field];
      }
    } else {
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

  // Get cell value
  function getCellValue(todo: Todo, columnKey: string): string {
    switch (columnKey) {
      case 'status':
        return formatStatus(todo.status);
      case 'priority':
        return formatPriority(todo.priority);
      case 'title':
        return todo.title || 'Untitled';
      case 'description':
        return todo.description || '-';
      case 'due_date':
        return formatDate(todo.due_date);
      case 'tags':
        return todo.tags || '-';
      case 'created_at':
        return formatDate(todo.created_at);
      default:
        return '-';
    }
  }

  function formatStatus(status: string | undefined): string {
    if (!status) return 'pending';
    return status.replace('_', ' ').toUpperCase();
  }

  function formatPriority(priority: string | undefined): string {
    if (!priority) return 'medium';
    return priority.charAt(0).toUpperCase() + priority.slice(1);
  }

  function formatDate(dateStr: string | undefined): string {
    if (!dateStr) return "-";
    return new Date(dateStr).toLocaleDateString();
  }

  // Modal handlers
  function openNewEntryModal() {
    selectedTodo = {
      title: '',
      description: '',
      status: 'pending',
      priority: 'medium',
      due_date: '',
      tags: ''
    } as Todo;
    selectedLPIds = [];
    selectedGPIds = [];
    selectedPersonIds = [];
    selectedFundIds = [];
    selectedRoadshowIds = [];
    selectedNoteIds = [];
    isNewEntry = true;
    showDetailModal = true;
  }

  async function openEditModal(todo: Todo) {
    selectedTodo = { ...todo };
    isNewEntry = false;

    // Load relationships
    if (todo.id) {
      try {
        const [lps, gps, people, funds, roadshows, notes] = await Promise.all([
          fetchTodoLPs(todo.id),
          fetchTodoGPs(todo.id),
          fetchTodoPeople(todo.id),
          fetchTodoFunds(todo.id),
          fetchTodoRoadshows(todo.id),
          fetchTodoNotes(todo.id)
        ]);

        selectedLPIds = lps.map(lp => lp.id).filter((id): id is number => id !== undefined);
        selectedGPIds = gps.map(gp => gp.id).filter((id): id is number => id !== undefined);
        selectedPersonIds = people.map(p => p.id).filter((id): id is number => id !== undefined);
        selectedFundIds = funds.map(f => f.id).filter((id): id is number => id !== undefined);
        selectedRoadshowIds = roadshows.map(r => r.id).filter((id): id is number => id !== undefined);
        selectedNoteIds = notes.map(n => n.id).filter((id): id is number => id !== undefined);
      } catch (err) {
        console.error("Failed to load todo relationships:", err);
      }
    }

    showDetailModal = true;
  }

  function closeDetailModal() {
    showDetailModal = false;
    isNewEntry = false;
    selectedTodo = null;
    selectedLPIds = [];
    selectedGPIds = [];
    selectedPersonIds = [];
    selectedFundIds = [];
    selectedRoadshowIds = [];
    selectedNoteIds = [];
  }

  async function handleSave() {
    if (!selectedTodo) return;

    try {
      console.log("=== SAVING TODO ===");
      console.log("Todo data:", selectedTodo);
      console.log("Is new entry:", isNewEntry);
      console.log("Selected relationships:", {
        lps: selectedLPIds,
        gps: selectedGPIds,
        people: selectedPersonIds,
        funds: selectedFundIds,
        roadshows: selectedRoadshowIds,
        notes: selectedNoteIds
      });

      let savedTodo: Todo;

      if (isNewEntry) {
        console.log("Creating new todo...");
        savedTodo = await createTodo(selectedTodo);
        console.log("Todo created:", savedTodo);
      } else {
        if (selectedTodo.id) {
          console.log("Updating todo with ID:", selectedTodo.id);
          savedTodo = await updateTodo(selectedTodo.id, selectedTodo);
          console.log("Todo updated:", savedTodo);
        } else {
          console.error("No todo ID found for update");
          return;
        }
      }

      // Always save relationships to ensure old ones are cleared
      if (savedTodo.id) {
        console.log("Saving relationships for todo ID:", savedTodo.id);
        const relationshipResult = await createTodoRelationships(savedTodo.id, {
          lp_ids: selectedLPIds,
          gp_ids: selectedGPIds,
          person_ids: selectedPersonIds,
          fund_ids: selectedFundIds,
          roadshow_ids: selectedRoadshowIds,
          note_ids: selectedNoteIds
        });
        console.log("Relationships saved:", relationshipResult);
      }

      console.log("Reloading todos...");
      await loadTodos();
      console.log("Todos reloaded, count:", allTodos.length);
      closeDetailModal();
    } catch (err) {
      console.error("Failed to save todo:", err);
      alert(`Failed to save todo: ${err}`);
    }
  }

  async function handleDelete(todoId: number | undefined) {
    if (!todoId) return;
    if (!confirm("Are you sure you want to delete this todo?")) return;

    try {
      await deleteTodo(todoId);
      await loadTodos();
      closeDetailModal();
    } catch (err) {
      console.error("Failed to delete todo:", err);
      alert("Failed to delete todo");
    }
  }

  async function toggleTodoComplete(todo: Todo) {
    if (!todo.id) return;

    try {
      const newStatus = todo.status === 'completed' ? 'pending' : 'completed';
      await updateTodo(todo.id, { ...todo, status: newStatus });
      await loadTodos();
    } catch (err) {
      console.error("Failed to toggle todo:", err);
    }
  }

  // Count active filters
  $: activeFilterCount = getActiveFilterCount();
</script>

<div class="database-view">
  <div class="header">
    <h1>Todo List</h1>
    <div class="header-actions">
      <button class="new-entry-btn" on:click={openNewEntryModal}>+ New Todo</button>
      <div class="header-stats">
        {filteredTodos.length} of {allTodos.length} todos
      </div>
    </div>
  </div>

  <div class="controls">
    <div class="search-bar">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search todos by title, description, or tags..."
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

        <!-- Status Filter -->
        <div class="filter-builder">
          <label>Status</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.status.value}>
              <option value="">Select...</option>
              {#each availableStatuses as status}
                <option value={status}>{status.replace('_', ' ').toUpperCase()}</option>
              {/each}
            </select>
            <button class="btn-add" on:click={() => {
              if (tempFilters.status.value) {
                addFilter('status', { type: 'equals', value: tempFilters.status.value });
                tempFilters.status = { type: 'equals', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Priority Filter -->
        <div class="filter-builder">
          <label>Priority</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.priority.value}>
              <option value="">Select...</option>
              {#each availablePriorities as priority}
                <option value={priority}>{priority.charAt(0).toUpperCase() + priority.slice(1)}</option>
              {/each}
            </select>
            <button class="btn-add" on:click={() => {
              if (tempFilters.priority.value) {
                addFilter('priority', { type: 'equals', value: tempFilters.priority.value });
                tempFilters.priority = { type: 'equals', value: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Due Date Filter -->
        <div class="filter-builder">
          <label>Due Date</label>
          <div class="filter-inputs">
            <input type="date" bind:value={tempFilters.due_date.startDate} placeholder="Start date" />
            <span>to</span>
            <input type="date" bind:value={tempFilters.due_date.endDate} placeholder="End date" />
            <button class="btn-add" on:click={() => {
              if (tempFilters.due_date.startDate && tempFilters.due_date.endDate) {
                addFilter('due_date', { type: 'date_range', startDate: tempFilters.due_date.startDate, endDate: tempFilters.due_date.endDate });
                tempFilters.due_date = { startDate: '', endDate: '' };
              }
            }}>Add</button>
          </div>
        </div>

        <!-- Tags Filter -->
        <div class="filter-builder">
          <label>Tags</label>
          <div class="filter-inputs">
            <select bind:value={tempFilters.tags.type}>
              <option value="contains">Contains</option>
              <option value="not_contains">Does not contain</option>
              <option value="is_empty">Is empty</option>
              <option value="is_not_empty">Is not empty</option>
            </select>
            {#if tempFilters.tags.type === 'contains' || tempFilters.tags.type === 'not_contains'}
              <input type="text" bind:value={tempFilters.tags.value} placeholder="Enter tag..." />
            {/if}
            <button class="btn-add" on:click={() => {
              if (tempFilters.tags.type === 'is_empty' || tempFilters.tags.type === 'is_not_empty' || tempFilters.tags.value) {
                addFilter('tags', { type: tempFilters.tags.type, value: tempFilters.tags.value });
                tempFilters.tags = { type: 'contains', value: '' };
              }
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
        <button class="sort-option {sortFields.includes('status') ? 'active' : ''}" on:click={() => toggleSort('status')}>
          Status
          {#if sortFields.includes('status')}
            <span class="sort-indicator">{sortDirections['status'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

        <button class="sort-option {sortFields.includes('priority') ? 'active' : ''}" on:click={() => toggleSort('priority')}>
          Priority
          {#if sortFields.includes('priority')}
            <span class="sort-indicator">{sortDirections['priority'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

        <button class="sort-option {sortFields.includes('due_date') ? 'active' : ''}" on:click={() => toggleSort('due_date')}>
          Due Date
          {#if sortFields.includes('due_date')}
            <span class="sort-indicator">{sortDirections['due_date'] === 'asc' ? '↑' : '↓'}</span>
          {/if}
        </button>

        <button class="sort-option {sortFields.includes('created_at') ? 'active' : ''}" on:click={() => toggleSort('created_at')}>
          Created
          {#if sortFields.includes('created_at')}
            <span class="sort-indicator">{sortDirections['created_at'] === 'asc' ? '↑' : '↓'}</span>
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
              <button class="reorder-btn" disabled={index === 0} on:click={() => moveColumnUp(index)} title="Move up">
                ↑
              </button>
              <button class="reorder-btn" disabled={index === columnOrder.length - 1} on:click={() => moveColumnDown(index)} title="Move down">
                ↓
              </button>
            </div>
            <label class="checkbox-label">
              <input type="checkbox" bind:checked={visibleColumns[column.key]} />
              <span>{column.label}</span>
            </label>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  {#if loading}
    <div class="loading">Loading todos...</div>
  {:else}
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="checkbox-col"></th>
            {#each columnOrder as column}
              {#if visibleColumns[column.key]}
                <th>{column.label}</th>
              {/if}
            {/each}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each filteredTodos as todo}
            <tr class="todo-row" class:completed={todo.status === 'completed'}>
              <td class="checkbox-col">
                <input
                  type="checkbox"
                  checked={todo.status === 'completed'}
                  on:change={() => toggleTodoComplete(todo)}
                />
              </td>
              {#each columnOrder as column}
                {#if visibleColumns[column.key]}
                  <td
                    class={column.key === 'title' ? 'title-cell' : ''}
                    class:priority-urgent={column.key === 'priority' && todo.priority === 'urgent'}
                    class:priority-high={column.key === 'priority' && todo.priority === 'high'}
                    class:priority-medium={column.key === 'priority' && todo.priority === 'medium'}
                    class:priority-low={column.key === 'priority' && todo.priority === 'low'}
                    on:click={() => openEditModal(todo)}
                  >
                    {getCellValue(todo, column.key)}
                  </td>
                {/if}
              {/each}
              <td>
                <button class="btn-action btn-edit" on:click={() => openEditModal(todo)}>Edit</button>
                <button class="btn-action btn-delete" on:click={() => handleDelete(todo.id)}>Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

{#if showDetailModal && selectedTodo}
  <div class="modal-overlay" on:click={closeDetailModal}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>{isNewEntry ? 'Create New Todo' : 'Edit Todo'}</h2>
        <button class="modal-close" on:click={closeDetailModal}>✕</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label for="title">Title*</label>
          <input id="title" type="text" bind:value={selectedTodo.title} required />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea id="description" bind:value={selectedTodo.description} rows="4"></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="status">Status</label>
            <select id="status" bind:value={selectedTodo.status}>
              {#each availableStatuses as status}
                <option value={status}>{status.replace('_', ' ').toUpperCase()}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="priority">Priority</label>
            <select id="priority" bind:value={selectedTodo.priority}>
              {#each availablePriorities as priority}
                <option value={priority}>{priority.charAt(0).toUpperCase() + priority.slice(1)}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="due_date">Due Date</label>
          <input id="due_date" type="date" bind:value={selectedTodo.due_date} />
        </div>

        <div class="form-group">
          <label for="tags">Tags (comma-separated)</label>
          <input id="tags" type="text" bind:value={selectedTodo.tags} placeholder="urgent, follow-up, meeting" />
        </div>

        <div class="relationships-section">
          <h3>Related Entities</h3>

          <div class="form-group">
            <label for="lps">LPs</label>
            <input type="text" bind:value={lpSearch} placeholder="Search LPs..." class="search-input-small" />
            <select id="lps" bind:value={selectedLPIds} multiple size="6">
              {#each filteredLPs as lp}
                <option value={lp.id}>{lp.name}</option>
              {/each}
            </select>
            <small class="help-text">Hold Ctrl/Cmd to select multiple</small>
          </div>

          <div class="form-group">
            <label for="gps">GPs</label>
            <input type="text" bind:value={gpSearch} placeholder="Search GPs..." class="search-input-small" />
            <select id="gps" bind:value={selectedGPIds} multiple size="6">
              {#each filteredGPs as gp}
                <option value={gp.id}>{gp.name}</option>
              {/each}
            </select>
            <small class="help-text">Hold Ctrl/Cmd to select multiple</small>
          </div>

          <div class="form-group">
            <label for="people">People</label>
            <input type="text" bind:value={peopleSearch} placeholder="Search people..." class="search-input-small" />
            <select id="people" bind:value={selectedPersonIds} multiple size="6">
              {#each filteredPeople as person}
                <option value={person.id}>{person.name}</option>
              {/each}
            </select>
            <small class="help-text">Hold Ctrl/Cmd to select multiple</small>
          </div>

          <div class="form-group">
            <label for="funds">Funds</label>
            <input type="text" bind:value={fundSearch} placeholder="Search funds..." class="search-input-small" />
            <select id="funds" bind:value={selectedFundIds} multiple size="6">
              {#each filteredFunds as fund}
                <option value={fund.id}>{fund.fund_name}</option>
              {/each}
            </select>
            <small class="help-text">Hold Ctrl/Cmd to select multiple</small>
          </div>

          <div class="form-group">
            <label for="roadshows">Roadshows</label>
            <input type="text" bind:value={roadshowSearch} placeholder="Search roadshows..." class="search-input-small" />
            <select id="roadshows" bind:value={selectedRoadshowIds} multiple size="6">
              {#each filteredRoadshows as roadshow}
                <option value={roadshow.id}>{roadshow.name}</option>
              {/each}
            </select>
            <small class="help-text">Hold Ctrl/Cmd to select multiple</small>
          </div>

          <div class="form-group">
            <label for="notes">Notes</label>
            <input type="text" bind:value={noteSearch} placeholder="Search notes..." class="search-input-small" />
            <select id="notes" bind:value={selectedNoteIds} multiple size="6">
              {#each filteredNotes as note}
                <option value={note.id}>{note.name}</option>
              {/each}
            </select>
            <small class="help-text">Hold Ctrl/Cmd to select multiple</small>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeDetailModal}>Cancel</button>
        <button class="btn-primary" on:click={handleSave}>Save</button>
      </div>
    </div>
  </div>
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

  .btn-columns {
    background: #9b59b6;
    color: white;
    border-color: #9b59b6;
  }

  .btn-columns:hover {
    background: #8e44ad;
  }

  /* Filter Panel */
  .filter-panel, .sort-panel, .columns-panel {
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-height: 70vh;
    overflow-y: auto;
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
    position: sticky;
    top: 0;
    z-index: 10;
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

  .checkbox-col {
    width: 40px;
    min-width: 40px;
    padding: 0.5rem !important;
    text-align: center;
  }

  .data-table tbody tr {
    border-bottom: 1px solid #e0e0e0;
    transition: background 0.2s;
  }

  .todo-row {
    cursor: pointer;
  }

  .todo-row:hover {
    background: #f8f9fa;
  }

  .todo-row.completed {
    opacity: 0.6;
  }

  .todo-row.completed .title-cell {
    text-decoration: line-through;
  }

  .data-table td {
    padding: 1rem;
    color: #555;
    min-width: 120px;
  }

  .title-cell {
    font-weight: 600;
    color: #2c3e50;
  }

  .priority-urgent {
    color: #e74c3c;
    font-weight: bold;
  }

  .priority-high {
    color: #e67e22;
    font-weight: 600;
  }

  .priority-medium {
    color: #3498db;
  }

  .priority-low {
    color: #95a5a6;
  }

  .btn-action {
    padding: 0.25rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 0.85rem;
    margin-right: 0.25rem;
    transition: all 0.2s;
  }

  .btn-edit {
    border-color: #3498db;
    color: #3498db;
  }

  .btn-edit:hover {
    background: #3498db;
    color: white;
  }

  .btn-delete {
    border-color: #e74c3c;
    color: #e74c3c;
  }

  .btn-delete:hover {
    background: #e74c3c;
    color: white;
  }

  .loading {
    text-align: center;
    padding: 4rem;
    color: #999;
    font-size: 1.2rem;
  }

  /* Modal */
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

  .modal-content {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    max-width: 800px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .modal-header h2 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.5rem;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #999;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-close:hover {
    color: #333;
  }

  .modal-body {
    margin-bottom: 1.5rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .form-group input,
  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
  }

  .form-group input:focus,
  .form-group textarea:focus,
  .form-group select:focus {
    outline: none;
    border-color: #3498db;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .relationships-section {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid #e0e0e0;
  }

  .relationships-section h3 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
    font-size: 1.2rem;
  }

  .help-text {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.25rem;
  }

  .search-input-small {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }

  .search-input-small:focus {
    outline: none;
    border-color: #3498db;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }

  .btn-primary, .btn-secondary {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
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

  /* Custom scrollbar */
  .table-container::-webkit-scrollbar,
  .modal-content::-webkit-scrollbar {
    width: 12px;
    height: 12px;
  }

  .table-container::-webkit-scrollbar-track,
  .modal-content::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb,
  .modal-content::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb:hover,
  .modal-content::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
</style>
