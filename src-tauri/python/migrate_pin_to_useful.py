"""
Migration script to consolidate pin and useful fields.
- If pin is set (not null/empty), set useful = True
- If useful is already True, keep it True
"""

from database import get_session, Note

def migrate_pin_to_useful():
    with get_session() as session:
        notes = session.query(Note).all()

        updated_count = 0
        for note in notes:
            # If pin has any value and useful is not already True, set useful to True
            if note.pin and not note.useful:
                note.useful = True
                updated_count += 1
                print(f"Updated note {note.id} ({note.name}): pin='{note.pin}' -> useful=True")
            elif note.pin and note.useful:
                print(f"Note {note.id} ({note.name}): already has useful=True, pin='{note.pin}'")

        session.commit()
        print(f"\nMigration complete! Updated {updated_count} notes.")
        print(f"Total notes with useful=True: {sum(1 for n in notes if n.useful)}")

if __name__ == "__main__":
    migrate_pin_to_useful()
