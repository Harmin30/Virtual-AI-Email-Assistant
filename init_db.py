# init_db.py
from models import Base, engine

# Create all tables in the database
Base.metadata.create_all(engine)

print("✅ Tables created successfully in emails.db")
