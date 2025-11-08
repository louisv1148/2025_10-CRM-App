/**
 * Frontend → Backend API Bridge
 * Uses Tauri invoke for communication with Python backend
 */

import { invoke } from "@tauri-apps/api/core";

const API_BASE_URL = "http://localhost:8000";

// Types
export interface LP {
  id?: number;
  name: string;
  aum_billions?: number;
  advisor?: string;
  intl_alts?: string;
  intl_mf?: string;
  local_alts?: string;
  local_mf?: string;
  investment_high?: number;
  investment_low?: number;
  location?: string;
  priority?: string;
  type_of_group?: string;
  text?: string;
  notion_id?: string;
}

export interface GP {
  id?: number;
  name: string;
  location?: string;
  contact_level?: string;
  flagship_strategy?: string;
  other_strategies?: string;
  note?: string;
  distributor_id?: number;
  notion_id?: string;
}

export interface Person {
  id?: number;
  name: string;
  position?: string;
  role?: string;
  org_type?: string;
  org_id?: number;
  email?: string;
  phone?: string;
  cell_phone?: string;
  office_phone?: string;
  location?: string;
  people_type?: string;
  personal_note?: string;
}

export interface Note {
  id?: number;
  name?: string;
  date?: string;
  lp_id?: number;
  gp_id?: number;
  raw_notes?: string;
  summary?: string;
  content_text?: string;
  fundraise?: string;
  interest?: string;
  contact_type?: string;
  useful?: boolean;
  audio_path?: string;
  transcription_path?: string;
}

export interface Todo {
  id?: number;
  note_id: number;
  description: string;
  status?: string;
  due_date?: string;
}

export interface Fund {
  id?: number;
  notion_id?: string;
  fund_name: string;
  geography?: string;
  target_multiple?: number;
  status?: string;
  days_to_rs?: number;
  target_irr?: string;
  hard_cap_mn?: number;
  target_mn?: number;
  roadshow_date?: string;
  sectors?: string;
  note?: string;
  potential?: string;
  asset_class?: string;
  current_lps?: string;
  launch?: string;
  roadshows?: string;
  final_close?: string;
  closed?: boolean;
  gp_notion_id?: string;
}

// API functions - LPs
export async function fetchLPs(): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/lps`);
  return response.json();
}

export async function searchLPs(query: string): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/lps/search?q=${encodeURIComponent(query)}`);
  return response.json();
}

export async function createLP(lp: LP): Promise<LP> {
  const response = await fetch(`${API_BASE_URL}/lps`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lp),
  });
  return response.json();
}

export async function updateLP(id: number, lp: Partial<LP>): Promise<LP> {
  const response = await fetch(`${API_BASE_URL}/lps/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lp),
  });
  return response.json();
}

export async function deleteLP(id: number): Promise<void> {
  await fetch(`${API_BASE_URL}/lps/${id}`, { method: "DELETE" });
}

// API functions - GPs
export async function fetchGPs(): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/gps`);
  return response.json();
}

export async function searchGPs(query: string): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/gps/search?q=${encodeURIComponent(query)}`);
  return response.json();
}

export async function createGP(gp: GP): Promise<GP> {
  const response = await fetch(`${API_BASE_URL}/gps`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(gp),
  });
  return response.json();
}

export async function updateGP(id: number, gp: Partial<GP>): Promise<GP> {
  const response = await fetch(`${API_BASE_URL}/gps/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(gp),
  });
  return response.json();
}

export async function deleteGP(id: number): Promise<void> {
  await fetch(`${API_BASE_URL}/gps/${id}`, { method: "DELETE" });
}

// API functions - Funds
export async function fetchFunds(): Promise<Fund[]> {
  const response = await fetch(`${API_BASE_URL}/funds`);
  return response.json();
}

export async function searchFunds(query: string): Promise<Fund[]> {
  const response = await fetch(`${API_BASE_URL}/funds/search?q=${encodeURIComponent(query)}`);
  return response.json();
}

// API functions - People
export async function fetchPeople(): Promise<Person[]> {
  const response = await fetch(`${API_BASE_URL}/people`);
  return response.json();
}

export async function searchPeople(query: string): Promise<Person[]> {
  const response = await fetch(`${API_BASE_URL}/people/search?q=${encodeURIComponent(query)}`);
  return response.json();
}

export async function createPerson(person: Person): Promise<Person> {
  const response = await fetch(`${API_BASE_URL}/people`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(person),
  });
  return response.json();
}

export async function updatePerson(id: number, person: Partial<Person>): Promise<Person> {
  const response = await fetch(`${API_BASE_URL}/people/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(person),
  });
  return response.json();
}

export async function fetchPersonLPs(personId: number): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/people/${personId}/lps`);
  return response.json();
}

export async function fetchPersonGPs(personId: number): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/people/${personId}/gps`);
  return response.json();
}

// API functions - Notes
export async function fetchNotes(): Promise<Note[]> {
  const response = await fetch(`${API_BASE_URL}/notes`);
  return response.json();
}

export async function fetchNote(id: number): Promise<Note> {
  const response = await fetch(`${API_BASE_URL}/notes/${id}`);
  return response.json();
}

export async function createNote(note: Note): Promise<Note> {
  const response = await fetch(`${API_BASE_URL}/notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(note),
  });
  return response.json();
}

export async function fetchNoteLPs(noteId: number): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/lps`);
  return response.json();
}

export async function fetchNoteGPs(noteId: number): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/gps`);
  return response.json();
}

export async function fetchNoteFunds(noteId: number): Promise<Fund[]> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/funds`);
  return response.json();
}

export async function linkNoteToFund(noteId: number, fundId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/funds/${fundId}`, {
    method: "POST",
  });
}

export async function unlinkNoteFromFund(noteId: number, fundId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/funds/${fundId}`, {
    method: "DELETE",
  });
}

export async function updateNote(id: number, note: Partial<Note>): Promise<Note> {
  const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(note),
  });
  return response.json();
}

export async function createNoteRelationships(
  noteId: number,
  lpIds: number[],
  gpIds: number[],
  participantIds: number[],
  fundIds: number[] = []
): Promise<{ success: boolean; note_id: number }> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/relationships`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lp_ids: lpIds,
      gp_ids: gpIds,
      participant_ids: participantIds,
      fund_ids: fundIds
    }),
  });
  return response.json();
}

// API functions - Todos
export async function fetchTodos(): Promise<Todo[]> {
  const response = await fetch(`${API_BASE_URL}/todos`);
  return response.json();
}

export async function createTodo(todo: Todo): Promise<Todo> {
  const response = await fetch(`${API_BASE_URL}/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(todo),
  });
  return response.json();
}

export async function updateTodo(id: number, todo: Partial<Todo>): Promise<Todo> {
  const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(todo),
  });
  return response.json();
}

// Audio recording
export async function startRecording(deviceIndex?: number): Promise<void> {
  return invoke("start_recording", { deviceIndex });
}

export async function stopRecording(): Promise<string> {
  return invoke("stop_recording");
}

export async function getAudioDevices(): Promise<any[]> {
  return invoke("get_audio_devices");
}

// Transcription
export async function transcribeAudio(audioPath: string): Promise<string> {
  return invoke("transcribe_audio", { audioPath });
}

// Summarization
export async function summarizeTranscription(transcription: string): Promise<any> {
  return invoke("summarize_transcription", { transcription });
}

// Relationship API functions
export async function fetchLPPeople(lpId: number): Promise<Person[]> {
  const response = await fetch(`${API_BASE_URL}/lps/${lpId}/people`);
  return response.json();
}

export async function fetchLPNotes(lpId: number): Promise<Note[]> {
  const response = await fetch(`${API_BASE_URL}/lps/${lpId}/notes`);
  return response.json();
}

export async function fetchLPTasks(lpId: number): Promise<Todo[]> {
  const response = await fetch(`${API_BASE_URL}/lps/${lpId}/tasks`);
  return response.json();
}

// GP relationship functions
export async function fetchGPPeople(gpId: number): Promise<Person[]> {
  const response = await fetch(`${API_BASE_URL}/gps/${gpId}/people`);
  return response.json();
}

export async function fetchGPNotes(gpId: number): Promise<Note[]> {
  const response = await fetch(`${API_BASE_URL}/gps/${gpId}/notes`);
  return response.json();
}

export async function fetchGPTasks(gpId: number): Promise<Todo[]> {
  const response = await fetch(`${API_BASE_URL}/gps/${gpId}/tasks`);
  return response.json();
}
