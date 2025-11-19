<script lang="ts">
  import { isRecording, meetingDate, meetingTitle, meetingType, meetingPinned, funds, selectedFunds, roadshows, selectedRoadshows } from "../lib/stores";
  import { startRecording, stopRecording, fetchFunds, fetchRoadshows, type Fund, type Roadshow } from "../lib/api";
  import { onMount } from "svelte";

  const meetingTypeOptions = ["in-person", "in-bound", "call/VC", "chats", "out-bound", "documents"];

  onMount(async () => {
    // Load funds and roadshows
    try {
      const [loadedFunds, loadedRoadshows] = await Promise.all([
        fetchFunds(),
        fetchRoadshows()
      ]);
      $funds = loadedFunds;
      $roadshows = loadedRoadshows;
    } catch (err) {
      console.error("Failed to load data:", err);
    }
  });

  async function toggleRecording() {
    if ($isRecording) {
      const audioPath = await stopRecording();
      console.log("Recording saved:", audioPath);
      $isRecording = false;
    } else {
      await startRecording();
      $isRecording = true;
    }
  }
</script>

<section class="meeting-meta">
  <h3>Meeting Details</h3>

  <div class="form-group">
    <label for="date">Date</label>
    <input id="date" type="date" bind:value={$meetingDate} />
  </div>

  <div class="form-group">
    <label for="title">Meeting Title</label>
    <input id="title" type="text" bind:value={$meetingTitle} placeholder="e.g., Q4 Review" />
    <small class="help-text">Will be saved as: {$meetingDate ? $meetingDate.replace(/-/g, '_') : 'YYYY_MM_DD'}_{$meetingTitle || 'Title'}</small>
  </div>

  <div class="form-group">
    <label for="meetingType">Meeting Type</label>
    <select id="meetingType" bind:value={$meetingType}>
      <option value="">Select type...</option>
      {#each meetingTypeOptions as option}
        <option value={option}>{option}</option>
      {/each}
    </select>
  </div>

  <div class="form-group checkbox-group">
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={$meetingPinned} />
      <span>Useful</span>
    </label>
  </div>

  <div class="form-group">
    <label for="funds">Related Funds</label>
    <select id="funds" bind:value={$selectedFunds} multiple size="4">
      <option value="">No fund selected</option>
      {#each $funds as fund}
        <option value={fund.id}>{fund.fund_name}</option>
      {/each}
    </select>
    <small class="help-text">Hold Ctrl/Cmd to select multiple funds</small>
  </div>

  <div class="form-group">
    <label for="roadshows">Related Roadshows</label>
    <select id="roadshows" bind:value={$selectedRoadshows} multiple size="4">
      <option value="">No roadshow selected</option>
      {#each $roadshows as roadshow}
        <option value={roadshow.id}>{roadshow.name}</option>
      {/each}
    </select>
    <small class="help-text">Hold Ctrl/Cmd to select multiple roadshows</small>
  </div>

  <div class="recording-controls">
    <button
      class="record-btn"
      class:recording={$isRecording}
      on:click={toggleRecording}
    >
      {$isRecording ? "⏹ Stop Recording" : "⏺ Start Recording"}
    </button>
  </div>
</section>

<style>
  .meeting-meta {
    margin-bottom: 1.5rem;
  }

  h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 2px solid #27ae60;
    padding-bottom: 0.5rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 0.25rem;
  }

  input,
  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  select[multiple] {
    min-height: 100px;
  }

  .help-text {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.75rem;
    color: #999;
  }

  .checkbox-group {
    display: flex;
    align-items: center;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-size: 0.9rem;
    color: #2c3e50;
  }

  .checkbox-label input[type="checkbox"] {
    width: auto;
    cursor: pointer;
  }

  .recording-controls {
    margin-top: 1.5rem;
  }

  .record-btn {
    width: 100%;
    padding: 0.75rem;
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
    transition: background 0.2s;
  }

  .record-btn:hover {
    background: #229954;
  }

  .record-btn.recording {
    background: #e74c3c;
    animation: pulse 1.5s infinite;
  }

  .record-btn.recording:hover {
    background: #c0392b;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
</style>
