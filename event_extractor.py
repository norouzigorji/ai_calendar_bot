import os
import logging
import json
import asyncio
from datetime import datetime, timedelta
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class EventExtractor:
    def __init__(self):
        # Initialize Ollama with Persian model
        self.llm = Ollama(
            model="mshojaei77/gemma3persian",
            base_url="http://localhost:11434",
            temperature=0.1,  # Added lower temperature for more deterministic outputs
            timeout=1800  # Increased to 30 minutes to accommodate low-end hardware
        )
        logger.info("EventExtractor initialized with Ollama model")

    async def get_current_time(self) -> str:
        """Get the current time in a formatted string."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"Current time retrieved: {current_time}")
        return current_time

    async def extract_event_details(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract event details from the user's message using AI."""
        logger.info(f"Starting event extraction for message: {message}")
        
        try:
            # First, determine if we need current time
            time_check_prompt = f"""
            تحلیل کن که آیا پیام زیر برای درک زمان رویداد نیاز به زمان فعلی دارد:
            "{message}"
            فقط با "بله" یا "خیر" پاسخ بده.
            """
            
            logger.debug(f"Sending time check prompt to LLM: {time_check_prompt}")
            logger.info("Please wait, this may take several minutes due to CPU processing of the AI model...")
            
            # Use a timeout for the LLM call
            try:
                time_check_response = await asyncio.wait_for(
                    asyncio.to_thread(lambda: self.llm(time_check_prompt)),
                    timeout=900  # Increased to 15 minutes
                )
                logger.debug(f"LLM time check response: {time_check_response}")
            except asyncio.TimeoutError:
                logger.error("Time check LLM call timed out after 15 minutes")
                return None
                
            needs_current_time = "بله" in time_check_response.strip()
            logger.info(f"Current time needed: {needs_current_time}")
            
            current_time = await self.get_current_time() if needs_current_time else None
            
            # Create a simpler direct extraction prompt that returns JSON
            extraction_prompt = f"""
            اطلاعات رویداد را از پیام زیر استخراج کن. اگر زمان فعلی داده شده، از آن به عنوان مرجع استفاده کن.
            
            پیام: {message}
            زمان فعلی: {current_time}
            
            اطلاعات را به صورت دقیقاً به فرمت JSON با فیلدهای زیر استخراج کن:
            {{
                "summary": "عنوان رویداد",
                "start_time": "YYYY-MM-DD HH:MM",
                "end_time": "YYYY-MM-DD HH:MM",
                "description": "توضیحات اضافی"
            }}
            
            اگر هر اطلاعاتی نامشخص است، برای آن فیلد از null استفاده کن.
            """
            
            logger.debug(f"Sending extraction request to LLM with direct prompt")
            logger.info("Extracting event details, this may take several minutes...")
            
            # Use a timeout for the LLM call
            try:
                extraction_response = await asyncio.wait_for(
                    asyncio.to_thread(lambda: self.llm(extraction_prompt)),
                    timeout=1200  # Increased to 20 minutes
                )
                logger.debug(f"LLM extraction raw response: {extraction_response}")
            except asyncio.TimeoutError:
                logger.error("Extraction LLM call timed out after 20 minutes")
                return None
            
            # Try to extract the JSON part from the response
            try:
                # Look for JSON in the response (sometimes the model adds text before/after the JSON)
                import re
                json_match = re.search(r'({[\s\S]*})', extraction_response)
                if json_match:
                    json_str = json_match.group(1)
                    event_details = json.loads(json_str)
                    logger.info(f"Parsed event details: {event_details}")
                else:
                    logger.error("No JSON found in LLM response")
                    return None
            except Exception as e:
                logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
                logger.error(f"Raw response: {extraction_response}")
                return None
            
            if not event_details.get('summary') or not event_details.get('start_time'):
                logger.warning("Missing required fields in event details")
                return None
                
            # Convert string times to datetime objects
            try:
                event_details['start_time'] = datetime.strptime(
                    event_details['start_time'], 
                    '%Y-%m-%d %H:%M'
                )
                logger.debug(f"Parsed start time: {event_details['start_time']}")
                
                if event_details.get('end_time'):
                    event_details['end_time'] = datetime.strptime(
                        event_details['end_time'], 
                        '%Y-%m-%d %H:%M'
                    )
                    logger.debug(f"Parsed end time: {event_details['end_time']}")
                else:
                    # Default to 1 hour duration if end time not specified
                    event_details['end_time'] = event_details['start_time'] + timedelta(hours=1)
                    logger.debug(f"Using default end time: {event_details['end_time']}")
                
                logger.info("Event extraction completed successfully")
                return event_details
                
            except ValueError as e:
                logger.error(f"Failed to parse datetime: {str(e)}")
                logger.error(f"Event details: {event_details}")
                return None
            
        except Exception as e:
            logger.error(f"Error in event extraction: {str(e)}", exc_info=True)
            return None 