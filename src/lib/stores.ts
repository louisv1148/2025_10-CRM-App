/**
 * Svelte stores for state management
 */

import { writable } from "svelte/store";
import type { LP, GP, Person, Note, Todo, Fund, Roadshow } from "./api";

// Entity stores
export const lps = writable<LP[]>([]);
export const gps = writable<GP[]>([]);
export const people = writable<Person[]>([]);
export const notes = writable<Note[]>([]);
export const todos = writable<Todo[]>([]);
export const funds = writable<Fund[]>([]);
export const roadshows = writable<Roadshow[]>([]);

// Current meeting state
export const currentNote = writable<Note | null>(null);
export const isRecording = writable<boolean>(false);
export const selectedLP = writable<number | null>(null);  // Legacy - kept for backward compatibility
export const selectedGP = writable<number | null>(null);  // Legacy - kept for backward compatibility
export const selectedLPs = writable<number[]>([]);  // New: support multiple LPs
export const selectedGPs = writable<number[]>([]);  // New: support multiple GPs
export const selectedParticipants = writable<number[]>([]);
export const selectedFunds = writable<number[]>([]);
export const selectedRoadshows = writable<number[]>([]);

// Meeting metadata
export const meetingDate = writable<string>(new Date().toISOString().split("T")[0]);
export const meetingTitle = writable<string>("");
export const meetingType = writable<string>("");
export const meetingPinned = writable<boolean>(false);

// UI state
export const activeTab = writable<string>("meeting");
export const showSettings = writable<boolean>(false);

// Auto-save state
export const lastSaved = writable<Date | null>(null);
export const hasUnsavedChanges = writable<boolean>(false);
