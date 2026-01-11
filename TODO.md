# AI-Driven Terminal Scaffold - Implementation Plan

## Overview
Create a production-minded scaffold for an AI-driven terminal with FastAPI backend and React frontend using xterm.js.

## Files to Create

### Backend Files
- [ ] backend/main.py - FastAPI app with WebSocket terminal sessions
- [ ] backend/command_executor.py - Core command implementations with security
- [ ] backend/llm_adapter.py - Pluggable LLM adapter interface

### Frontend Files
- [ ] frontend/index.html - HTML entry point with CDN dependencies
- [ ] frontend/App.jsx - React app with xterm.js terminal
- [ ] frontend/styles.css - Basic styling

### Documentation
- [ ] README_RUN.md - Run instructions and production notes

## Implementation Steps

1. Create backend directory structure
2. Implement command_executor.py with safe command registry
3. Implement llm_adapter.py with rule-based fallback
4. Implement main.py with FastAPI WebSocket endpoint
5. Create frontend directory structure
6. Implement index.html with React and xterm.js CDNs
7. Implement App.jsx with terminal integration
8. Implement styles.css for basic styling
9. Create README_RUN.md with setup instructions
10. Test the scaffold structure

## Security Features to Implement
- Command whitelist (ls, cd, pwd, mkdir, rm with confirmation, touch, cat, mv, cp)
- Session-based sandboxing with SESSION_ROOT
- NLP safety with JSON command spec validation
- Audit logging for all executed commands
- Dry-run validation
