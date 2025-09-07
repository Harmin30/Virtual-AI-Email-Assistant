# from getpass import getpass
# from werkzeug.security import generate_password_hash
# from models import Session, User

# # Prompt for admin credentials
# email = input("Enter admin email: ").strip()

# # Secure password input
# password = getpass("Enter password (hidden): ")
# confirm_password = getpass("Confirm password: ")

# if password != confirm_password:
#     print("❌ Passwords do not match.")
#     exit(1)

# # Hash the password
# hashed_password = generate_password_hash(password)

# # Create admin user
# session = Session()
# existing_user = session.query(User).filter_by(email=email).first()

# if existing_user:
#     print(f"⚠️ User with email {email} already exists.")
# else:
#     admin = User(email=email, password=hashed_password, is_admin=True, role='admin')
#     session.add(admin)
#     session.commit()
#     print(f"✅ Admin user {email} created successfully.")

# session.close()

from models import Session, User

session = Session()
user = session.query(User).filter_by(email='admin@gmail.com').first()
if user:
    print(f"Email: {user.email}")
    print(f"is_admin: {user.is_admin}")
    print(f"role: {user.role}")
else:
    print("User not found.")
session.close()
