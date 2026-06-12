<<<<<<< HEAD
# Lab 12 - Production AI Agent

AI Agent hoàn chỉnh dùng FastAPI, Redis, Docker và Nginx. Mock LLM được dùng để
lab chạy mà không cần API key của nhà cung cấp LLM.

## Kiến Trúc

```text
Client -> Nginx load balancer -> Agent replicas -> Redis
```

Redis lưu conversation history, sliding-window rate limit và monthly cost.
Vì không có state quan trọng trong memory của agent, stack có thể scale ngang.

## Chạy Local

```powershell
Copy-Item .env.example .env.local
# Đặt AGENT_API_KEY trong .env.local
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d --build --scale agent=3
.\.venv\Scripts\python.exe -m pytest tests -v
```

Service được expose tại `http://localhost:8000`.

```powershell
$headers = @{
  "X-API-Key" = "<key-trong-.env.local>"
  "X-User-ID" = "student-01"
}
$body = '{"question":"What is Docker?"}'
Invoke-RestMethod http://localhost:8000/ask -Method Post -Headers $headers `
  -ContentType application/json -Body $body
```

## API

| Method | Path | Auth | Mục đích |
|---|---|---|---|
| GET | `/health` | Không | Liveness probe |
| GET | `/ready` | Không | Readiness và Redis probe |
| POST | `/ask` | API key | Hỏi agent và tiếp tục session |
| GET | `/sessions/{id}` | API key | Xem conversation history |
| DELETE | `/sessions/{id}` | API key | Xóa conversation |
| GET | `/usage` | API key | Xem monthly cost |

Header `X-User-ID` mô phỏng danh tính người dùng trong shared API-key setup.
Hệ thống thực tế nên lấy user ID từ JWT hoặc identity provider.

## Production Controls

- Config và secrets từ environment variables.
- API key auth và constant-time comparison.
- Atomic Redis sliding-window rate limit.
- Atomic Redis monthly cost guard.
- Redis-backed conversation history với TTL.
- Multi-stage Docker image, non-root runtime, health check.
- Liveness, readiness, graceful shutdown và JSON event logs.
- Nginx load balancing cho local multi-instance test.

## Deploy Render Free

Blueprint chính nằm tại `../render.yaml`. Sau khi push repository lên GitHub:

1. Render Dashboard -> New -> Blueprint.
2. Kết nối repository và chọn root-level `render.yaml`.
3. Xác nhận web service và Key Value đều dùng plan `free`.
4. Apply Blueprint và chờ deploy thành công.

Sau deploy, lấy URL cùng `AGENT_API_KEY` trong Render Dashboard và chạy:

```powershell
$env:BASE_URL = "https://<domain>"
$env:AGENT_API_KEY = "<production-key>"
.\.venv\Scripts\python.exe -m pytest tests -v
```
=======
# Lab 12 — Complete Production Agent

Kết hợp TẤT CẢ những gì đã học trong 1 project hoàn chỉnh.

## Checklist Deliverable

- [x] Dockerfile (multi-stage, < 500 MB)
- [x] docker-compose.yml (agent + redis)
- [x] .dockerignore
- [x] Health check endpoint (`GET /health`)
- [x] Readiness endpoint (`GET /ready`)
- [x] API Key authentication
- [x] Rate limiting
- [x] Cost guard
- [x] Config từ environment variables
- [x] Structured logging
- [x] Graceful shutdown
- [x] Public URL ready (Railway / Render config)

---

## Cấu Trúc

```
06-lab-complete/
├── app/
│   ├── main.py         # Entry point — kết hợp tất cả
│   ├── config.py       # 12-factor config
│   ├── auth.py         # API Key + JWT
│   ├── rate_limiter.py # Rate limiting
│   └── cost_guard.py   # Budget protection
├── Dockerfile          # Multi-stage, production-ready
├── docker-compose.yml  # Full stack
├── railway.toml        # Deploy Railway
├── render.yaml         # Deploy Render
├── .env.example        # Template
├── .dockerignore
└── requirements.txt
```

---

## Chạy Local

```bash
# 1. Setup
cp .env.example .env

# 2. Chạy với Docker Compose
docker compose up

# 3. Test
curl http://localhost/health

# 4. Lấy API key từ .env, test endpoint
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" \
     -X POST http://localhost/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is deployment?"}'
```

---

## Deploy Railway (< 5 phút)

```bash
# Cài Railway CLI
npm i -g @railway/cli

# Login và deploy
railway login
railway init
railway variables set OPENAI_API_KEY=sk-...
railway variables set AGENT_API_KEY=your-secret-key
railway up

# Nhận public URL!
railway domain
```

---

## Deploy Render

1. Push repo lên GitHub
2. Render Dashboard → New → Blueprint
3. Connect repo → Render đọc `render.yaml`
4. Set secrets: `OPENAI_API_KEY`, `AGENT_API_KEY`
5. Deploy → Nhận URL!

---

## Kiểm Tra Production Readiness

```bash
python check_production_ready.py
```

Script này kiểm tra tất cả items trong checklist và báo cáo những gì còn thiếu.
>>>>>>> 1bc3e8ea401ec09838476ee6810d4087387fcd6d
