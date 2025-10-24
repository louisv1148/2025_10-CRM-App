<script lang="ts">
  import { isRecording } from "../lib/stores";
  import { startRecording, stopRecording } from "../lib/api";

  let meetingDate = new Date().toISOString().split("T")[0];
  let fundraise = "";
  let interest = "";

  const fundraiseOptions = ["Pre-seed", "Seed", "Series A", "Series B", "Series C+", "Growth", "Other"];
  const interestOptions = ["Cold", "Warm", "Hot", "Closed", "Passed"];

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
    <input id="date" type="date" bind:value={meetingDate} />
  </div>

  <div class="form-group">
    <label for="fundraise">Fundraise Stage</label>
    <select id="fundraise" bind:value={fundraise}>
      <option value="">Select stage...</option>
      {#each fundraiseOptions as option}
        <option value={option}>{option}</option>
      {/each}
    </select>
  </div>

  <div class="form-group">
    <label for="interest">Interest Level</label>
    <select id="interest" bind:value={interest}>
      <option value="">Select level...</option>
      {#each interestOptions as option}
        <option value={option}>{option}</option>
      {/each}
    </select>
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
