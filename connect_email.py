# connect_email.py
import imaplib
import email
import datetime
from email.header import decode_header, make_header

def connect_to_gmail(email_address, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')  
    mail.login(email_address, password)
    mail.select('inbox')
    return mail

def fetch_uber_receipts_by_month(mail, month, year):
    emails_list = []
    start_date = datetime.date(year, month, 1)
    next_month = datetime.date(year + 1, 1, 1) if month == 12 else datetime.date(year, month + 1, 1)
    start_str = start_date.strftime("%d-%b-%Y")
    next_str = next_month.strftime("%d-%b-%Y")
    
    # Filtra apenas emails de noreply@uber.com dentro do período
    criteria = (
        f'(FROM "noreply@uber.com" '
        f'SINCE "{start_str}" BEFORE "{next_str}" '
        f'OR OR SUBJECT "receipt" SUBJECT "recibo" SUBJECT "viagem")'
    )

    status, messages = mail.search(None, criteria)
    
    if status == 'OK':
        email_ids = messages[0].split()
        if not email_ids:
            return emails_list
        
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Decodifica corretamente o assunto
                raw_subject = email_message['Subject'] or ""
                decoded_subject = str(make_header(decode_header(raw_subject)))
                from_ = email_message['From']
                date = email_message['Date']

                # Extrai o corpo (priorizando HTML)
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))
                        if ctype == "text/html" and "attachment" not in cdispo:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                        elif ctype == "text/plain" and "attachment" not in cdispo and not body:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                else:
                    body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")

                emails_list.append({
                    "subject": decoded_subject,
                    "from": from_,
                    "date": date,
                    "content": body
                })
    return emails_list
