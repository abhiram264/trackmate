# quick_migrate.py
from sqlalchemy import text
from app.database import engine

queries = [
    "ALTER TABLE lost_items ADD COLUMN description_embedding TEXT",
    "ALTER TABLE lost_items ADD COLUMN image_embedding TEXT", 
    "ALTER TABLE lost_items ADD COLUMN combined_embedding TEXT",
    "ALTER TABLE found_items ADD COLUMN description_embedding TEXT",
    "ALTER TABLE found_items ADD COLUMN image_embedding TEXT",
    "ALTER TABLE found_items ADD COLUMN combined_embedding TEXT"
]

with engine.connect() as conn:
    for q in queries:
        try:
            conn.execute(text(q))
        except:
            pass  # Column might already exist
    conn.commit()

print("✅ Basic migration done!")
