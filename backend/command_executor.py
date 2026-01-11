# backend/command_executor.py
# Enhanced command executor with sandboxing, structured logging,
# resource monitoring, and safer operations.

import os
import shutil
import shlex
import json
from pathlib import Path
from datetime import datetime
import psutil

SESSION_ROOT = Path(os.environ.get('SESSION_ROOT', str(Path.cwd() / 'sessions'))).resolve()
SESSION_ROOT.mkdir(parents=True, exist_ok=True)

class CommandError(Exception):
    pass


# ---------- Utility helpers ----------

def _resolve_path(session_id: str, path_str: str) -> Path:
    """Resolve a path safely within the session sandbox."""
    base = (SESSION_ROOT / session_id).resolve()
    base.mkdir(parents=True, exist_ok=True)
    p = (base / Path(path_str)).expanduser().resolve()
    if not str(p).startswith(str(base)):
        raise CommandError("path escapes session root")
    return p

def _log(session_id: str, entry: dict):
    """Structured JSON audit logging per session."""
    entry["ts"] = datetime.utcnow().isoformat()
    entry["session"] = session_id
    log_path = SESSION_ROOT / session_id / "audit.log"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------- Whitelisted command implementations ----------

def cmd_ls(session_id, args, cwd):
    p = _resolve_path(session_id, args[0] if args else cwd)
    if p.is_file():
        return p.name
    out = []
    for x in sorted(p.iterdir()):
        mode = "d" if x.is_dir() else "-"
        out.append(f"{mode}\t{x.name}")
    return "\n".join(out)

def cmd_pwd(session_id, args, cwd):
    return cwd

def cmd_cd(session_id, args, cwd):
    if not args:
        return cwd
    p = _resolve_path(session_id, args[0])
    if not p.is_dir():
        raise CommandError(f"{args[0]}: not a directory")
    return str(p.relative_to(SESSION_ROOT / session_id))

def cmd_mkdir(session_id, args, cwd):
    if not args:
        raise CommandError("mkdir: missing operand")
    out = []
    for d in args:
        p = _resolve_path(session_id, d)
        p.mkdir(parents=True, exist_ok=True)
        out.append(str(p))
    return "\n".join(out)

def cmd_touch(session_id, args, cwd):
    if not args:
        raise CommandError("touch: missing operand")
    for f in args:
        p = _resolve_path(session_id, f)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch(exist_ok=True)
    return "ok"

def cmd_cat(session_id, args, cwd):
    if not args:
        raise CommandError("cat: missing operand")
    out = []
    for f in args:
        p = _resolve_path(session_id, f)
        if not p.exists():
            raise CommandError(f"{f}: no such file")
        out.append(p.read_text(encoding="utf-8"))
    return "\n".join(out)

def cmd_rm(session_id, args, cwd):
    if not args:
        raise CommandError("rm: missing operand")
    if len(args) > 1:
        return {"confirm": True, "message": f"rm: remove {len(args)} items?"}
    for f in args:
        p = _resolve_path(session_id, f)
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    return "ok"

def cmd_mv(session_id, args, cwd):
    if len(args) != 2:
        raise CommandError("mv: requires source and destination")
    src = _resolve_path(session_id, args[0])
    dst = _resolve_path(session_id, args[1])
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return "ok"

def cmd_cp(session_id, args, cwd):
    if len(args) != 2:
        raise CommandError("cp: requires source and destination")
    src = _resolve_path(session_id, args[0])
    dst = _resolve_path(session_id, args[1])
    if src.is_dir():
        shutil.copytree(str(src), str(dst))
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
    return "ok"

def cmd_echo(session_id, args, cwd):
    return " ".join(args)

def cmd_clear(session_id, args, cwd):
    return "\x1b[2J\x1b[H"  # ANSI clear screen

def cmd_whoami(session_id, args, cwd):
    return f"user_{session_id[:8]}"

def cmd_date(session_id, args, cwd):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cmd_ps(session_id, args, cwd):
    """Show top processes (pid, name, cpu%, mem%)."""
    procs = []
    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
        info = p.info
        procs.append(f"{info['pid']}\t{info['name']}\tCPU:{info['cpu_percent']}%\tMEM:{info['memory_percent']:.1f}%")
    return "\n".join(procs[:15])

def cmd_top(session_id, args, cwd):
    """System summary: CPU, Memory, Disk."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return (f"CPU: {cpu}%\n"
            f"Memory: {mem.percent}% ({mem.used//(1024**2)}MB/{mem.total//(1024**2)}MB)\n"
            f"Disk: {disk.percent}% ({disk.used//(1024**3)}GB/{disk.total//(1024**3)}GB)")

# ---------- Command map & aliases ----------

COMMAND_MAP = {
    "ls": cmd_ls,
    "pwd": cmd_pwd,
    "cd": cmd_cd,
    "mkdir": cmd_mkdir,
    "touch": cmd_touch,
    "cat": cmd_cat,
    "rm": cmd_rm,
    "mv": cmd_mv,
    "cp": cmd_cp,
    "echo": cmd_echo,
    "clear": cmd_clear,
    "whoami": cmd_whoami,
    "date": cmd_date,
    "ps": cmd_ps,
    "top": cmd_top,
}

ALIASES = {
    "ll": ["ls"],
    "..": ["cd", ".."],
}

# ---------- Executor entrypoint ----------

def execute_command(session_id: str, cmd_name: str, args: list, cwd: str, dry_run: bool = False):
    # Alias expansion
    if cmd_name in ALIASES:
        expanded = ALIASES[cmd_name]
        cmd_name, args = expanded[0], expanded[1:] + args

    if cmd_name not in COMMAND_MAP:
        return {"ok": False, "error": "command not allowed"}

    if dry_run:
        return {"ok": True, "command": cmd_name, "args": args}

    try:
        func = COMMAND_MAP[cmd_name]
        result = func(session_id, args, cwd)
        _log(session_id, {"cmd": cmd_name, "args": args})
        return {"ok": True, "output": result}
    except CommandError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": f"internal error: {e}"}
