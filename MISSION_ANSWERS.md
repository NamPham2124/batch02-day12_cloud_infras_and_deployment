# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns

1. API key và database credential bị hardcode.
2. Secret bị ghi ra log.
3. App bind vào `localhost`, container bên ngoài không truy cập được.
4. Port cố định thay vì đọc biến `PORT`.
5. Bật debug reload trong production.
6. Không có health/readiness endpoint.
7. Dùng `print()` thay vì structured logging.
8. Không quản lý startup và graceful shutdown.

### Exercise 1.3: So sánh

| Feature | Develop | Production | Tại sao quan trọng |
|---|---|---|---|
| Config | Hardcode | Environment variables | Một image chạy được ở nhiều môi trường |
| Health | Không có | `/health`, `/ready` | Platform biết restart hoặc ngừng route |
| Logging | `print()` | JSON event log | Log aggregator parse được |
| Shutdown | Đột ngột | Uvicorn graceful shutdown | Hoàn thành request đang chạy |
| Network | `localhost` | `0.0.0.0` | Nhận traffic ngoài container |

## Part 2: Docker

1. Basic base image: `python:3.11`.
2. Working directory: `/app`.
3. Copy `requirements.txt` trước để tận dụng Docker layer cache.
4. `CMD` cung cấp command mặc định và dễ override; `ENTRYPOINT` định nghĩa executable chính.
5. Final image dùng multi-stage, slim runtime và non-root user.
6. Image production cuối lab: khoảng **253 MB**, dưới yêu cầu 500 MB.

Stack cuối:

```text
Nginx -> 3 Agent replicas -> Redis
```

## Part 3: Cloud Deployment

- Railway được chọn vì hỗ trợ Docker service, Redis và public domain nhanh.
- `railway.toml` mô tả start command, health check và restart policy.
- Secret được đặt bằng Railway variables, không commit vào Git.
- Render dùng Blueprint YAML; Cloud Run example minh họa build/push/deploy pipeline.

## Part 4: API Security

- API key được đọc từ `X-API-Key` và so sánh constant-time.
- `X-User-ID` mô phỏng caller identity; production thực tế nên dùng JWT subject.
- Rate limiter dùng Redis sorted set và Lua script atomic.
- Limit mặc định là 10 request/phút/user; request tiếp theo trả `429`.
- Cost guard dùng Redis và Lua script atomic, budget mặc định `$10/tháng/user`.
- API trả `402` nếu request mới làm vượt budget.

## Part 5: Scaling & Reliability

- `/health` kiểm tra process sống.
- `/ready` kiểm tra app đã startup và Redis còn kết nối.
- Uvicorn xử lý SIGTERM, chờ in-flight requests rồi chạy lifespan cleanup.
- Conversation, rate limit và cost đều nằm trong Redis.
- Nginx phân phối request tới 3 instance.
- Kết quả local: cả 3 instance đã phục vụ request, session vẫn nhất quán.

## Part 6: Final Project

Implementation nằm trong `06-lab-complete/`.

Kết quả kiểm thử local:

```text
3 agent replicas healthy
Redis healthy
Nginx exposed at localhost:8000
4/4 black-box tests passed
Cost guard returned HTTP 402 at the configured budget
Session continued after one serving instance was stopped
Docker image size: 253 MB
```

Các test xác minh health/readiness, auth, Redis conversation history và shared
rate limit qua nhiều instance.
