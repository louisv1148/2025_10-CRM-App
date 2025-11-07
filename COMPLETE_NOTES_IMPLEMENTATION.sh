#!/bin/bash

# Complete Notes Implementation Script
# This script completes the implementation of Related LPs/GPs and new fields in Notes view

echo "=== Completing Notes Implementation ==="

cd "/Users/lvc/AI Scripts/2025_10 CRM App"

# Step 1: Add API functions to api.ts
echo "Step 1: Adding API functions to api.ts..."

# Find the right place to add functions (after existing Note functions)
# Add these two functions after line 200 in api.ts

cat >> src/lib/api_additions.ts << 'EOF'
// Add these functions to api.ts after the existing Note functions:

export async function fetchNoteLPs(noteId: number): Promise<LP[]> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/lps`);
  return response.json();
}

export async function fetchNoteGPs(noteId: number): Promise<GP[]> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}/gps`);
  return response.json();
}
EOF

echo "✓ API functions code generated in src/lib/api_additions.ts"
echo "  Please manually add these to src/lib/api.ts after the existing Note functions"

# Step 2: Create NotesDatabaseView updates file
echo "Step 2: Creating NotesDatabaseView updates..."

cat > src/components/notes_view_updates.txt << 'EOF'
NOTES DATABASE VIEW UPDATES NEEDED:

1. Update imports (line 3):
   import { fetchNotes, fetchNoteLPs, fetchNoteGPs, type Note, type LP, type GP } from "../lib/api";

2. Add state after existing state declarations:
   let noteLPs: Map<number, string> = new Map();
   let noteGPs: Map<number, string> = new Map();

3. Update columnOrder array:
   let columnOrder = [
     { key: 'date', label: 'Date' },
     { key: 'interest', label: 'Interest' },
     { key: 'fundraise', label: 'Fundraise' },
     { key: 'summary', label: 'Summary' },
     { key: 'related_lps', label: 'Related LPs' },
     { key: 'related_gps', label: 'Related GPs' },
     { key: 'contact_type', label: 'Contact Type' },
     { key: 'useful', label: 'Useful' }
   ];

4. Update visibleColumns:
   let visibleColumns = {
     date: true,
     interest: true,
     fundraise: true,
     summary: true,
     related_lps: true,
     related_gps: true,
     contact_type: true,
     useful: true
   };

5. Add in onMount after "allNotes = await fetchNotes();":

   // Fetch related LPs and GPs for each note
   const relatedPromises = allNotes.map(async (note) => {
     if (!note.id) return;

     try {
       const [lps, gps] = await Promise.all([
         fetchNoteLPs(note.id),
         fetchNoteGPs(note.id)
       ]);

       if (lps && lps.length > 0) {
         noteLPs.set(note.id, lps.map(lp => lp.name).join(', '));
       }

       if (gps && gps.length > 0) {
         noteGPs.set(note.id, gps.map(gp => gp.name).join(', '));
       }
     } catch (err) {
       console.error(`Failed to load related data for note ${note.id}:`, err);
     }
   });

   await Promise.all(relatedPromises);
   noteLPs = noteLPs;
   noteGPs = noteGPs;

6. Update getCellValue function - add these cases:
   case 'related_lps':
     return note.id ? (noteLPs.get(note.id) || '-') : '-';
   case 'related_gps':
     return note.id ? (noteGPs.get(note.id) || '-') : '-';
   case 'contact_type':
     return note.contact_type || '-';
   case 'useful':
     return note.useful ? '✓' : '-';

EOF

echo "✓ Update instructions created in src/components/notes_view_updates.txt"

# Step 3: Restart backend server
echo "Step 3: Restarting backend server..."
pkill -f "src-tauri/python/backend.py"
sleep 2
source src-tauri/python/lib/bin/activate
python3 src-tauri/python/backend.py 2>&1 &
sleep 3

echo "✓ Backend server restarted with new endpoints"

echo ""
echo "=== Implementation Files Created ==="
echo "1. src/lib/api_additions.ts - Add these functions to api.ts"
echo "2. src/components/notes_view_updates.txt - Apply these updates to NotesDatabaseView.svelte"
echo ""
echo "Backend endpoints are now live at:"
echo "  - GET /notes/{note_id}/lps"
echo "  - GET /notes/{note_id}/gps"
echo ""
echo "To complete: Manually apply the updates from the generated files."
