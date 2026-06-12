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
docker compose up -d --build --scale agent=3
python -m pytest tests -v
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
python -m pytest tests -v
```
