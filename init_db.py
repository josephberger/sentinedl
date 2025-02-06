from app.database import init_db, SessionLocal, engine
from app.models import Base, User
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import OperationalError

# Step 1: Ensure the database is created
print("Initializing database...")
Base.metadata.create_all(engine)  # Explicitly create tables

# Step 2: Create a default admin user
session = SessionLocal()

try:
    # Ensure the users table exists before querying
    if not session.query(User).first():  # Check if any users exist
        hashed_password = generate_password_hash("password")
        admin_user = User(username="admin", password_hash=hashed_password)
        session.add(admin_user)
        session.commit()
        print("[I] Default admin user created: Username: admin | Password: password")
    else:
        print("[I] Admin user already exists.")

except OperationalError as e:
    print(f"[X] Database error: {e}")
    print("Make sure your database is properly initialized.")

finally:
    session.close()

print("[!] Database setup complete.")
