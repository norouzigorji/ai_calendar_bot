import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import asyncio
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

class GoogleCalendarManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.credentials_file = 'credentials.json'
        self.token_file = 'token.pickle'
        logger.info("GoogleCalendarManager initialized")
        
    def _get_credentials(self, user_id: str) -> Optional[Credentials]:
        """Get or refresh Google Calendar credentials."""
        logger.debug(f"Getting credentials for user {user_id}")
        creds = None
        
        # Load token from file if it exists
        token_path = f'tokens/{user_id}_{self.token_file}'
        if os.path.exists(token_path):
            logger.debug(f"Found existing token at {token_path}")
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                logger.debug("Successfully loaded credentials from token file")
            except Exception as e:
                logger.error(f"Error loading token file: {str(e)}")
                # If the token file is corrupted, remove it and try again
                os.remove(token_path)
                logger.info(f"Removed corrupted token file: {token_path}")
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            logger.info(f"Credentials for user {user_id} need to be refreshed or created")
            try:
                if creds and creds.expired and creds.refresh_token:
                    logger.debug("Refreshing expired credentials")
                    creds.refresh(Request())
                    logger.debug("Credentials refreshed successfully")
                else:
                    logger.info("Creating new credentials via OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("OAuth flow completed successfully")
                
                # Save the credentials for the next run
                os.makedirs('tokens', exist_ok=True)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                logger.debug(f"Saved credentials to {token_path}")
            except Exception as e:
                logger.error(f"Error obtaining credentials: {str(e)}", exc_info=True)
                return None
        
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
        logger.info(f"Creating calendar event for user {user_id}: {summary}")
        
        try:
            # Get credentials in a separate thread to avoid blocking
            creds = await asyncio.to_thread(self._get_credentials, user_id)
            if not creds:
                logger.error(f"Failed to obtain credentials for user {user_id}")
                return None

            # Build the calendar service
            service = await asyncio.to_thread(
                lambda: build('calendar', 'v3', credentials=creds)
            )
            logger.debug("Calendar service built successfully")

            # Prepare the event data
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
            logger.debug(f"Event data prepared: {event}")

            # Insert the event into Google Calendar
            event_result = await asyncio.to_thread(
                lambda: service.events().insert(
                    calendarId='primary',
                    body=event
                ).execute()
            )
            
            event_link = event_result.get('htmlLink')
            logger.info(f"Event created successfully: {event_link}")
            return event_link

        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}", exc_info=True)
            return None 