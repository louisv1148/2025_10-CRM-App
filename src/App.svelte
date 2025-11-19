<script lang="ts">
  import { onMount } from "svelte";
  import LPSection from "./components/LPSection.svelte";
  import GPSection from "./components/GPSection.svelte";
  import MeetingMeta from "./components/MeetingMeta.svelte";
  import NotesEditor from "./components/NotesEditor.svelte";
  import TodoList from "./components/TodoList.svelte";
  import LPDatabaseView from "./components/LPDatabaseView.svelte";
  import GPDatabaseView from "./components/GPDatabaseView.svelte";
  import FundsDatabaseView from "./components/FundsDatabaseView.svelte";
  import NotesDatabaseView from "./components/NotesDatabaseView.svelte";
  import PeopleDatabaseView from "./components/PeopleDatabaseView.svelte";
  import RoadshowFunnel from "./components/RoadshowFunnel.svelte";
  import { fetchLPs, fetchGPs, fetchNotes, fetchTodos } from "./lib/api";
  import { lps, gps, notes, todos, activeTab } from "./lib/stores";

  let loading = true;
  let error = "";

  onMount(async () => {
    // Load initial data
    try {
      console.log("Loading initial data...");
      $lps = await fetchLPs();
      console.log("LPs loaded:", $lps);
      $gps = await fetchGPs();
      console.log("GPs loaded:", $gps);
      $notes = await fetchNotes();
      console.log("Notes loaded:", $notes);
      $todos = await fetchTodos();
      console.log("Todos loaded:", $todos);
      loading = false;
    } catch (err) {
      console.error("Failed to load initial data:", err);
      error = `Failed to load data: ${err}`;
      loading = false;
    }
  });
</script>

<main>
  <header>
    <h1>CRM Meeting App</h1>
    <nav>
      <button class:active={$activeTab === "meeting"} on:click={() => ($activeTab = "meeting")}>
        Meeting
      </button>
      <button class:active={$activeTab === "lp-database"} on:click={() => ($activeTab = "lp-database")}>
        LP Database
      </button>
      <button class:active={$activeTab === "gp-database"} on:click={() => ($activeTab = "gp-database")}>
        GP Database
      </button>
      <button class:active={$activeTab === "funds-database"} on:click={() => ($activeTab = "funds-database")}>
        Funds Database
      </button>
      <button class:active={$activeTab === "notes-database"} on:click={() => ($activeTab = "notes-database")}>
        Notes Database
      </button>
      <button class:active={$activeTab === "people-database"} on:click={() => ($activeTab = "people-database")}>
        People Database
      </button>
      <button class:active={$activeTab === "roadshows"} on:click={() => ($activeTab = "roadshows")}>
        Roadshows
      </button>
      <button class:active={$activeTab === "history"} on:click={() => ($activeTab = "history")}>
        History
      </button>
    </nav>
  </header>

  <div class="container">
    {#if loading}
      <div class="loading">Loading...</div>
    {:else if error}
      <div class="error">{error}</div>
    {:else}
    {#if $activeTab === "meeting"}
      <div class="meeting-view">
        <div class="left-panel">
          <LPSection />
          <GPSection />
          <MeetingMeta />
        </div>

        <div class="center-panel">
          <NotesEditor />
        </div>

        <div class="right-panel">
          <TodoList />
        </div>
      </div>
    {:else if $activeTab === "lp-database"}
      <LPDatabaseView />
    {:else if $activeTab === "gp-database"}
      <GPDatabaseView />
    {:else if $activeTab === "funds-database"}
      <FundsDatabaseView />
    {:else if $activeTab === "notes-database"}
      <NotesDatabaseView />
    {:else if $activeTab === "people-database"}
      <PeopleDatabaseView />
    {:else if $activeTab === "roadshows"}
      <RoadshowFunnel />
    {:else if $activeTab === "history"}
      <div class="history-view">
        <h2>Meeting History</h2>
        <div class="notes-list">
          {#each $notes as note}
            <div class="note-card">
              <div class="note-date">{new Date(note.date).toLocaleDateString()}</div>
              <div class="note-summary">{note.summary || "No summary"}</div>
              <div class="note-meta">
                {#if note.fundraise}
                  <span class="badge">Fundraise: {note.fundraise}</span>
                {/if}
                {#if note.interest}
                  <span class="badge">Interest: {note.interest}</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {:else if $activeTab === "contacts"}
      <div class="contacts-view">
        <h2>Contacts</h2>
        <div class="contacts-grid">
          <div class="lp-list">
            <h3>Limited Partners</h3>
            {#each $lps as lp}
              <div class="contact-card">{lp.name}</div>
            {/each}
          </div>
          <div class="gp-list">
            <h3>General Partners</h3>
            {#each $gps as gp}
              <div class="contact-card">{gp.name}</div>
            {/each}
          </div>
        </div>
      </div>
    {/if}
    {/if}
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f5;
  }

  main {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    background: #2c3e50;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  nav {
    display: flex;
    gap: 1rem;
  }

  nav button {
    background: transparent;
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    cursor: pointer;
    border-radius: 4px;
    transition: background 0.2s;
  }

  nav button:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  nav button.active {
    background: rgba(255, 255, 255, 0.2);
  }

  .container {
    flex: 1;
    overflow: hidden;
    padding: 1rem;
  }

  .meeting-view {
    display: grid;
    grid-template-columns: 300px 1fr 300px;
    gap: 1rem;
    height: 100%;
  }

  .left-panel,
  .center-panel,
  .right-panel {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    overflow-y: auto;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .history-view,
  .contacts-view {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    height: 100%;
    overflow-y: auto;
  }

  .notes-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;
  }

  .note-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: box-shadow 0.2s;
  }

  .note-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .note-date {
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 0.5rem;
  }

  .note-summary {
    color: #666;
    margin-bottom: 0.5rem;
  }

  .note-meta {
    display: flex;
    gap: 0.5rem;
  }

  .badge {
    background: #3498db;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .contacts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-top: 1rem;
  }

  .contact-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .loading,
  .error {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-size: 1.5rem;
    color: #666;
  }

  .error {
    color: #e74c3c;
  }
</style>
