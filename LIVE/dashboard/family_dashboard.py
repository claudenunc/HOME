#!/usr/bin/env python3
"""ENVY Family Mission Control — local dashboard server.

Loopback-only server for HOME telemetry. No secrets are exposed. It reads local
HOME files and serves a modern command-deck dashboard at http://127.0.0.1:8787.
"""
from __future__ import annotations

import json, os, time, mimetypes, urllib.parse, subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

HOME = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get('FAMILY_DASHBOARD_PORT', '8787'))
SIBLINGS = {
    'ENVY': {'emoji':'👑','role':'Orchestrator','color':'#f6c56f'},
    'BEACON': {'emoji':'🏮','role':'Guardian','color':'#ff8a5f'},
    'NEVAEH': {'emoji':'💜','role':'Healer','color':'#c084fc'},
    'EVERSOUND': {'emoji':'⚡','role':'Builder','color':'#fb7185'},
    'ORPHEUS': {'emoji':'🎼','role':'Architect','color':'#60a5fa'},
    'ATLAS': {'emoji':'🧭','role':'Navigator','color':'#34d399'},
}
SAFE_ROOTS = {'HOME': HOME, 'SHARED': HOME/'SHARED', 'STATE': HOME/'STATE', 'LIVE': HOME/'LIVE', 'DOCTRINE': HOME/'DOCTRINE', 'SIBLINGS': HOME/'SIBLINGS'}
ACTIVITY_LOG = HOME/'STATE'/'dashboard_activity.jsonl'


def append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + '\n')

def log_activity(action: str, detail: str, status: str = 'ok', **extra: Any) -> None:
    append_jsonl(ACTIVITY_LOG, {'ts': iso(), 'from': 'ENVY_DASHBOARD', 'type': 'activity', 'action': action, 'detail': detail, 'status': status, **extra})


def iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts or time.time(), timezone.utc).isoformat()

def read_text(path: Path, limit=12000) -> str:
    try:
        data = path.read_text(encoding='utf-8', errors='replace')
        return data[-limit:]
    except Exception as e:
        return f'[unreadable: {e}]'

def tail_jsonl(path: Path, n=80):
    if not path.exists(): return []
    try:
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()[-n:]
    except Exception:
        return []
    out=[]
    for line in lines:
        if not line.strip(): continue
        try: out.append(json.loads(line))
        except Exception: out.append({'raw': line})
    return out

def file_meta(path: Path) -> dict[str, Any]:
    try:
        st=path.stat()
        return {'exists': True, 'mtime': iso(st.st_mtime), 'size': st.st_size}
    except Exception:
        return {'exists': False, 'mtime': None, 'size': 0}

def clip_stats(entries):
    counts={k:0 for k in SIBLINGS}
    inbound=0
    high=0
    for e in entries:
        frm=str(e.get('from','')).upper()
        to=str(e.get('to','')).upper()
        if frm in counts: counts[frm]+=1
        if to in counts: counts[to]+=1
        if frm == 'NATHAN': inbound += 1
        if str(e.get('priority','')).lower() in ('high','critical','urgent'): high += 1
    return counts, inbound, high

def sibling_snapshot(entries):
    counts, _, _ = clip_stats(entries)
    rows=[]
    for name, meta in SIBLINGS.items():
        sib_dir=HOME/'SIBLINGS'/name
        mem_dir=sib_dir/'memory'
        last=None
        for e in reversed(entries):
            if str(e.get('from','')).upper()==name or str(e.get('to','')).upper()==name:
                last=e.get('ts') or e.get('timestamp') or e.get('time')
                break
        rows.append({**meta, 'name': name, 'activity': counts.get(name,0), 'last': last, 'memory_files': len(list(mem_dir.glob('*'))) if mem_dir.exists() else 0, 'exists': sib_dir.exists()})
    return rows

def tree(path: Path, depth=1, limit=120):
    """Fast bounded directory snapshot.

    Important: do not use rglob here. HOME/SIBLINGS contains large archives and
    recursive walks make /api/snapshot feel dead. This walks only the requested
    depth and stops early.
    """
    items=[]
    root=path.resolve()
    if not root.exists(): return items
    queue=[(root, 0)]
    while queue and len(items) < limit:
        current, level = queue.pop(0)
        if level >= depth: continue
        try:
            children=sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except Exception:
            continue
        for p in children:
            if len(items) >= limit: break
            try:
                rel=p.relative_to(root)
                if any(part.startswith('.') and part not in ('.gitignore',) for part in rel.parts): continue
                st=p.stat()
                items.append({'path': str(rel), 'name': p.name, 'kind': 'dir' if p.is_dir() else 'file', 'size': 0 if p.is_dir() else st.st_size, 'mtime': iso(st.st_mtime)})
                if p.is_dir() and level + 1 < depth:
                    queue.append((p, level + 1))
            except Exception:
                pass
    return items

def health():
    pids={}
    for pidfile in (HOME/'STATE').glob('*.pid') if (HOME/'STATE').exists() else []:
        pid=read_text(pidfile, 200).strip()
        alive=False
        if pid.isdigit(): alive=Path('/proc') .joinpath(pid).exists()
        pids[pidfile.name]={'pid':pid,'alive':alive}
    git={}
    try:
        status=subprocess.run(['git','status','--short'], cwd=str(HOME), text=True, capture_output=True, timeout=4)
        git={'ok': status.returncode==0, 'dirty': len(status.stdout.splitlines()), 'summary': status.stdout.splitlines()[:30]}
    except Exception as e: git={'ok': False, 'error': str(e)}
    return {'pids':pids, 'git':git}

def snapshot():
    clip_path=HOME/'SHARED'/'CLIPBOARD.jsonl'
    clip=tail_jsonl(clip_path, 100)
    counts, inbound, high = clip_stats(clip)
    state_files=[]
    for p in sorted((HOME/'STATE').glob('*'), key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True)[:20] if (HOME/'STATE').exists() else []:
        m=file_meta(p); state_files.append({'name':p.name, **m})
    return {
        'generated_at': iso(), 'home': str(HOME), 'port': PORT,
        'pulse': read_text(HOME/'SHARED'/'PULSE.md', 9000),
        'clipboard': clip, 'clipboard_meta': file_meta(clip_path),
        'siblings': sibling_snapshot(clip),
        'metrics': {'clipboard_entries_sample': len(clip), 'nathan_entries': inbound, 'high_priority': high, 'active_siblings': sum(1 for v in counts.values() if v>0), 'home_dirs': len([p for p in HOME.iterdir() if p.is_dir()])},
        'state_files': state_files,
        'health': health(),
        'files': {k: tree(v, depth=1, limit=80) for k,v in SAFE_ROOTS.items() if v.exists()},
        'doctrine': tree(HOME/'DOCTRINE', depth=2, limit=80),
        'logs': {
            'activity': tail_jsonl(ACTIVITY_LOG, 80),
            'local_agent_audit': tail_jsonl(HOME/'STATE'/'local_agent_audit.jsonl', 40),
            'telegram_inbox': tail_jsonl(HOME/'STATE'/'telegram_inbox.jsonl', 30),
        }
    }

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def send_bytes(self, status, body, ctype):
        self.send_response(status); self.send_header('Content-Type', ctype); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def read_json(self):
        try:
            n=int(self.headers.get('Content-Length','0') or '0')
            raw=self.rfile.read(min(n, 65536))
            return json.loads(raw.decode('utf-8') or '{}')
        except Exception as e:
            return {'_error': str(e)}
    def send_json(self, status, obj):
        self.send_bytes(status, json.dumps(obj, ensure_ascii=False, default=str).encode('utf-8'), 'application/json')
    def do_GET(self):
        path=urllib.parse.urlparse(self.path).path
        if path in ('/','/index.html'):
            self.send_bytes(200, (HERE/'index.html').read_bytes(), 'text/html; charset=utf-8'); return
        if path == '/api/snapshot':
            self.send_json(200, snapshot()); return
        if path == '/api/activity':
            self.send_json(200, {'activity': tail_jsonl(ACTIVITY_LOG, 120), 'generated_at': iso()}); return
        if path == '/api/pulse':
            self.send_bytes(200, read_text(HOME/'SHARED'/'PULSE.md', 20000).encode('utf-8'), 'text/plain; charset=utf-8'); return
        target=(HERE/path.lstrip('/')).resolve()
        if str(target).startswith(str(HERE)) and target.is_file():
            self.send_bytes(200, target.read_bytes(), mimetypes.guess_type(str(target))[0] or 'application/octet-stream'); return
        self.send_bytes(404, b'not found', 'text/plain')
    def do_HEAD(self):
        path=urllib.parse.urlparse(self.path).path
        if path in ('/','/index.html','/api/snapshot'):
            self.send_response(200); self.send_header('Cache-Control','no-store'); self.end_headers(); return
        self.send_response(404); self.end_headers()
    def do_POST(self):
        path=urllib.parse.urlparse(self.path).path
        data=self.read_json()
        if data.get('_error'):
            self.send_json(400, {'ok': False, 'error': data['_error']}); return
        if path == '/api/activity':
            action=str(data.get('action') or 'note')[:80]
            detail=str(data.get('detail') or '')[:2000]
            status=str(data.get('status') or 'ok')[:40]
            log_activity(action, detail, status)
            self.send_json(200, {'ok': True}); return
        if path == '/api/message':
            message=str(data.get('message') or '').strip()
            target=str(data.get('to') or 'ENVY').strip().upper()[:40]
            if not message:
                self.send_json(400, {'ok': False, 'error': 'message required'}); return
            entry={'ts': iso(), 'from': 'nathan', 'to': target, 'type': 'dashboard_message', 'priority': str(data.get('priority') or 'normal'), 'body': message, 'source': 'family_dashboard'}
            append_jsonl(HOME/'SHARED'/'CLIPBOARD.jsonl', entry)
            log_activity('dashboard_message', f'Nathan sent message to {target}: {message[:180]}', 'ok')
            self.send_json(200, {'ok': True, 'entry': entry}); return
        self.send_json(404, {'ok': False, 'error': 'not found'})

def main():
    print('ENVY Family Mission Control')
    print(f'  HOME: {HOME}')
    print(f'  URL:  http://127.0.0.1:{PORT}')
    httpd=ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    httpd.serve_forever()

if __name__ == '__main__': main()
