from models import Session, User

admin_email = "admin@gmail.com"

session = Session()
admin = session.query(User).filter_by(email=admin_email).first()

if admin:
    admin.is_admin = True
    session.commit()
    print(f"✅ '{admin_email}' is now marked as admin.")
else:
    # Create new admin user
    admin = User(
        email=admin_email,
        email_address="admin@gmail.com",
        imap_password_encrypted="dummy",  # not used now
        role="admin",
        is_admin=True
    )
    admin.set_password("admin123")  # 👈 Set your desired password
    session.add(admin)
    session.commit()
    print(f"✅ Admin user '{admin_email}' created with password 'admin123'.")

session.close()
