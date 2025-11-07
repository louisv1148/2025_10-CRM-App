import sys
import json
sys.path.insert(0, 'src-tauri/python')

from database import Note, get_session

with get_session() as session:
    note = session.query(Note).filter(Note.name.like('%Reverence - Profu FU%')).first()
    if note and note.raw_notes:
        blocks = json.loads(note.raw_notes)
        print(f"Total blocks: {len(blocks)}")
        print(f"\nBlock types found:")
        types = {}
        for block in blocks:
            block_type = block.get('type', 'unknown')
            types[block_type] = types.get(block_type, 0) + 1

        for block_type, count in types.items():
            print(f"  {block_type}: {count}")

        # Find and print image blocks
        print(f"\n=== Image blocks ===")
        for i, block in enumerate(blocks):
            if block.get('type') == 'image':
                print(f"\nImage block #{i}:")
                print(json.dumps(block, indent=2)[:500])
    else:
        print("Note or raw_notes not found")
