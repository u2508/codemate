# AI-Driven Terminal Scaffold

A production-minded scaffold for an AI-driven terminal with Natural Language -> command translation, command history, tab-autocomplete, and a web UI using FastAPI (backend) + WebSockets + React frontend (xterm.js).

## Features

- **Secure Command Execution**: Whitelisted safe commands only (ls, pwd, mkdir, touch, cat)
- **Natural Language Processing**: Convert natural language to structured commands
- **WebSocket Terminal**: Real-time interactive terminal sessions
- **Session Sandboxing**: Each session runs in isolated directory
- **Audit Logging**: All commands logged with timestamps
- **React Frontend**: Modern UI with xterm.js terminal integration

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install fastapi uvicorn python-dotenv psutil
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
python -m http.server 3000
# Open browser to http://localhost:3000
```

## Security Features

- **Command Whitelist**: Only safe commands are allowed
- **Path Sandboxing**: All operations confined to session directory
- **Audit Logging**: All executed commands are logged
- **Dry-run Support**: Preview commands before execution
- **Session Isolation**: Each WebSocket session gets isolated workspace

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app with WebSocket endpoint
│   ├── command_executor.py  # Safe command implementations
│   └── llm_adapter.py       # NLP to command translation
├── frontend/
│   ├── index.html          # HTML entry point
│   ├── App.jsx             # React terminal component
│   └── styles.css          # Basic styling
└── README_RUN.md           # Detailed setup instructions
```

## Next Steps

1. **LLM Integration**: Wire to OpenAI, Anthropic, or local models
2. **Authentication**: Add user authentication and session management
3. **Production Build**: Convert to full React + Vite app
4. **Testing**: Add unit tests with pytest
5. **Docker**: Add containerization for easy deployment

## Production Considerations

- Use HTTPS in production
- Implement proper authentication
- Set SESSION_ROOT environment variable
- Use proper React build instead of CDN
- Add rate limiting and monitoring

---

**Ready to extend!** The scaffold provides a secure foundation that can be easily extended with additional features.
