# Run instructions

1. Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-dotenv psutil
# start
uvicorn backend.main:app --reload --port 8000
```

2. Frontend (quick dev)

```bash
cd frontend
python -m http.server 3000
# open http://localhost:3000
```

# Production notes

* Use HTTPS and auth
* Use a proper React build and serve via CDN or Node server
* Secure session root and set SESSION_ROOT environment variable
