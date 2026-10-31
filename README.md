# NL2Schedule / MANS — Slide và demo

Ứng dụng hệ đa tác tử AI trong lập kế hoạch và lập lịch công việc từ mô tả ngôn ngữ tự nhiên.

## Mở nhanh

- Mở `index.html` để chọn **18 slide** hoặc **demo offline**, không cần cài thư viện.
- Slide: phím ← →, Home/End, F toàn màn hình, N lời thuyết trình; số + Enter để nhảy trang; Ctrl+P để in/xuất PDF. Bấm vùng bên phải để tiến, vùng bên trái để lùi. Gõ số trang rồi Enter để nhảy ẩn (không có thanh công cụ).
- Lời nói từng slide: [docs/thuyet-trinh.md](docs/thuyet-trinh.md).
- Kịch bản trình diễn: [docs/huong-dan-demo.md](docs/huong-dan-demo.md).

## Demo LLM thực (tùy chọn)

Python 3.10+, chỉ dùng thư viện chuẩn. Trong PowerShell:

```powershell
$env:LLM_API_KEY = 'YOUR_KEY'
$env:LLM_BASE_URL = 'https://YOUR_PROVIDER/v1'
$env:LLM_MODEL = 'YOUR_AVAILABLE_MODEL'
python server.py
```

Mở http://127.0.0.1:8765/demo/ rồi chọn **LLM thật**. Endpoint cần tương thích Chat Completions, model hỗ trợ system message và trả JSON. Không thêm `/chat/completions` vào base URL. Mỗi lần bắt đầu chạy gọi 4 lượt LLM, có thể phát sinh phí theo nhà cung cấp. Key chỉ ở biến môi trường server, không lưu vào repo hay browser. Chế độ này không hoạt động trên hosting tĩnh như GitHub Pages; cần server local.

## Phân biệt các thành phần

| Thành phần | Nguồn và phạm vi |
|---|---|
| MANS, số liệu thực nghiệm | Bài báo ACL 2026 bên dưới |
| Slide, lời nói, giao diện | Nhóm triển khai cho bài thuyết trình |
| Offline | Ví dụ cố định 2 nhiệm vụ, có thể đổi thời lượng; kiểm tra bằng quy tắc và bộ lập lịch nhỏ, không phải LLM |
| Chế độ LLM | Viết lại quy trình 4 vai trò dựa trên bài, không phải nguyên bản code tác giả hay tái lập toàn bộ benchmark |
| Gantt và kiểm tra xung đột | Phần bổ sung của nhóm; kiểm tra so với cấu trúc đã xác nhận |

Không sao chép kho nguồn tác giả vào repo này vì chưa thấy LICENSE ở commit kiểm tra. Có thể tải source gốc riêng:

```powershell
git clone https://github.com/SCUNLP/NL2Schedule.git upstream-source
git -C upstream-source checkout 47f62b052c6585f6ab1a10ca948378db22666078
```

## Nguồn học thuật

Wenrui Liao, Weihong Du, Yi Li, Hongru Liang, Wenqiang Lei. **NL ⇒ Schedule: Evaluate Multitask Scheduling Capability of Large Language Models.** ACL 2026, Long Papers, 35620–35640.

- [Bài báo và DOI](https://aclanthology.org/2026.acl-long.1648/)
- [PDF chính thức](https://aclanthology.org/2026.acl-long.1648.pdf)
- [Repository tác giả](https://github.com/SCUNLP/NL2Schedule)
- [Ghi chú đối chiếu số liệu và mã](docs/nguon-va-kiem-tra.md)

## Kiểm tra

```powershell
node test_engine.cjs
python -m unittest test_pipeline.py
```

Demo offline được kiểm tra với lịch 8 phút và phát hiện lịch vi phạm. Pipeline được kiểm tra bằng mock để xác nhận Architect nhận dữ liệu đã sửa của Verifier. Chưa xác nhận kết quả gọi LLM thật khi không có API cấu hình. Kết quả có thể khác theo model. Bộ kiểm tra không chứng minh nội dung đã trích xuất hoàn toàn đúng văn bản, cũng không chứng minh tối ưu ở chế độ LLM.

## Hình minh họa

Hình 1, 2 và 5 được trích từ PDF bài báo và giữ nguyên tỷ lệ, có ghi nguồn tại slide. Các sơ đồ và biểu đồ còn lại được trình bày lại theo dữ liệu đã dẫn nguồn.

Demo cho phép chọn lại bước đã chạy để xem thẻ nhiệm vụ, chuỗi công đoạn, bảng sửa dữ liệu và lịch Gantt; JSON được thu gọn trong phần mở rộng.
