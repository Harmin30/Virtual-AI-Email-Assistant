def categorize_email(subject, summary):
    spam_keywords = ['win money', 'lottery', 'claim prize', 'free gift', 'urgent help', 'congratulations']
    work_keywords = ['project', 'deadline', 'qa', 'launch', 'client', 'coordination', 'meeting']
    combined = f"{subject.lower()} {summary.lower()}"
    if any(w in combined for w in spam_keywords):
        return 'Spam'
    elif any(w in combined for w in work_keywords):
        return 'Work'
    else:
        return 'Inbox'

def assign_priority(subject, summary):
    content = f"{subject.lower()} {summary.lower()}"
    if any(word in content for word in ['urgent', 'asap', 'important', 'immediately']):
        return 'High'
    elif any(word in content for word in ['reminder', 'follow-up', 'update']):
        return 'Medium'
    return 'Low'
