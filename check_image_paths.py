import sys
import json
sys.path.insert(0, 'src-tauri/python')

from database import Note, get_session

with get_session() as session:
    note = session.query(Note).filter(Note.name.like('%Reverence - Profu FU%')).first()
    if note:
        print('Note ID:', note.id)
        print('Name:', note.name)
        print('\n=== Image Paths ===')
        print('image_paths field:', note.image_paths)

        # Parse the image block to see its structure
        if note.raw_notes:
            blocks = json.loads(note.raw_notes)
            for block in blocks:
                if block.get('type') == 'image':
                    print('\n=== Image Block Structure ===')
                    print(json.dumps(block, indent=2))
    else:
        print('Note not found')
