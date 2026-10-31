# Slide và demo — bản cuối

Hai chủ đề **Hub-and-Spoke** và **NL2Schedule / MANS**. Không gồm bộ Agentic PM cũ.

Mở `index.html` để chọn, hoặc mở trực tiếp đúng file dưới đây:

| File | Nội dung |
|---|---|
| [01_Slide_Hub-and-Spoke.html](final/01_Slide_Hub-and-Spoke.html) | 15 slide Hub-and-Spoke |
| [02_Demo_Hub-and-Spoke.html](final/02_Demo_Hub-and-Spoke.html) | Dev nộp mã → QA/Governance chặn secret → sửa → chấp nhận |
| [03_Slide_NL2Schedule_MANS.html](final/03_Slide_NL2Schedule_MANS.html) | 16 slide NL2Schedule |
| [04_Demo_NL2Schedule_MANS.html](final/04_Demo_NL2Schedule_MANS.html) | Seeker → Weaver → Verifier → Architect, lịch A/B 8 phút |

Mỗi file HTML đã nhúng ảnh, CSS và JavaScript. Hai demo chỉ có một ví dụ và hai nút thao tác, chạy offline không cần cài đặt. Không gọi LLM hay tái lập benchmark của tác giả. Slide đã bỏ phần giới thiệu demo và nút mở demo.

Điều khiển slide: Space / ← →; gõ số trang + Enter để nhảy trang ẩn; F toàn màn hình; bấm bên phải để tiến, bên trái để lùi. Slide NL có N để xem lời nói.

`slides.html` và `demo/index.html` cũng đã được cập nhật theo bản NL2Schedule cuối. Lời thuyết trình 16 slide tại [docs/thuyet-trinh.md](docs/thuyet-trinh.md).

## Nguồn

- NL2Schedule: Liao và cộng sự, ACL 2026. [Bài báo](https://aclanthology.org/2026.acl-long.1648/) · [PDF](https://aclanthology.org/2026.acl-long.1648.pdf) · [Mã tác giả](https://github.com/SCUNLP/NL2Schedule).
- Hình 1, 2, 5 trên slide NL2Schedule trích trực tiếp từ PDF. Sơ đồ và biểu đồ còn lại được vẽ lại theo nội dung, số liệu hoặc ví dụ có ghi nguồn.
- Hub-and-Spoke: Muhammad Awais (2026), Governing Agentic AI SDLC Project Management Framework. Các liên kết PDF trong slide trỏ tới tài liệu ở thư mục dự án gốc; PDF chưa nằm trong repository này. Nội dung và hình trình chiếu đã được nhúng.

Các file `server.py`, engine và kiểm tra pipeline từ phiên bản phát triển được giữ lại; không cần chúng để dùng 4 file cuối. Source gốc của tác giả được dẫn riêng; demo là bản minh họa do nhóm xây dựng.
