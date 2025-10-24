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
}

export interface GP {
  id?: number;
  name: string;
}

export interface Person {
  id?: number;
  name: string;
  role: string;
  org_type: string;
  org_id?: number;
  email?: string;
  phone?: string;
}

export interface Note {
  id?: number;
  date?: string;
  lp_id?: number;
  gp_id?: number;
  raw_notes?: string;
  summary?: string;
  fundraise?: string;
  interest?: string;
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

// API functions - LPs
export async function fetchLPs(): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/lps`);
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

export async function deleteLP(id: number): Promise<void> {
  await fetch(`${API_BASE_URL}/lps/${id}`, { method: "DELETE" });
}

// API functions - GPs
export async function fetchGPs(): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/gps`);
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

export async function deleteGP(id: number): Promise<void> {
  await fetch(`${API_BASE_URL}/gps/${id}`, { method: "DELETE" });
}

// API functions - People
export async function fetchPeople(): Promise<Person[]> {
  const response = await fetch(`${API_BASE_URL}/people`);
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

export async function updateNote(id: number, note: Partial<Note>): Promise<Note> {
  const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(note),
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
