import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from typing import Optional

class GoogleCalendarManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.pickle'
        
    def _get_credentials(self, user_id: str) -> Optional[Credentials]:
        """Get or refresh Google Calendar credentials."""
        creds = None
        
        # Load token from file if it exists
        token_path = f'tokens/{user_id}_{self.token_file}'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            os.makedirs('tokens', exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    async def create_event(
        self,
        user_id: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str = ''
    ) -> Optional[str]:
        """Create an event in Google Calendar."""
        try:
            creds = self._get_credentials(user_id)
            if not creds:
                return None

            service = build('calendar', 'v3', credentials=creds)

            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Tehran',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Tehran',
                },
            }

            event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return event.get('htmlLink')

        except Exception as e:
            print(f"Error creating calendar event: {str(e)}")
            return None 