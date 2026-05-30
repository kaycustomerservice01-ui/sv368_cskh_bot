# SV368 CSKH Bot - Telegram

Bot hỗ trợ khách hàng SV368 với Admin panel bảo mật.

## Tính năng

✅ Chat 1-1 với khách hàng  
✅ Admin panel (mã lệnh bảo mật)  
✅ Cập nhật dữ liệu (khuyến mãi, quy tắc, liên hệ, cách đăng ký)  
✅ Database JSON lưu trữ dữ liệu  
✅ Deploy 24/7 trên Railway  

## Thông tin Bot

- **Tên:** SV368 CSKH Bot
- **Username:** @sv368cskh_bot
- **Token:** 8999982037:AAFkiBcOAHJ52fW0rwYLmW-1QQCi_wQ0pyg
- **Mã admin:** admin_KaY8386_SV368_CSKH_2024_UpdateData_SecureMode

## Cài đặt Địa phương

### 1. Clone repo
```bash
git clone <repo_url>
cd sv368_bot
```

### 2. Cài dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
export TELEGRAM_TOKEN="8999982037:AAFkiBcOAHJ52fW0rwYLmW-1QQCi_wQ0pyg"
export ADMIN_PASSWORD="admin_KaY8386_SV368_CSKH_2024_UpdateData_SecureMode"
export ADMIN_ID="YOUR_TELEGRAM_ID"
```

### 4. Chạy bot
```bash
python sv368_bot.py
```

## Deploy lên Railway

### 1. Tạo tài khoản Railway
- Vào https://railway.app
- Đăng ký (GitHub hoặc Email)

### 2. Tạo Project
- Nhấp "Create New Project"
- Chọn "Deploy from GitHub"
- Chọn repo này

### 3. Set Environment Variables
Trên Railway dashboard:
- Vào "Variables"
- Thêm:
  - `TELEGRAM_TOKEN`: 8999982037:AAFkiBcOAHJ52fW0rwYLmW-1QQCi_wQ0pyg
  - `ADMIN_PASSWORD`: admin_KaY8386_SV368_CSKH_2024_UpdateData_SecureMode
  - `ADMIN_ID`: (ID Telegram của bạn)

### 4. Deploy
- Railway sẽ tự động deploy
- Bot sẽ chạy 24/7

## Cách Dùng

### Khách hàng

1. Chat với @sv368cskh_bot
2. Gửi `/start`
3. Hỏi về: khuyến mãi, cách đăng ký, quy tắc, liên hệ

### Admin (Bạn)

1. Chat với @sv368cskh_bot
2. Gửi: `/admin_KaY8386_SV368_CSKH_2024_UpdateData_SecureMode`
3. Chọn chức năng từ menu

## Các lệnh

### Khách hàng
- `/start` - Bắt đầu

### Admin
- `/admin_KaY8386_SV368_CSKH_2024_UpdateData_SecureMode` - Vào admin panel

## File cấu trúc

```
sv368_bot/
├── sv368_bot.py          # Code bot chính
├── requirements.txt      # Dependencies
├── Procfile              # Config Railway
├── .env                  # Environment variables
├── sv368_data.json       # Database (tự tạo)
└── README.md             # Hướng dẫn này
```

## Database

Bot sử dụng file `sv368_data.json` để lưu dữ liệu:

```json
{
  "khuyến_mãi": "...",
  "quy_tắc": "...",
  "liên_hệ": "...",
  "cách_đăng_ký": "...",
  "admin_id": "...",
  "lần_cập_nhật": "..."
}
```

## Hỗ trợ

Nếu có vấn đề, liên hệ: @kay8386

---

**Bot đã sẵn sàng! 🚀**
