import os
from datetime import datetime, timedelta
from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional

class EventExtractor:
    def __init__(self):
        # Initialize Ollama with Persian model
        self.llm = Ollama(
            model="mshojaei77/gemma3persian",
            base_url="http://localhost:11434"
        )

    async def get_current_time(self) -> str:
        """Get the current time in a formatted string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def extract_event_details(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract event details from the user's message using AI."""
        try:
            # First, determine if we need current time
            time_check_prompt = f"""
            تحلیل کن که آیا پیام زیر برای درک زمان رویداد نیاز به زمان فعلی دارد:
            "{message}"
            فقط با "بله" یا "خیر" پاسخ بده.
            """
            
            time_check_response = self.llm(time_check_prompt)
            needs_current_time = "بله" in time_check_response.strip()
            
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
            
            chain = LLMChain(llm=self.llm, prompt=extraction_prompt)
            response = await chain.arun(
                message=message,
                current_time=current_time
            )
            
            # Parse the response and convert to datetime objects
            event_details = eval(response)
            
            if not event_details.get('start_time'):
                return None
                
            # Convert string times to datetime objects
            event_details['start_time'] = datetime.strptime(
                event_details['start_time'], 
                '%Y-%m-%d %H:%M'
            )
            
            if event_details.get('end_time'):
                event_details['end_time'] = datetime.strptime(
                    event_details['end_time'], 
                    '%Y-%m-%d %H:%M'
                )
            else:
                # Default to 1 hour duration if end time not specified
                event_details['end_time'] = event_details['start_time'] + timedelta(hours=1)
            
            return event_details
            
        except Exception as e:
            print(f"Error in event extraction: {str(e)}")
            return None 