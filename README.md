# AI Calendar Bot

A Telegram bot that uses AI to understand natural language and create events in Google Calendar.

## Author
👨‍💻 [AmirHossein NorouziGorji](https://github.com/norouzigorji)

## Features

- Natural language processing for event creation
- Integration with Google Calendar
- Smart time and date extraction
- Persian language support
- User-specific calendar management

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google API credentials
- Gemini API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai_calendar_bot.git
cd ai_calendar_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GOOGLE_API_KEY=your_gemini_api_key
```

4. Set up Google Calendar API:
- Go to the [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project
- Enable the Google Calendar API
- Create OAuth 2.0 credentials
- Download the credentials and save as `credentials.json` in the project root

## Usage

1. Start the bot:
```bash
python main.py
```

2. Open Telegram and start a conversation with your bot

3. Send messages in natural language to create events. Examples:
- "برای فردا ساعت ۱۱ یک جلسه با تیم برنامه‌نویسی تنظیم کن"
- "یادآوری کن که فردا ساعت ۳ بعدازظهر با دکتر ملاقات دارم"
- "برای شنبه هفته بعد ساعت ۱۰ صبح یک جلسه کاری تنظیم کن"

## Project Structure

```
ai_calendar_bot/
│
├── main.py                 # Main bot implementation
├── calendar_utils.py       # Google Calendar integration
├── event_extractor.py      # AI-powered event extraction
├── credentials.json        # Google API credentials
├── requirements.txt        # Python dependencies
└── tokens/                 # User-specific OAuth tokens
```

## Security Notes

- Never share your `credentials.json` or `.env` files
- Keep your API keys secure
- The `tokens` directory contains sensitive user data and should be properly secured

## License

MIT License 