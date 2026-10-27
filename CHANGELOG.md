# Changelog

Tất cả thay đổi đáng chú ý của VietVoiceOmni được ghi tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/), phiên bản theo [SemVer](https://semver.org/).

## [1.0.0] - 2026-07-01

Phiên bản đầu tiên 🎉

### Thêm mới
- **Tạo giọng đọc**: sinh audio tiếng Việt từ giọng đã clone, có thanh tiến trình + **ETA theo từng câu**.
- **Nhân bản giọng**: tải audio mẫu → tạo giọng mới.
- **Kho giọng**: quản lý giọng đã lưu kèm thông số.
- **Thư viện**: lịch sử chia 3 mục Bài Thoại / Podcast / Sách nói; nghe lại, tải, xoá.
- **Phòng Podcast**: tối đa 13 người dẫn, mỗi người có tên/tính cách/thói quen/màu riêng + thông số giọng riêng; sinh hội thoại nhiều người từ kịch bản.
- **Sách nói**: parse EPUB/TXT → tách chương → xuất audiobook ghép đầy đủ.
- **Cài đặt**: thông số mặc định, chế độ hậu kỳ (RAW/Clean), bitrate MP3, lưu vào SQLite.
- Nhãn thông số bằng tiếng Việt: Độ biểu cảm / Độ mịn / Nghỉ giữa câu / Tốc độ đọc.
- Thêm điều khiển **Tốc độ đọc** (atempo qua ffmpeg).
- Engine mặc định & chính: **VoxCPM2** (model thường trú, nạp 1 lần).

### Kỹ thuật
- Giao diện **Reflex** (Python → React), theme tối, tiếng Việt có dấu toàn bộ.
- SQLite cho voices / history / hosts / podcasts / settings (có migration an toàn).
- Toàn bộ endpoint đã audit chạy thật end-to-end.
