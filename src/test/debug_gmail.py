# debug_gmail.py

import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def debug_gmail():
    """Debug Gmail-Zugriff Schritt für Schritt"""
    print("🔍 Gmail Debug Session gestartet...")

    # Setup Gmail API
    creds = None
    if os.path.exists('../token.json'):
        creds = Credentials.from_authorized_user_file('../token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('../token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # 1. Welcher Account ist authentifiziert?
    print("\n1️⃣ Prüfe authentifizierten Account...")
    try:
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')
        total_messages = profile.get('messagesTotal', 0)
        print(f"✅ Angemeldet als: {email_address}")
        print(f"📊 Gesamt Nachrichten im Account: {total_messages}")

        if email_address != "jutastrasse.wg@gmail.com":
            print(f"⚠️  ACHTUNG: Sie sind angemeldet als {email_address}")
            print(f"   Aber wir erwarten: jutastrasse.wg@gmail.com")
            print(f"   Löschen Sie token.json und melden Sie sich mit dem richtigen Account an!")
    except Exception as e:
        print(f"❌ Fehler beim Abrufen des Profils: {e}")
        return

    # 2. Alle E-Mails ohne Filter
    print("\n2️⃣ Teste: Alle E-Mails (ohne Filter)...")
    try:
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        all_messages = results.get('messages', [])
        print(f"📧 Gefunden: {len(all_messages)} E-Mails (ohne Filter)")

        if all_messages:
            # Details der ersten E-Mail
            first_msg = service.users().messages().get(userId='me', id=all_messages[0]['id']).execute()
            headers = first_msg['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Kein Betreff')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unbekannter Absender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unbekanntes Datum')

            print(f"📨 Erste E-Mail:")
            print(f"   Von: {sender}")
            print(f"   Betreff: {subject}")
            print(f"   Datum: {date}")
        else:
            print("❌ Keine E-Mails gefunden! Der Account scheint leer zu sein.")
            return
    except Exception as e:
        print(f"❌ Fehler beim Abrufen aller E-Mails: {e}")
        return

    # 3. Teste verschiedene Datumsbereiche
    print("\n3️⃣ Teste verschiedene Datumsbereiche...")

    date_ranges = [
        ("Letzte 1 Tag", 1),
        ("Letzte 3 Tage", 3),
        ("Letzte 7 Tage", 7),
        ("Letzte 30 Tage", 30),
        ("Letzte 90 Tage", 90)
    ]

    for range_name, days in date_ranges:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            query = f"after:{start_date.strftime('%Y/%m/%d')}"

            results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
            messages = results.get('messages', [])
            print(f"📅 {range_name}: {len(messages)} E-Mails")

        except Exception as e:
            print(f"❌ Fehler bei {range_name}: {e}")

    # 4. Teste ohne Datumsfilter aber mit Anzahl-Limit
    print("\n4️⃣ Letzte 20 E-Mails (chronologisch)...")
    try:
        results = service.users().messages().list(userId='me', maxResults=20).execute()
        recent_messages = results.get('messages', [])

        print(f"📧 Zeige Details der letzten {len(recent_messages)} E-Mails:")

        for i, msg in enumerate(recent_messages[:5], 1):  # Zeige erste 5
            try:
                details = service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = details['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Kein Betreff')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unbekannter Absender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unbekanntes Datum')

                print(f"  {i}. Von: {sender[:50]}...")
                print(f"     Betreff: {subject[:50]}...")
                print(f"     Datum: {date}")
                print()
            except Exception as e:
                print(f"  {i}. ❌ Fehler beim Abrufen der E-Mail: {e}")

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der letzten E-Mails: {e}")

    print("\n✅ Debug abgeschlossen!")
    print("💡 Überprüfen Sie:")
    print("   1. Sind Sie mit jutastrasse.wg@gmail.com angemeldet?")
    print("   2. Sind die E-Mails innerhalb der letzten 7 Tage?")
    print("   3. Falls nein, erhöhen Sie days_back in email_reader.py")


if __name__ == "__main__":
    debug_gmail()