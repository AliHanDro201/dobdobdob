# Jarvis - Personal AI Assistant

## Description
Jarvis is a personal AI agent that can control your computer on your behalf. It executes commands, writes code, opens applications, clicks, enters text - in short, does everything a user does, but faster, more accurately, and without fatigue.

## Features
- Voice control: speech recognition using Whisper API from OpenAI
- Voice responses: using ElevenLabs and edge-tts for natural communication
- ChatGPT integration: ability to communicate with GPT through browser
- Computer control: opening applications, navigating websites
- Autonomous tasks: performing sequences of actions in autopilot mode
- Computer vision: ability to "see" the screen, recognize text and interact with UI elements

## Installation

### Requirements
- Python 3.8+
- Chrome/Chromium for browser integration
- Tesseract OCR for screen text recognition (optional)

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/AliHanDro201/solid-solid-solid-solid-meme.git
cd solid-solid-solid-solid-meme
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with API keys:
```
OPENAI_API_KEY=your_openai_key
SECOND_OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_weatherapi_key
```

4. Run the application:
```bash
python main.py
```

You can also run with additional parameters:
```bash
python main.py --host 0.0.0.0 --port 8000 --mode chrome --no-browser
```

Available parameters:
- `--host`: Host to bind the server (default: 127.0.0.1)
- `--port`: Port to bind the server (default: 8000)
- `--mode`: Browser mode (default: chrome)
- `--no-browser`: Don't open browser automatically
- `--test`: Run in test mode without API keys

## Usage
1. Launch the application
2. Turn on the microphone by clicking the toggle
3. Speak commands, for example:
   - "Open calculator"
   - "Find information about weather in Moscow"
   - "Ask GPT: tell me about quantum physics"

## Documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed description of the project architecture
- [COMMANDS.md](COMMANDS.md) - List of available commands
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Possible improvements for the project
- [TESTING.md](TESTING.md) - Information about tests and how to run them
- [INSTALL.md](INSTALL.md) - Detailed installation instructions
- [SCREEN_VISION.md](SCREEN_VISION.md) - Information about computer vision capabilities

## Testing
To run the tests, use the following command:
```bash
python -m unittest discover -s tests
```

For more information about testing, see [TESTING.md](TESTING.md).

## Architecture
- **core/**: core application logic
- **utils/**: utility functions
- **commands/**: commands for computer control
- **integrations/**: integrations with external services
- **ui/**: user interface
- **tests/**: unit tests

## License
MIT
