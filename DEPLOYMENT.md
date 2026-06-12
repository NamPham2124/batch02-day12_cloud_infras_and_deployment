# Deployment Information

## Platform

Render Free Blueprint

## Public URL

Sẽ được cập nhật sau khi kết nối GitHub repository với Render Blueprint.

## Environment Variables

- `AGENT_API_KEY`
- `ENVIRONMENT=production`
- `REDIS_URL`
- `RATE_LIMIT_PER_MINUTE=10`
- `MONTHLY_BUDGET_USD=10`

## Validation

```powershell
$env:BASE_URL = "https://day12-production-agent.onrender.com"
$env:AGENT_API_KEY = "<production-key>"
python -m pytest 06-lab-complete/tests -v
```

Secret không được ghi vào tài liệu hoặc commit vào repository.

## Create Blueprint

1. Push repository lên GitHub.
2. Mở Render Dashboard, chọn **New > Blueprint**.
3. Kết nối repository và dùng file `render.yaml` ở repository root.
4. Nhập một secret ngẫu nhiên cho `AGENT_API_KEY` khi Render yêu cầu.
5. Kiểm tra cả web service và Key Value instance đều dùng plan `free`.
6. Chọn **Apply** và đợi deploy thành công.
7. Mở web service để lấy public URL.

Blueprint tự động tạo:

```text
day12-production-agent  -> Free Docker web service
day12-agent-cache       -> Free Render Key Value
REDIS_URL               -> Private connection string
```
