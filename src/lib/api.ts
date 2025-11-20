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
  title: string;
  description?: string;
  status?: string;  // pending, in_progress, completed, cancelled
  priority?: string;  // low, medium, high, urgent
  created_at?: string;
  due_date?: string;
  completed_at?: string;
  recurrence_pattern?: string;  // JSON string: {"type": "daily|weekly|monthly", "interval": 1, "end_date": "ISO8601"}
  parent_todo_id?: number;
  tags?: string;  // Comma-separated
  note_id?: number;  // Legacy/optional
}

export interface TodoRelationships {
  lp_ids?: number[];
  gp_ids?: number[];
  person_ids?: number[];
  fund_ids?: number[];
  roadshow_ids?: number[];
  note_ids?: number[];
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

export interface SalesFunnelItem {
  fund_id: number;
  lp_id: number;
  lp_name: string;
  interest: string;
  last_contact_date?: string;
  latest_note_id?: number;
  // LP details
  aum_billions?: number;
  location?: string;
  priority?: string;
  advisor?: string;
  type_of_group?: string;
  investment_low?: number;
  investment_high?: number;
}

export interface Roadshow {
  id?: number;
  name: string; // e.g., "Q1 2025 Mexico Roadshow"
  fund_id: number; // Required: each roadshow is for ONE fund
  arrival?: string;
  arrival_city?: string;
  second_city?: string;
  second_arrival?: string;
  departure?: string;
  lv_flight: string; // Needed, Done, None
  lv_hotel: string; // Needed, Done, None
  mty_driver: string; // Needed, Done, None
  cdmx_driver: string; // Needed, Done, None
  flight_images?: string; // JSON array of image data URLs
  notes?: string;
}

export interface RoadshowLPStatus {
  roadshow_id: number;
  lp_id: number;
  lp_name: string;
  status: string; // inactive, declined, offered, interested, confirmed
  last_contact_date?: string;
  latest_note_id?: number;
  // LP details (same as SalesFunnelItem)
  aum_billions?: number;
  location?: string;
  priority?: string;
  advisor?: string;
  type_of_group?: string;
  investment_low?: number;
  investment_high?: number;
}

// API functions - LPs
export async function fetchLPs(): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/lps`);
  return response.json();
}

export async function fetchLP(id: number): Promise<LP> {
  const response = await fetch(`${API_BASE_URL}/lps/${id}`);
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

export async function fetchGP(id: number): Promise<GP> {
  const response = await fetch(`${API_BASE_URL}/gps/${id}`);
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

export async function fetchFund(id: number): Promise<Fund> {
  const response = await fetch(`${API_BASE_URL}/funds/${id}`);
  return response.json();
}

export async function searchFunds(query: string): Promise<Fund[]> {
  const response = await fetch(`${API_BASE_URL}/funds/search?q=${encodeURIComponent(query)}`);
  return response.json();
}

export async function createFund(fund: Fund): Promise<Fund> {
  const response = await fetch(`${API_BASE_URL}/funds`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fund),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create fund: ${error}`);
  }
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

export async function linkNoteToLP(noteId: number, lpId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/lps/${lpId}`, {
    method: "POST",
  });
}

export async function unlinkNoteFromLP(noteId: number, lpId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/lps/${lpId}`, {
    method: "DELETE",
  });
}

export async function linkNoteToGP(noteId: number, gpId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/gps/${gpId}`, {
    method: "POST",
  });
}

export async function unlinkNoteFromGP(noteId: number, gpId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/gps/${gpId}`, {
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
  fundIds: number[] = [],
  roadshowIds: number[] = []
): Promise<{ success: boolean; note_id: number }> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/relationships`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lp_ids: lpIds,
      gp_ids: gpIds,
      participant_ids: participantIds,
      fund_ids: fundIds,
      roadshow_ids: roadshowIds
    }),
  });
  return response.json();
}

// Enhanced API functions - Todos
export async function fetchTodos(filters?: {
  status?: string;
  priority?: string;
  tag?: string;
  due_before?: string;
  due_after?: string;
}): Promise<Todo[]> {
  const params = new URLSearchParams();
  if (filters) {
    if (filters.status) params.append("status", filters.status);
    if (filters.priority) params.append("priority", filters.priority);
    if (filters.tag) params.append("tag", filters.tag);
    if (filters.due_before) params.append("due_before", filters.due_before);
    if (filters.due_after) params.append("due_after", filters.due_after);
  }
  const queryString = params.toString();
  const url = queryString ? `${API_BASE_URL}/todos?${queryString}` : `${API_BASE_URL}/todos`;
  const response = await fetch(url);
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

export async function deleteTodo(id: number): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
    method: "DELETE",
  });
  return response.json();
}

// Todo relationship functions
export async function createTodoRelationships(
  todoId: number,
  relationships: TodoRelationships
): Promise<{ success: boolean; todo_id: number }> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/relationships`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(relationships),
  });
  return response.json();
}

export async function fetchTodoLPs(todoId: number): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/lps`);
  return response.json();
}

export async function fetchTodoGPs(todoId: number): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/gps`);
  return response.json();
}

export async function fetchTodoPeople(todoId: number): Promise<Person[]> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/people`);
  return response.json();
}

export async function fetchTodoFunds(todoId: number): Promise<Fund[]> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/funds`);
  return response.json();
}

export async function fetchTodoRoadshows(todoId: number): Promise<Roadshow[]> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/roadshows`);
  return response.json();
}

export async function fetchTodoNotes(todoId: number): Promise<Note[]> {
  const response = await fetch(`${API_BASE_URL}/todos/${todoId}/notes`);
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

// Fund relationship functions
export async function fetchFundNotes(fundId: number): Promise<Note[]> {
  const response = await fetch(`${API_BASE_URL}/funds/${fundId}/notes`);
  return response.json();
}

export async function updateFund(fundId: number, fund: Partial<Fund>): Promise<Fund> {
  console.log("updateFund API call - fundId:", fundId, "data:", fund);
  console.log("Request URL:", `${API_BASE_URL}/funds/${fundId}`);
  console.log("Request body:", JSON.stringify(fund));

  const response = await fetch(`${API_BASE_URL}/funds/${fundId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fund),
  });

  console.log("Response status:", response.status);
  console.log("Response ok:", response.ok);

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Response error:", errorText);
    throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
  }

  const result = await response.json();
  console.log("updateFund result:", result);
  return result;
}

// Sales Funnel functions
export async function fetchFundSalesFunnel(fundId: number): Promise<SalesFunnelItem[]> {
  const response = await fetch(`${API_BASE_URL}/funds/${fundId}/sales-funnel`);
  return response.json();
}

export async function updateLPInterest(fundId: number, lpId: number, interest: string): Promise<void> {
  await fetch(`${API_BASE_URL}/funds/${fundId}/lps/${lpId}/interest?interest=${encodeURIComponent(interest)}`, {
    method: "PUT",
  });
}

// Roadshow functions
export async function fetchRoadshows(): Promise<Roadshow[]> {
  const response = await fetch(`${API_BASE_URL}/roadshows`);
  return response.json();
}

export async function createRoadshow(roadshow: Roadshow): Promise<Roadshow> {
  const response = await fetch(`${API_BASE_URL}/roadshows`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(roadshow),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create roadshow: ${error}`);
  }
  return response.json();
}

export async function updateRoadshow(roadshowId: number, roadshow: Partial<Roadshow>): Promise<Roadshow> {
  const response = await fetch(`${API_BASE_URL}/roadshows/${roadshowId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(roadshow),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to update roadshow: ${error}`);
  }
  return response.json();
}

export async function deleteRoadshow(roadshowId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/roadshows/${roadshowId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete roadshow");
  }
}

// Roadshow LP Status functions (similar to sales funnel)
export async function fetchRoadshowLPStatus(roadshowId: number): Promise<RoadshowLPStatus[]> {
  const response = await fetch(`${API_BASE_URL}/roadshows/${roadshowId}/lp-status`);
  return response.json();
}

export async function updateLPRoadshowStatus(roadshowId: number, lpId: number, status: string): Promise<void> {
  await fetch(`${API_BASE_URL}/roadshows/${roadshowId}/lps/${lpId}/status?status=${encodeURIComponent(status)}`, {
    method: "PUT",
  });
}

// Link notes to roadshows
export async function fetchNoteRoadshows(noteId: number): Promise<Roadshow[]> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/roadshows`);
  return response.json();
}

export async function linkNoteToRoadshow(noteId: number, roadshowId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/roadshows/${roadshowId}`, {
    method: "POST",
  });
}

export async function unlinkNoteFromRoadshow(noteId: number, roadshowId: number): Promise<void> {
  await fetch(`${API_BASE_URL}/notes/${noteId}/roadshows/${roadshowId}`, {
    method: "DELETE",
  });
}
