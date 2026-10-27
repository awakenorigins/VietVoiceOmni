# Đóng góp cho VietVoiceOmni

Cảm ơn bạn quan tâm! Một số lưu ý ngắn gọn.

## Thiết lập môi trường

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows ( source .venv/bin/activate trên Linux/macOS )
pip install -r requirements.txt
reflex run --env dev
```

Cần **ffmpeg** trong PATH và trọng số model **VoxCPM2** (`openbmb/VoxCPM2`).

## Quy ước

- **UI**: chỉnh trong `VietVoiceOmni/VietVoiceOmni.py`. Reflex 0.9 **không tự sinh setter** — khai báo `set_xxx` thủ công trong `state.py`.
- **Logic**: đặt trong `state.py`. Tác vụ chạy lâu dùng `@rx.event(background=True)` để không khoá UI.
- **Engine**: mọi lệnh gọi VoxCPM2 đi qua `backend/voice_service.py` (giữ model resident).
- **DB**: thêm cột mới bằng migration `_ensure_col` trong `backend/db.py` để không vỡ DB cũ.
- **Chữ tiếng Việt**: luôn có dấu đầy đủ trên giao diện.

## Trước khi mở PR

1. Chạy thử app: `reflex run --env dev` — không lỗi compile.
2. Nếu thêm endpoint: viết/chạy script audit (xem các `audit_*.py`) để chứng minh chạy thật.
3. Mô tả rõ thay đổi trong PR, cập nhật `CHANGELOG.md`.

## Giấy phép

Đóng góp của bạn được phát hành theo [Apache License 2.0](LICENSE).
