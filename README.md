# NL2Schedule / MANS

Lập lịch đa tác vụ từ mô tả ngôn ngữ tự nhiên. Seeker, Weaver, Verifier, Architect gọi Gemini; Python kiểm tra lịch độc lập.

## Chạy demo

Cấu hình key bằng `real-demo/cau-hinh-api.cmd`, sau đó chạy `real-demo/start.cmd` hoặc `python server.py`. Mở http://127.0.0.1:8766/mans.

- [Hướng dẫn đầy đủ](real-demo/README.md).
- [Slide](slides.html).
- [Lời thuyết trình](docs/thuyet-trinh.md).
- [Hướng dẫn demo](docs/huong-dan-demo.md).

`final` chứa slide và trang mở demo NL2Schedule; bản mô phỏng cũ nằm trong `offline-backup`, không thay thế kết quả API.

Nguồn: [NL2Schedule, ACL 2026](https://aclanthology.org/2026.acl-long.1648/) · [Mã tác giả](https://github.com/SCUNLP/NL2Schedule).

Demo không tái lập toàn bộ benchmark. Lịch hợp lệ không đồng nghĩa tối ưu. Key và dữ liệu phiên không đưa lên Git.
