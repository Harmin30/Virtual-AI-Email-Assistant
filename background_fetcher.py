from email_helpers import categorize_email, assign_priority
from email_utils import fetch_emails
from models import Session, EmailStatus
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env for EMAIL, APP_PASSWORD
load_dotenv()
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def background_fetch_emails():
    while True:
        session = Session()
        emails = fetch_emails(EMAIL, APP_PASSWORD)

        existing_emails = {
            (e.subject, e.timestamp)
            for e in session.query(EmailStatus.subject, EmailStatus.timestamp).all()
        }

        for e in emails:
            if not e['subject']:
                e['subject'] = "(No Subject)"
            ts = datetime.strptime(e['timestamp'], "%Y-%m-%dT%H:%M:%S")
            key = (e['subject'], ts)
            if key not in existing_emails:
                category = categorize_email(e['subject'], e['summary'])
                priority = assign_priority(e['subject'], e['summary'])
                new_email = EmailStatus(
                    subject=e['subject'],
                    sender=e['from'],
                    summary=e['summary'],
                    timestamp=ts,
                    classification=category.title(),
                    read=False,
                    archived=False,
                    priority=priority
                )
                session.add(new_email)
                print(f"✅ New email added: {e['subject']}")

        session.commit()
        session.close()
        time.sleep(60)
