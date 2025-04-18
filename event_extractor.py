import os
from datetime import datetime, timedelta
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish
from typing import Dict, Any, Optional

class EventExtractor:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0.7
        )

    async def get_current_time(self) -> str:
        """Get the current time in a formatted string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def extract_event_details(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract event details from the user's message using AI."""
        try:
            # First, determine if we need current time
            time_check_prompt = f"""
            Analyze if the following message requires the current time to understand the event timing:
            "{message}"
            Respond with only 'yes' or 'no'.
            """
            
            time_check_response = self.model.generate_content(time_check_prompt)
            needs_current_time = time_check_response.text.strip().lower() == 'yes'
            
            current_time = await self.get_current_time() if needs_current_time else None
            
            # Create the main extraction prompt
            extraction_prompt = PromptTemplate(
                input_variables=["message", "current_time"],
                template="""
                Extract event details from the following message. If current_time is provided, use it as reference.
                
                Message: {message}
                Current Time: {current_time}
                
                Extract the following information in JSON format:
                - summary: The title/description of the event
                - start_time: The start time in YYYY-MM-DD HH:MM format
                - end_time: The end time in YYYY-MM-DD HH:MM format (default to 1 hour after start if not specified)
                - description: Any additional details about the event
                
                If any information is missing or unclear, return null for that field.
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