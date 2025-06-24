# email_reader.py

import os
import base64
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import EMAIL_CONFIG

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailReader:
    def __init__(self):
        self.service = None
        self.credentials = None
        self.setup_gmail_api()

    def setup_gmail_api(self):
        """Set up Gmail API authentication"""
        creds = None

        # Load existing credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # You need to download credentials.json from Google Cloud Console
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API authenticated successfully")

    def get_recent_emails(self, days_back: int = 7) -> List[Dict]:
        """Get all recent emails (assuming all are rental applications)"""
        try:
            # Calculate date range (add 1 day to end_date to include today)
            end_date = datetime.now() + timedelta(days=1)
            start_date = end_date - timedelta(days=days_back + 1)

            # Simple query - just get all emails in date range
            query = f"after:{start_date.strftime('%Y/%m/%d')}"
            print(f"🔍 Getting all emails from last {days_back} days...")
            print(f"🔍 Query: {query}")

            # Search for emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()

            messages = results.get('messages', [])
            print(f"📧 Found {len(messages)} emails to process")

            # Get detailed email data
            email_data = []
            for message in messages:
                email_details = self.get_email_details(message['id'])
                if email_details:
                    email_data.append(email_details)

            return email_data

        except HttpError as error:
            print(f"❌ An error occurred: {error}")
            return []

    def get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed information from a specific email"""
        try:
            # Get the email
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = self.get_header_value(headers, 'Subject')
            sender = self.get_header_value(headers, 'From')
            date_str = self.get_header_value(headers, 'Date')

            # Extract email body
            body = self.extract_email_body(message['payload'])

            # Parse date
            email_date = self.parse_email_date(date_str)

            email_data = {
                'id': message_id,
                'subject': subject or 'No Subject',
                'sender': sender or 'Unknown Sender',
                'date': email_date,
                'body': body or 'No Body Content',
                'raw_date': date_str
            }

            print(f"📨 Processed email from: {email_data['sender']}")
            return email_data

        except HttpError as error:
            print(f"❌ Error getting email details: {error}")
            return None

    def get_header_value(self, headers: List[Dict], name: str) -> Optional[str]:
        """Extract header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None

    def extract_email_body(self, payload: Dict) -> str:
        """Extract text content from email payload"""
        body = ""

        if 'parts' in payload:
            # Multi-part email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if no plain text
                    if not body:
                        data = part['body']['data']
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Single part email
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body.strip()

    def parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime object"""
        try:
            # This is a simplified parser - you might need to handle more formats
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now()


# Test function
def test_email_reader():
    """Test the email reader functionality"""
    print("🚀 Testing Email Reader...")

    reader = EmailReader()
    emails = reader.get_recent_emails(days_back=7)

    print(f"\n📊 Summary:")
    print(f"Found {len(emails)} emails (all assumed to be rental applications)")

    for i, email in enumerate(emails[:3], 1):  # Show first 3 emails
        print(f"\n{i}. From: {email['sender']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Date: {email['date']}")
        print(f"   Body preview: {email['body'][:100]}...")


if __name__ == "__main__":
    test_email_reader()