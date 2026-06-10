import subprocess
import sys
import urllib.request
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse, RedirectResponse

router = APIRouter(tags=["Frontend"])

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
frontend_process: subprocess.Popen[bytes] | None = None

def find_frontend_build() -> Path | None:
    candidates = [FRONTEND_DIR / 'dist', FRONTEND_DIR / 'build', FRONTEND_DIR / 'output']
    for d in candidates:
        if d.exists() and d.is_dir():
            return d
    return None

def is_dev_server_up() -> bool:
    try:
        req = urllib.request.Request('http://127.0.0.1:5173', headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1) as resp:
            return resp.status < 400
    except Exception:
        return False

def start_frontend() -> subprocess.Popen[bytes] | None:
    npm_command = ["npm.cmd" if sys.platform == "win32" else "npm", "run", "dev", "--", "--host", "127.0.0.1"]
    print(f"Запуск фронтенда из {FRONTEND_DIR}")
    return subprocess.Popen(npm_command, cwd=FRONTEND_DIR)

def stop_frontend() -> None:
    global frontend_process
    if frontend_process is None:
        return
    if frontend_process.poll() is None:
        print("Остановка фронтенда...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()

@router.get("/__frontend_ready")
def frontend_ready():
    if find_frontend_build():
        return PlainTextResponse("ready", status_code=200)
    if is_dev_server_up():
        return PlainTextResponse("ready", status_code=200)
    return PlainTextResponse("not-ready", status_code=503)

@router.get("/")
def serve_frontend_index():
    build_dir = find_frontend_build()
    if build_dir:
        index = build_dir / 'index.html'
        if index.exists():
            return FileResponse(index, media_type='text/html')
            
    if is_dev_server_up():
        return RedirectResponse('http://127.0.0.1:5173')
        
    html = """
        <!doctype html>
        <html lang="ru">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Загрузка…</title>
                <style>
                    :root{--bg:#0b1220;--card:#0f1724;--muted:#94a3b8;--accent:#60a5fa}
                    html,body{height:100%;margin:0}
                    body{background:radial-gradient(1200px 600px at 10% 20%, rgba(96,165,250,0.06), transparent), var(--bg);color:var(--muted);font-family:Inter,ui-sans-serif,system-ui,Segoe UI,Helvetica,Arial,sans-serif;display:flex;align-items:center;justify-content:center}
                    .box{background:linear-gradient(180deg, rgba(255,255,255,0.02), transparent);padding:28px;border-radius:12px;box-shadow:0 6px 24px rgba(2,6,23,0.6);text-align:center;min-width:320px}
                    h1{color:#e6eef8;margin:0 0 8px 0;font-size:20px}
                    p{margin:0 0 14px 0;color:var(--muted)}
                    .spinner{width:72px;height:72px;border-radius:50%;border:8px solid rgba(255,255,255,0.06);border-top-color:var(--accent);animation:spin 1s linear infinite;margin:0 auto 16px}
                    .dots{display:flex;gap:8px;justify-content:center}
                    .dot{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,0.08);animation:pulse 1.2s infinite}
                    .dot:nth-child(1){animation-delay:0s}
                    .dot:nth-child(2){animation-delay:0.15s}
                    .dot:nth-child(3){animation-delay:0.3s}
                    @keyframes spin{to{transform:rotate(360deg)}}
                    @keyframes pulse{0%{transform:translateY(0);opacity:0.6}50%{transform:translateY(-6px);opacity:1}100%{transform:translateY(0);opacity:0.6}}
                    small{display:block;margin-top:8px;color:#7e8aa3;font-size:12px}
                </style>
            </head>
            <body>
                <div class="box">
                    <div class="spinner" aria-hidden></div>
                    <h1>Загрузка фронтенда…</h1>
                    <p>Страницу можно открыть через порт <strong>5173</strong> при запущенном dev‑сервере.</p>
                    <div class="dots" aria-hidden>
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                    <small>Авто‑обновление выполняется каждые 1.5 секунды.</small>
                </div>
                <script>
                    async function check(){
                        try{
                            const r = await fetch('/__frontend_ready');
                            if(r.ok){ location.reload(); return; }
                        }catch(e){}
                        setTimeout(check,1500);
                    }
                    check();
                </script>
            </body>
        </html>
    """
    return HTMLResponse(html)