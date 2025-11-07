import sys
sys.path.insert(0, 'src-tauri/python')

from database import Note, get_session

with get_session() as session:
    # Find the note mentioned in the screenshot
    note = session.query(Note).filter(Note.name.like('%Reverence - Profu FU%')).first()
    if note:
        print('Note ID:', note.id)
        print('Name:', note.name)
        print('Date:', note.date)
        print('Raw notes length:', len(note.raw_notes) if note.raw_notes else 0)
        print('Content text length:', len(note.content_text) if note.content_text else 0)
        print('\n=== First 1000 chars of raw_notes ===')
        print(note.raw_notes[:1000] if note.raw_notes else 'None')
        print('\n=== First 1000 chars of content_text ===')
        print(note.content_text[:1000] if note.content_text else 'None')
    else:
        print('Note not found')
