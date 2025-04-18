# AI Calendar Bot

A Telegram bot that uses AI to understand natural language and create events in Google Calendar.

## Author
👨‍💻 [AmirHossein NorouziGorji](https://github.com/norouzigorji)

## Features

- Natural language processing for event creation using Ollama and Persian language model
- Integration with Google Calendar
- Smart time and date extraction
- Persian language support
- User-specific calendar management
- Support for both local and Google Colab environments

## Prerequisites

### For Local Installation:
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google API credentials
- Ollama installed and running locally
- Persian language model (mshojaei77/gemma3persian) pulled in Ollama

### For Google Colab:
- Google Account
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google API credentials
- Access to Google Colab

## Setup

### Local Installation:

1. Install Ollama:
   - Download and install Ollama from [ollama.ai](https://ollama.ai)
   - Pull the Persian language model:
     ```bash
     ollama pull mshojaei77/gemma3persian
     ```

2. Clone the repository:
```bash
git clone https://github.com/norouzigorji/ai_calendar_bot.git
cd ai_calendar_bot
```

3. Create and activate virtual environment:

   **Linux/MacOS:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   ```

   **Windows (Command Prompt):**
   ```cmd
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   venv\Scripts\activate
   ```

   **Windows (PowerShell):**
   ```powershell
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

6. Set up Google Calendar API:
- Go to the [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project
- Enable the Google Calendar API
- Create OAuth 2.0 credentials
- Download the credentials and save as `credentials.json` in the project root

### Google Colab Setup:

1. Open the [Google Colab Notebook](https://colab.research.google.com/)

2. Upload the notebook file (`ai_calendar_bot_colab.ipynb`) to your Google Drive

3. Open the notebook in Google Colab

4. Follow the instructions in the notebook to:
   - Install dependencies
   - Set up your Telegram bot token
   - Upload your Google Calendar credentials
   - Run the bot

## Usage

### Local Usage:

1. Make sure your virtual environment is activated

2. Start the bot:
```bash
python main.py
```

3. Open Telegram and start a conversation with your bot

4. Send messages in natural language to create events. Examples:
- "برای فردا ساعت ۱۱ یک جلسه با تیم برنامه‌نویسی تنظیم کن"
- "یادآوری کن که فردا ساعت ۳ بعدازظهر با دکتر ملاقات دارم"
- "برای شنبه هفته بعد ساعت ۱۰ صبح یک جلسه کاری تنظیم کن"

### Google Colab Usage:

1. Open the notebook in Google Colab

2. Run each cell in sequence

3. When prompted:
   - Enter your Telegram bot token
   - Upload your Google Calendar credentials file

4. The bot will start running in the Colab environment

## Project Structure

```
ai_calendar_bot/
│
├── main.py                 # Main bot implementation
├── calendar_utils.py       # Google Calendar integration
├── event_extractor.py      # AI-powered event extraction using Ollama
├── credentials.json        # Google API credentials
├── requirements.txt        # Python dependencies
├── ai_calendar_bot_colab.ipynb  # Google Colab notebook version
└── tokens/                 # User-specific OAuth tokens
```

## Security Notes

- Never share your `credentials.json` or `.env` files
- Keep your API keys secure
- The `tokens` directory contains sensitive user data and should be properly secured
- When using Google Colab, be careful with your credentials and tokens

## License

MIT License 