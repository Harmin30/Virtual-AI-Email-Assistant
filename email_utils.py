# import imaplib
# import email
# from email.header import decode_header
# import datetime
# from transformers import pipeline
# from models import EmailStatus, Session
# from datetime import datetime as dt
# import os

# import re
# from datetime import datetime, timedelta

# # Reminder

# def detect_reminder(subject, body):
#     reminder_keywords = ['remind', 'reminder', 'remember', 'don’t forget', 'meeting', 'appointment', 'submit', 'deadline', 'due']

#     text = f"{subject.lower()} {body.lower()}"
    
#     if any(keyword in text for keyword in reminder_keywords):
#         # Try to find a date in the format DD-MM-YYYY or DD/MM/YYYY
#         date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', text)
#         if date_match:
#             try:
#                 date_str = date_match.group(1).replace('/', '-')
#                 reminder_date = datetime.strptime(date_str, '%d-%m-%Y')
#                 if reminder_date > datetime.now():
#                     return True, reminder_date
#             except:
#                 pass

#         # If no date, default to tomorrow
#         return True, datetime.now() + timedelta(days=1)
    
#     return False, None

# # 🔍 Load summarizer model once
# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# # 📁 Ensure attachment directory exists
# ATTACHMENT_DIR = os.path.join("static", "attachments")
# os.makedirs(ATTACHMENT_DIR, exist_ok=True)

# # 🧠 Email Classification
# def classify_email(subject, body):
#     spam_keywords = ['win money', 'lottery', 'claim prize', 'free gift', 'urgent help', 'congratulations']
#     work_keywords = ['project', 'deadline', 'qa', 'launch', 'client', 'coordination', 'meeting']
#     combined = f"{subject.lower()} {body.lower()}"
#     if any(w in combined for w in spam_keywords):
#         return 'Spam'
#     elif any(w in combined for w in work_keywords):
#         return 'Work'
#     else:
#         return 'Inbox'

# # ⚠️ Priority Detection
# def determine_priority(subject, body):
#     combined = f"{subject.lower()} {body.lower()}"
#     high_keywords = ['urgent', 'asap', 'immediate', 'critical', 'action required', 'important', 'client escalation']
#     medium_keywords = ['reminder', 'follow up', 'reschedule', 'please check', 'client update', 'awaiting response']

#     if any(word in combined for word in high_keywords):
#         return 'High'
#     elif any(word in combined for word in medium_keywords):
#         return 'Medium'
#     return 'Low'

# # 📝 Summarize email content
# def summarize_email(text):
#     text = text.strip()
#     if len(text.split()) < 8:
#         return text  # Skip summarizing short emails
#     try:
#         summary = summarizer(text, max_length=60, min_length=10, do_sample=False)
#         return summary[0]['summary_text']
#     except Exception as e:
#         print(f"[❌ Summarization failed]: {e}")
#         return text

# # 📩 Fetch unseen emails and store in DB
# def fetch_emails(email_address, imap_password):
#     emails = []

#     try:
#         imap = imaplib.IMAP4_SSL("imap.gmail.com")
#         imap.login(email_address, imap_password)
#         imap.select("inbox")

#         status, messages = imap.search(None, 'UNSEEN')
#         if status != 'OK':
#             print("❌ Failed to search inbox.")
#             return emails

#         for num in messages[0].split():
#             res, msg_data = imap.fetch(num, "(RFC822)")
#             if res != 'OK':
#                 continue

#             msg = email.message_from_bytes(msg_data[0][1])

#             # 📨 Subject decoding
#             subject_raw = msg.get("Subject", "No Subject")
#             subject, encoding = decode_header(subject_raw)[0]
#             if isinstance(subject, bytes):
#                 try:
#                     subject = subject.decode(encoding or 'utf-8', errors='ignore')
#                 except:
#                     subject = "No Subject"

#             # 👤 Sender
#             from_ = msg.get("From", "Unknown")

#             # 🕒 Timestamp parsing
#             date_ = msg.get("Date", "")
#             try:
#                 timestamp = datetime.datetime.strptime(date_[:25], "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S")
#             except:
#                 timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

#             # 📄 Extract plain text body + attachments
#             body = ""
#             attachments = []

#             if msg.is_multipart():
#                 for part in msg.walk():
#                     content_disposition = str(part.get("Content-Disposition"))
#                     content_type = part.get_content_type()

#                     if content_type == "text/plain" and "attachment" not in content_disposition:
#                         try:
#                             body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
#                         except:
#                             continue

#                     elif "attachment" in content_disposition:
#                         filename = part.get_filename()
#                         if filename:
#                             decoded_filename, encoding = decode_header(filename)[0]
#                             if isinstance(decoded_filename, bytes):
#                                 filename = decoded_filename.decode(encoding or 'utf-8', errors='ignore')
#                             filepath = os.path.join(ATTACHMENT_DIR, filename)
#                             try:
#                                 with open(filepath, "wb") as f:
#                                     f.write(part.get_payload(decode=True))
#                                 attachments.append(filename)
#                             except Exception as e:
#                                 print(f"❌ Failed to save attachment: {filename}", e)
#             else:
#                 try:
#                     body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
#                 except:
#                     body = "Unable to decode email body."

#             # 🔍 Classification, Summary & Priority
#             classification = classify_email(subject, body)
#             summary = summarize_email(body)
#             priority = determine_priority(subject, body)

#             # ✅ Save to DB if not duplicate
#             session = Session()
#             existing = session.query(EmailStatus).filter_by(subject=subject, timestamp=timestamp).first()
#             if not existing:
#                 email_obj = EmailStatus(
#                     subject=subject,
#                     sender=from_,
#                     classification=classification,
#                     summary=summary,
#                     timestamp=dt.strptime(timestamp, "%Y-%m-%dT%H:%M:%S"),
#                     body=body,
#                     priority=priority,
#                     attachments=", ".join(attachments) if attachments else None
#                 )
#                 session.add(email_obj)
#                 session.commit()
                
#             session.close()
            
            

#         imap.logout()

        

#     except Exception as e:
#         print("❌ Error fetching emails:", e)

#     return emails

import imaplib
import email
from email.header import decode_header
import datetime
from transformers import pipeline
from models import EmailStatus, Session
from datetime import datetime as dt, timedelta
import os
import re

# 📁 Ensure attachment directory exists
ATTACHMENT_DIR = os.path.join("static", "attachments")
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

# 🔍 Load summarizer model once
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# 🧠 Email Classification
def classify_email(subject, body):
    spam_keywords = ['win money', 'lottery', 'claim prize', 'free gift', 'urgent help', 'congratulations']
    work_keywords = ['project', 'deadline', 'qa', 'launch', 'client', 'coordination', 'meeting']
    combined = f"{subject.lower()} {body.lower()}"
    if any(w in combined for w in spam_keywords):
        return 'Spam'
    elif any(w in combined for w in work_keywords):
        return 'Work'
    else:
        return 'Inbox'

# ⚠️ Priority Detection
def determine_priority(subject, body):
    combined = f"{subject.lower()} {body.lower()}"
    high_keywords = ['urgent', 'asap', 'immediate', 'critical', 'action required', 'important', 'client escalation']
    medium_keywords = ['reminder', 'follow up', 'reschedule', 'please check', 'client update', 'awaiting response']
    if any(word in combined for word in high_keywords):
        return 'High'
    elif any(word in combined for word in medium_keywords):
        return 'Medium'
    return 'Low'

# 📌 Reminder Detection
def detect_reminder(subject, body):
    keywords = ['remind', 'reminder', 'remember', 'don’t forget', 'meeting', 'appointment', 'submit', 'deadline', 'due']
    text = f"{subject.lower()} {body.lower()}"
    if any(k in text for k in keywords):
        date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', text)
        if date_match:
            try:
                date_str = date_match.group(1).replace('/', '-')
                reminder_date = datetime.datetime.strptime(date_str, '%d-%m-%Y')
                if reminder_date > datetime.datetime.now():
                    return True, reminder_date
            except:
                pass
        return True, datetime.datetime.now() + timedelta(days=1)
    return False, None

# 📝 Summarization
def summarize_email(text):
    text = text.strip()
    if len(text.split()) < 8:
        return text
    try:
        summary = summarizer(text, max_length=60, min_length=10, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"[❌ Summarization failed]: {e}")
        return text

# 📩 Fetch and Process Emails
def fetch_emails(email_address, imap_password):
    emails = []

    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(email_address, imap_password)
        imap.select("inbox")

        status, messages = imap.search(None, 'UNSEEN')
        if status != 'OK':
            print("❌ Failed to search inbox.")
            return emails

        for num in messages[0].split():
            res, msg_data = imap.fetch(num, "(RFC822)")
            if res != 'OK':
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            subject_raw = msg.get("Subject", "No Subject")
            subject, encoding = decode_header(subject_raw)[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8', errors='ignore') if encoding else subject.decode()

            from_ = msg.get("From", "Unknown")

            date_ = msg.get("Date", "")
            try:
                timestamp = datetime.datetime.strptime(date_[:25], "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S")
            except:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            body = ""
            attachments = []

            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    content_type = part.get_content_type()

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        except:
                            continue
                    elif "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            decoded_filename, enc = decode_header(filename)[0]
                            if isinstance(decoded_filename, bytes):
                                filename = decoded_filename.decode(enc or 'utf-8', errors='ignore')
                            filepath = os.path.join(ATTACHMENT_DIR, filename)
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            attachments.append(filename)
            else:
                try:
                    body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                except:
                    body = "Unable to decode email body."

            # AI Processing
            classification = classify_email(subject, body)
            summary = summarize_email(body)
            priority = determine_priority(subject, body)

            session = Session()
            existing = session.query(EmailStatus).filter_by(subject=subject, timestamp=timestamp).first()
            if not existing:
                email_obj = EmailStatus(
                    subject=subject,
                    sender=from_,
                    classification=classification,
                    summary=summary,
                    timestamp=dt.strptime(timestamp, "%Y-%m-%dT%H:%M:%S"),
                    body=body,
                    priority=priority,
                    attachments=", ".join(attachments) if attachments else None
                )
                session.add(email_obj)
                session.commit()

                # ✅ Save reminder if applicable
                is_reminder, reminder_time = detect_reminder(subject, body)
                if is_reminder:
                    reminder = Reminder(
                        email_id=email_obj.id,
                        subject=subject,
                        sender=from_,
                        content=body,
                        reminder_time=reminder_time
                    )
                    session.add(reminder)
                    session.commit()
                    

            session.close()

        imap.logout()

    except Exception as e:
        print("❌ Error fetching emails:", e)

    return emails
