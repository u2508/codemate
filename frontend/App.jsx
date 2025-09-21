// frontend/App.jsx
import React, { useEffect, useRef, useState } from 'react'
import { Terminal } from 'xterm'
import 'xterm/css/xterm.css'
import './src/styles.css'

export default function App(){
  const termRef = useRef(null)
  const wsRef = useRef(null)
  const [session, setSession] = useState(null)
  const [nl, setNl] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [commandHistory, setCommandHistory] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(()=>{
    const term = new Terminal({
      rows: 24,
      cols: 100,
      cursorBlink: true,
      theme: {
        background: '#1e1e1e',
        foreground: '#ffffff',
        cursor: '#ffffff',
        cursorAccent: '#000000',
        selection: '#3e4451'
      }
    })
    term.open(document.getElementById('terminal'))
    term.writeln('\x1b[1;32mAI Terminal v1.0 — Secure AI-Powered Terminal\x1b[0m')
    term.writeln('Type natural language commands or use traditional commands...')
    term.writeln('Example: "create a folder called test" or "ls"')
    term.writeln('')
    termRef.current = term

    const ws = new WebSocket('ws://127.0.0.1:8000/ws/term')
    ws.onopen = ()=>{
      setIsConnected(true)
      term.writeln('\x1b[1;32m✓ Connected to terminal session\x1b[0m')
    }
    ws.onclose = ()=>{
      setIsConnected(false)
      term.writeln('\x1b[1;31m✗ Disconnected from terminal session\x1b[0m')
    }
    ws.onerror = (error)=>{
      term.writeln('\x1b[1;31m✗ Connection error: ' + error + '\x1b[0m')
    }
    ws.onmessage = (ev)=>{
      const data = JSON.parse(ev.data)
      if(data.type === 'session') {
        setSession(data.session_id)
        term.writeln(`\x1b[1;36mSession ID: ${data.session_id}\x1b[0m`)
      }
      if(data.type === 'output') {
        term.writeln(String(data.output))
        setIsLoading(false)
      }
      if(data.type === 'nl_spec') {
        term.writeln('\x1b[1;33mNL → ' + JSON.stringify(data.spec) + '\x1b[0m')
      }
      if(data.type === 'require_confirm') {
        term.writeln('\x1b[1;31m⚠️  Confirmation required for: ' + data.spec.command + '\x1b[0m')
        term.writeln('Type "yes" to confirm or "no" to cancel')
      }
    }
    wsRef.current = ws
    return ()=> ws.close()
  },[])

  function sendExec(cmd, args = []){
    if (!wsRef.current || !isConnected) {
      termRef.current?.writeln('\x1b[1;31m✗ Not connected\x1b[0m')
      return
    }
    setIsLoading(true)
    wsRef.current.send(JSON.stringify({type:'exec', command: cmd, args: args}))
    setCommandHistory(prev => [...prev, {type: 'command', command: cmd, args: args, timestamp: new Date()}])
  }

  function sendNL(){
    if (!nl.trim()) return
    if (!wsRef.current || !isConnected) {
      termRef.current?.writeln('\x1b[1;31m✗ Not connected\x1b[0m')
      return
    }
    setIsLoading(true)
    termRef.current?.writeln(`\x1b[1;35m> ${nl}\x1b[0m`)
    wsRef.current.send(JSON.stringify({type:'nl', text: nl}))
    setCommandHistory(prev => [...prev, {type: 'nl', text: nl, timestamp: new Date()}])
    setNl('')
  }

  function handleKeyPress(e){
    if (e.key === 'Enter') {
      sendNL()
    }
  }

  function clearTerminal(){
    termRef.current?.clear()
    termRef.current?.writeln('\x1b[1;32mAI Terminal — Session cleared\x1b[0m')
  }

  function showHelp(){
    termRef.current?.writeln('\x1b[1;36m=== AI Terminal Help ===\x1b[0m')
    termRef.current?.writeln('Natural Language Commands:')
    termRef.current?.writeln('  • "create a folder called myfolder"')
    termRef.current?.writeln('  • "list files" or "show directory contents"')
    termRef.current?.writeln('  • "make a file named test.txt"')
    termRef.current?.writeln('  • "read the contents of file.txt"')
    termRef.current?.writeln('')
    termRef.current?.writeln('Traditional Commands:')
    termRef.current?.writeln('  • ls, pwd, mkdir, touch, cat')
    termRef.current?.writeln('')
    termRef.current?.writeln('Controls:')
    termRef.current?.writeln('  • Enter: Execute natural language command')
    termRef.current?.writeln('  • Clear button: Clear terminal output')
    termRef.current?.writeln('  • Help button: Show this help')
    termRef.current?.writeln('\x1b[1;36m======================\x1b[0m')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 AI Terminal</h1>
          <div className="status-indicators">
            <span className={`status ${isConnected ? 'connected' : 'disconnected'}`}>
              {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
            {session && <span className="session-id">Session: {session.substring(0, 8)}...</span>}
          </div>
        </div>
        <div className="header-actions">
          <button onClick={showHelp} className="btn-secondary">Help</button>
          <button onClick={clearTerminal} className="btn-secondary">Clear</button>
        </div>
      </header>

      <div className="terminal-container">
        <div id='terminal' />
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner">⟳</div>
          </div>
        )}
      </div>

      <div className="controls">
        <div className="input-group">
          <input
            value={nl}
            onChange={e=>setNl(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder='Type natural language instruction (e.g., "create a folder called test")'
            className="nl-input"
            disabled={!isConnected}
          />
          <button
            onClick={sendNL}
            disabled={!isConnected || !nl.trim() || isLoading}
            className="btn-primary"
          >
            {isLoading ? '⟳' : '🚀 Run'}
          </button>
        </div>

        <div className="quick-commands">
          <span className="quick-label">Quick Commands:</span>
          <button onClick={() => sendExec('ls')} disabled={!isConnected} className="btn-quick">ls</button>
          <button onClick={() => sendExec('pwd')} disabled={!isConnected} className="btn-quick">pwd</button>
          <button onClick={() => sendExec('mkdir', ['demo'])} disabled={!isConnected} className="btn-quick">mkdir demo</button>
          <button onClick={() => sendExec('touch', ['hello.txt'])} disabled={!isConnected} className="btn-quick">touch hello.txt</button>
        </div>
      </div>

      {commandHistory.length > 0 && (
        <div className="history-panel">
          <h3>Command History</h3>
          <div className="history-list">
            {commandHistory.slice(-5).map((item, index) => (
              <div key={index} className="history-item">
                <span className="history-type">
                  {item.type === 'nl' ? '💬' : '⚡'}
                </span>
                <span className="history-content">
                  {item.type === 'nl' ? item.text : `${item.command} ${item.args.join(' ')}`}
                </span>
                <span className="history-time">
                  {item.timestamp.toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
