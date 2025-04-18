import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from event_extractor import EventExtractor
from calendar_utils import GoogleCalendarManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CalendarBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        logger.info("Initializing CalendarBot components")
        self.event_extractor = EventExtractor()
        self.calendar_manager = GoogleCalendarManager()
        logger.info("CalendarBot initialized successfully")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        logger.info(f"Start command received from user {update.effective_user.id}")
        welcome_message = (
            "👋 سلام! من ربات تقویم هوشمند هستم.\n\n"
            "می‌توانید به من بگویید چه رویدادی را در تقویم ثبت کنم.\n"
            "مثال: 'برای فردا ساعت ۱۱ یک جلسه با تیم برنامه‌نویسی تنظیم کن'"
        )
        await update.message.reply_text(welcome_message)
        logger.debug("Welcome message sent")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the user message and process the event request."""
        user_id = update.effective_user.id
        user_message = update.message.text
        logger.info(f"Message received from user {user_id}: {user_message}")

        try:
            # Extract event details using the event extractor
            logger.debug("Starting event extraction process")
            event_details = await self.event_extractor.extract_event_details(user_message)
            
            if not event_details:
                logger.warning(f"Failed to extract event details for user {user_id}")
                await update.message.reply_text(
                    "متأسفانه نتوانستم اطلاعات رویداد را از پیام شما استخراج کنم. "
                    "لطفاً دوباره با جزئیات بیشتر توضیح دهید."
                )
                return

            logger.info(f"Event details extracted successfully: {event_details}")

            # Create the event in Google Calendar
            logger.debug("Attempting to create event in Google Calendar")
            event_link = await self.calendar_manager.create_event(
                user_id=user_id,
                summary=event_details['summary'],
                start_time=event_details['start_time'],
                end_time=event_details['end_time'],
                description=event_details.get('description', '')
            )

            if event_link:
                logger.info(f"Event created successfully for user {user_id}")
                response = (
                    f"✅ رویداد با موفقیت در تقویم شما ثبت شد!\n\n"
                    f"📝 عنوان: {event_details['summary']}\n"
                    f"⏰ زمان: {event_details['start_time'].strftime('%Y-%m-%d %H:%M')}\n"
                    f"🔗 لینک رویداد: {event_link}"
                )
            else:
                logger.error(f"Failed to create event in Google Calendar for user {user_id}")
                response = "❌ متأسفانه در ثبت رویداد مشکلی پیش آمد. لطفاً دوباره تلاش کنید."

            await update.message.reply_text(response)
            logger.debug("Response sent to user")

        except Exception as e:
            logger.error(f"Error processing message from user {user_id}: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
            )

    def run(self):
        """Start the bot."""
        logger.info("Starting CalendarBot")
        try:
            application = Application.builder().token(self.token).build()

            # Add handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

            # Start the bot
            logger.info("Bot is running and ready to receive messages")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}", exc_info=True)
            raise

if __name__ == '__main__':
    try:
        bot = CalendarBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True) 