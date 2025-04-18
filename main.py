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
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CalendarBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.event_extractor = EventExtractor()
        self.calendar_manager = GoogleCalendarManager()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        welcome_message = (
            "👋 سلام! من ربات تقویم هوشمند هستم.\n\n"
            "می‌توانید به من بگویید چه رویدادی را در تقویم ثبت کنم.\n"
            "مثال: 'برای فردا ساعت ۱۱ یک جلسه با تیم برنامه‌نویسی تنظیم کن'"
        )
        await update.message.reply_text(welcome_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the user message and process the event request."""
        try:
            user_message = update.message.text
            user_id = update.effective_user.id

            # Extract event details using the event extractor
            event_details = await self.event_extractor.extract_event_details(user_message)
            
            if not event_details:
                await update.message.reply_text(
                    "متأسفانه نتوانستم اطلاعات رویداد را از پیام شما استخراج کنم. "
                    "لطفاً دوباره با جزئیات بیشتر توضیح دهید."
                )
                return

            # Create the event in Google Calendar
            event_link = await self.calendar_manager.create_event(
                user_id=user_id,
                summary=event_details['summary'],
                start_time=event_details['start_time'],
                end_time=event_details['end_time'],
                description=event_details.get('description', '')
            )

            if event_link:
                response = (
                    f"✅ رویداد با موفقیت در تقویم شما ثبت شد!\n\n"
                    f"📝 عنوان: {event_details['summary']}\n"
                    f"⏰ زمان: {event_details['start_time'].strftime('%Y-%m-%d %H:%M')}\n"
                    f"🔗 لینک رویداد: {event_link}"
                )
            else:
                response = "❌ متأسفانه در ثبت رویداد مشکلی پیش آمد. لطفاً دوباره تلاش کنید."

            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await update.message.reply_text(
                "متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
            )

    def run(self):
        """Start the bot."""
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = CalendarBot()
    bot.run() 