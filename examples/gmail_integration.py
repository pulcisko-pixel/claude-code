"""
Príklad integrácie s Gmail API.

Pred použitím:
1. Aktivujte Gmail API v Google Cloud Console
2. Stiahnite credentials.json
3. Nainštalujte: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

Dokumentácia: https://developers.google.com/gmail/api/quickstart/python
"""

import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from agents.email_auto_labeling.agent import EmailAutoLabelingAgent
from models.email import Email

# Uncomment po nainštalovaní Gmail API knižníc:
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# import base64

load_dotenv()

# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def get_gmail_service():
    """Pripojí sa k Gmail API."""
    # TODO: Implementovať OAuth2 autentifikáciu
    # creds = None
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())
    # service = build('gmail', 'v1', credentials=creds)
    # return service
    raise NotImplementedError("Nainštalujte Gmail API knižnice a odkomentujte kód")


def fetch_unread_emails(service, max_results=10) -> List[Email]:
    """Načíta neprečítané emaily z Gmailu."""
    # TODO: Implementovať načítanie emailov
    # results = service.users().messages().list(
    #     userId='me',
    #     labelIds=['UNREAD'],
    #     maxResults=max_results
    # ).execute()
    # messages = results.get('messages', [])
    #
    # emails = []
    # for message in messages:
    #     msg = service.users().messages().get(userId='me', id=message['id']).execute()
    #
    #     # Parse email
    #     headers = msg['payload']['headers']
    #     subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    #     sender = next((h['value'] for h in headers if h['name'] == 'From'), 'unknown@example.com')
    #
    #     # Get body
    #     if 'parts' in msg['payload']:
    #         parts = msg['payload']['parts']
    #         data = parts[0]['body'].get('data', '')
    #     else:
    #         data = msg['payload']['body'].get('data', '')
    #
    #     body = base64.urlsafe_b64decode(data).decode('utf-8') if data else ''
    #
    #     email = Email(
    #         sender=sender,
    #         subject=subject,
    #         body=body,
    #         received_at=datetime.now().isoformat()
    #     )
    #     emails.append(email)
    #
    # return emails
    raise NotImplementedError("Nainštalujte Gmail API knižnice a odkomentujte kód")


def apply_label_to_email(service, message_id: str, label_name: str):
    """Aplikuje label na email v Gmaile."""
    # TODO: Implementovať aplikáciu labelu
    # # Najprv vytvor label ak neexistuje
    # labels = service.users().labels().list(userId='me').execute()
    # label_id = None
    #
    # for label in labels.get('labels', []):
    #     if label['name'] == label_name:
    #         label_id = label['id']
    #         break
    #
    # if not label_id:
    #     # Vytvor nový label
    #     label_object = {
    #         'name': label_name,
    #         'messageListVisibility': 'show',
    #         'labelListVisibility': 'labelShow'
    #     }
    #     created_label = service.users().labels().create(
    #         userId='me',
    #         body=label_object
    #     ).execute()
    #     label_id = created_label['id']
    #
    # # Aplikuj label
    # service.users().messages().modify(
    #     userId='me',
    #     id=message_id,
    #     body={'addLabelIds': [label_id]}
    # ).execute()
    raise NotImplementedError("Nainštalujte Gmail API knižnice a odkomentujte kód")


def main():
    """Hlavná funkcia - automaticky štítkuje neprečítané emaily v Gmaile."""

    print("📧 Gmail Auto-Labeling Integration\n")

    # Inicializuj agenta
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY nie je nastavený!")
        return

    agent = EmailAutoLabelingAgent(api_key=api_key)

    # Pripoj sa k Gmailu
    print("🔐 Pripájam sa k Gmail API...")
    try:
        service = get_gmail_service()
    except NotImplementedError as e:
        print(f"\n⚠️  {e}")
        print("\nPre integráciu s Gmail:")
        print("1. pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print("2. Nastavte Gmail API v Google Cloud Console")
        print("3. Stiahnite credentials.json")
        print("4. Odkomentujte kód v tomto súbore")
        return

    # Načítaj neprečítané emaily
    print("📨 Načítavam neprečítané emaily...")
    emails = fetch_unread_emails(service, max_results=10)
    print(f"✅ Našiel som {len(emails)} emailov\n")

    # Spracuj každý email
    for i, email in enumerate(emails, 1):
        print(f"{i}. {email.subject[:50]}...")

        # Označ email
        response = agent.label_email(email)

        if response.primary_label:
            label_name = response.primary_label.name
            print(f"   🏷️  Priradený štítok: {label_name}")

            # Aplikuj label v Gmaile
            # apply_label_to_email(service, email.thread_id, label_name)
            print(f"   ✅ Label aplikovaný v Gmaile")
        print()

    print("✅ Hotovo!")


if __name__ == "__main__":
    main()
