# backend/main.py
# FastAPI app with a WebSocket endpoint for interactive terminal sessions.

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import json

from command_executor import execute_command
from llm_adapter import interpret

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sessions = {}

@app.websocket('/ws/term')
async def websocket_terminal(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    cwd = '/'
    sessions[session_id] = {'cwd': cwd}
    try:
        await ws.send_json({'type': 'session', 'session_id': session_id})
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            # payload types: {type: 'exec', command: 'ls', args:[], dry_run:False}
            if payload.get('type') == 'nl':
                spec = interpret(payload.get('text',''))
                await ws.send_json({'type': 'nl_spec', 'spec': spec})
                if spec.get('command')=='unknown':
                    await ws.send_json({'type':'output','output':'Could not interpret NL instruction.'})
                    continue
                # if confirmation required
                if spec.get('confirm'):
                    await ws.send_json({'type':'require_confirm','spec':spec})
                    continue
                try:
                    res = execute_command(session_id, spec['command'], spec.get('args',[]), sessions[session_id]['cwd'], dry_run=False)
                    await ws.send_json({'type':'output','output':res.get('output','')})
                except Exception as e:
                    await ws.send_json({'type':'output','output':str(e)})
                continue

            if payload.get('type') == 'exec':
                cmd = payload.get('command')
                args = payload.get('args', [])
                dry = payload.get('dry_run', False)
                try:
                    res = execute_command(session_id, cmd, args, sessions[session_id]['cwd'], dry_run=dry)
                    await ws.send_json({'type':'output','output':res.get('output', str(res))})
                except Exception as e:
                    await ws.send_json({'type':'output','output':str(e)})

    except WebSocketDisconnect:
        sessions.pop(session_id, None)
