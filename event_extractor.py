import os
import logging
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
            base_url="http://localhost:11434"
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
            time_check_response = self.llm(time_check_prompt)
            logger.debug(f"LLM time check response: {time_check_response}")
            
            needs_current_time = "بله" in time_check_response.strip()
            logger.info(f"Current time needed: {needs_current_time}")
            
            current_time = await self.get_current_time() if needs_current_time else None
            
            # Create the main extraction prompt
            extraction_prompt = PromptTemplate(
                input_variables=["message", "current_time"],
                template="""
                اطلاعات رویداد را از پیام زیر استخراج کن. اگر زمان فعلی داده شده، از آن به عنوان مرجع استفاده کن.
                
                پیام: {message}
                زمان فعلی: {current_time}
                
                اطلاعات زیر را به صورت JSON استخراج کن:
                - summary: عنوان/توضیحات رویداد
                - start_time: زمان شروع به فرمت YYYY-MM-DD HH:MM
                - end_time: زمان پایان به فرمت YYYY-MM-DD HH:MM (اگر مشخص نشده، یک ساعت بعد از زمان شروع در نظر بگیر)
                - description: جزئیات اضافی رویداد
                
                اگر هر اطلاعاتی نامشخص یا ناقص است، برای آن فیلد null قرار بده.
                """
            )
            
            logger.debug("Creating LLM chain for event extraction")
            chain = LLMChain(llm=self.llm, prompt=extraction_prompt)
            
            logger.debug(f"Sending extraction request to LLM with message: {message}")
            response = await chain.ainvoke(
                {"message": message, "current_time": current_time}
            )
            logger.debug(f"LLM extraction response: {response}")
            
            # Parse the response and convert to datetime objects
            try:
                event_details = eval(response)
                logger.info(f"Parsed event details: {event_details}")
            except Exception as e:
                logger.error(f"Failed to parse LLM response: {str(e)}")
                logger.error(f"Raw response: {response}")
                return None
            
            if not event_details.get('start_time'):
                logger.warning("No start time found in event details")
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