/**
 * Svelte stores for state management
 */

import { writable } from "svelte/store";
import type { LP, GP, Person, Note, Todo } from "./api";

// Entity stores
export const lps = writable<LP[]>([]);
export const gps = writable<GP[]>([]);
export const people = writable<Person[]>([]);
export const notes = writable<Note[]>([]);
export const todos = writable<Todo[]>([]);

// Current meeting state
export const currentNote = writable<Note | null>(null);
export const isRecording = writable<boolean>(false);
export const selectedLP = writable<number | null>(null);
export const selectedGP = writable<number | null>(null);

// UI state
export const activeTab = writable<string>("meeting");
export const showSettings = writable<boolean>(false);

// Auto-save state
export const lastSaved = writable<Date | null>(null);
export const hasUnsavedChanges = writable<boolean>(false);
