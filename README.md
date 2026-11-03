# Hub-and-Spoke và NL2Schedule — bản chạy thật

Hai hệ thống trong [real-demo](real-demo/README.md) đã chuyển sang Gemini API và kiểm tra Python thực. Không có API key thì agent không chạy; lỗi API không được thay bằng dữ liệu mô phỏng.

## Mở nhanh

1. Chạy [cau-hinh-api.cmd](real-demo/cau-hinh-api.cmd) để nhập key từ Google AI Studio trên máy.
2. Chạy [start.cmd](real-demo/start.cmd) hoặc `python server.py`.
3. Mở [Hub-and-Spoke](http://127.0.0.1:8766/hub) hoặc [NL2Schedule](http://127.0.0.1:8766/mans).

Đọc [hướng dẫn đầy đủ](real-demo/README.md) về Free Tier, phạm vi kiểm tra, cách trình diễn và kiểm thử. Giao diện chỉ có một nút xử lý chính; cấu hình/lịch sử thu gọn.

## Các file cuối

- `final/01_Slide_Hub-and-Spoke.html`: bộ slide Hub-and-Spoke.
- `final/02_Demo_Hub-and-Spoke.html`: trang mở hệ thống Hub chạy thật.
- `final/03_Slide_NL2Schedule_MANS.html`: bộ slide NL2Schedule.
- `final/04_Demo_NL2Schedule_MANS.html`: trang mở hệ thống MANS chạy thật.

Ảnh và nội dung slide được giữ nguyên. `slides.html` là lối mở bộ slide NL2Schedule; lời thuyết trình tại `docs/thuyet-trinh.md`. Hai bản mô phỏng trước được giữ trong `offline-backup/` để đối chiếu, không được tự dùng thay cho kết quả API.

## Nguồn nghiên cứu

NL2Schedule / MANS: [Liao và cộng sự, ACL 2026](https://aclanthology.org/2026.acl-long.1648/) · [PDF](https://aclanthology.org/2026.acl-long.1648.pdf) · [Mã tác giả](https://github.com/SCUNLP/NL2Schedule).

Hub-and-Spoke: tài liệu Governing Agentic AI SDLC Project Management Framework của Muhammad Awais (2026). Hệ thống demo là triển khai riêng cho phạm vi hàm kiểm tra email và cổng Governance, không phải mã nguồn tác giả.

Model, phạm vi dữ liệu, bước người dùng xác nhận, QA/AST và vòng sửa được giải thích rõ trong real-demo/README.md. Đã kiểm tra cả hai hệ thống bằng Gemini 3.5 Flash-Lite thật. Hub qua QA/AST và sửa được secret mẫu; MANS tạo lịch hợp lệ 9 phút. Chi tiết tại real-demo/LIVE-VERIFICATION.md.
