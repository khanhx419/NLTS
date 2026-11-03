# Hai hệ thống AI Agent chạy thật

**Hub-and-Spoke / Governance** và **NL2Schedule / MANS** dùng Gemini API thật. Python kiểm tra kết quả độc lập. Không có lịch mẫu hoặc mã mẫu tự thế chỗ khi API lỗi.

## Khởi động trên Windows

Yêu cầu: Python 3.10 trở lên, có mạng khi gọi Gemini. Chỉ dùng thư viện chuẩn Python, không cần pip install.

1. Tạo key tại [Google AI Studio](https://aistudio.google.com/apikey), chọn project Free Tier nếu muốn sử dụng hạn mức miễn phí.
2. Mở **cau-hinh-api.cmd**. Dán key khi được hỏi; ký tự được ẩn. Model mặc định: `gemini-3.5-flash-lite`.
3. Mở **start.cmd**, giữ cửa sổ server chạy.
4. Mở [Hub-and-Spoke](http://127.0.0.1:8766/hub) hoặc [MANS](http://127.0.0.1:8766/mans).

Hoặc trong PowerShell, đứng ở thư mục này:

```powershell
python setup_api.py
python app.py
```

Nếu dùng biến môi trường thay file `.env`:

```powershell
$env:GEMINI_API_KEY = 'YOUR_KEY'
$env:GEMINI_MODEL = 'gemini-3.5-flash-lite'
python app.py
```

Biến môi trường được ưu tiên hơn `.env`. Không gửi key qua chat, không đặt key trong HTML. File `.env` nằm trong `.gitignore`. Sau khi sửa cấu hình, bấm đọc lại cấu hình hoặc tải lại trang; không phải sửa code.

## API miễn phí

Kiểm tra nguồn chính thức ngày **01/11/2026**: [bảng giá Gemini](https://ai.google.dev/gemini-api/docs/pricing) liệt kê Free Tier cho Gemini 3.5 Flash-Lite. [Hạn mức](https://ai.google.dev/gemini-api/docs/rate-limits) phụ thuộc project/tài khoản và có thể thay đổi.

Miễn phí không đồng nghĩa vô hạn. Ứng dụng không biết tài khoản của bạn đã bật Cloud Billing hay chưa, không tự nâng cấp gói, không tự đổi sang model khác. Nếu quota hết, nó báo HTTP 429 và giữ phiên để bạn thử lại. Free Tier có thể sử dụng nội dung để cải thiện sản phẩm theo điều kiện của Google; dùng dữ liệu học tập.

## Hub-and-Spoke: luồng thực

1. **Planner — Gemini:** tạo một story và tiêu chí từ yêu cầu.
2. **Developer — Gemini:** viết hàm Python `validate_email(email)`. Nếu bạn nhập mã có sẵn, bước này chỉ nhận mã, không giả là Gemini đã viết.
3. **QA — local:** thông dịch AST của hàm trong tập con Python giới hạn và kiểm tra 14 ca email. Không dùng `exec()` hoặc `eval()` trên mã của model.
4. **Governance — local:** phân tích AST để tìm secret viết cứng, chuỗi ghép/alias đơn giản, default secret trong `getenv`, lệnh nguy hiểm/import/cấu trúc ngoài phạm vi.
5. **Developer sửa — Gemini:** nhận phản hồi thực, giá trị secret phát hiện được được che trước khi gửi sửa. Mã mới phải chạy kiểm tra lại; tối đa 3 lần sửa.
6. **Người dùng chấp nhận:** chỉ xuất hiện khi cả QA và Governance đạt. Không merge/deploy.

Muốn thấy vòng chặn–sửa: mở phần yêu cầu, bấm **Điền ví dụ có secret**, rồi bắt đầu. Đây là mã đầu vào được gắn nhãn rõ, không phải lỗi được bí mật chèn vào phản hồi Gemini.

Phần **Kiểm tra AST / QA trực tiếp** cho phép thử cổng kiểm tra ngay cả khi chưa có API key; không có agent LLM trong thao tác này.

### Phạm vi kiểm tra mã

- Một hàm `validate_email(email) -> bool` cho email cơ bản: trim hai đầu, đúng một `@`, phần trước không rỗng, tên miền có dấu chấm và các nhãn không rỗng, không có khoảng trắng bên trong.
- Tập con được hỗ trợ: gán biến, `if/elif/else`, `return`, boolean/so sánh, một số thao tác chuỗi, `len`, `bool`, `re.fullmatch/match/search`, `os.getenv`.
- Không có Python tùy ý, vòng lặp, helper function, I/O hoặc mạng trong mã sinh. Mã ngoài tập con bị chặn/yêu cầu viết lại.
- Worker chạy riêng với timeout 4 giây. Đây là bộ thông dịch AST giới hạn, **không phải Docker sandbox** và không phải bộ phát hiện mọi secret. PASS chỉ chứng minh đạt bộ quy tắc/ca thử hiện tại, không phải chứng nhận an toàn.

## MANS: luồng thực

1. Nhập mô tả có nhiệm vụ, công đoạn, tài nguyên và thời lượng.
2. **Seeker — Gemini:** xác định nhiệm vụ.
3. **Weaver — Gemini:** trích xuất các công đoạn.
4. **Verifier — Gemini:** đối chiếu và sửa dữ liệu, hoặc yêu cầu làm rõ.
5. **Bạn xác nhận dữ liệu** khớp mô tả gốc trước khi tiếp tục.
6. **Architect — Gemini:** sinh lịch. Không gọi bộ giải để thay lịch của Gemini.
7. **Python kiểm tra thật:** đủ công đoạn, không lặp, đúng máy/thời lượng/thứ tự, không trùng tài nguyên và makespan khớp lịch.
8. Nếu sai, giữ lỗi và cho Architect sửa; tối đa 3 lịch thử. Không tự tuyên bố thành công.

Giới hạn: 1–8 nhiệm vụ, tổng tối đa 36 công đoạn; mỗi nhiệm vụ là một chuỗi bước không ngắt quãng, mỗi bước dùng một tài nguyên sức chứa 1, thời lượng xác định. Yêu cầu ràng buộc phức tạp ngoài phạm vi phải được làm rõ. Verifier vẫn có thể đọc sai văn bản, nên việc người dùng đối chiếu là cần thiết. Lịch hợp lệ không đồng nghĩa đã chứng minh tối ưu.

Ứng dụng dựa trên bốn vai trò trong [NL2Schedule, ACL 2026](https://aclanthology.org/2026.acl-long.1648/). Xác nhận dữ liệu, kiểm tra cục bộ, vòng sửa và UI là phần bổ sung; không phải tái lập toàn bộ benchmark hoặc nguyên bản code tác giả.

## Dữ liệu và giao diện

- Một nút xử lý bước tiếp; cấu hình và lịch sử thu gọn, không có auto-run làm tốn API ngoài ý muốn.
- Session lưu SQLite trong `.state/`, hết hạn sau 24 giờ. Có token phiên, kiểm tra version để tránh chạy trùng; nạp lại cùng tab có thể tiếp tục.
- Có tải JSON phiên và thống kê token/thời gian nhận từ API. Key không lưu trong phiên hoặc gửi vào web.
- Server chỉ bind `127.0.0.1`. Static routes chỉ cho phép file UI; `.env`, source backend và database không được serve.

## Kiểm thử và mức xác nhận

```powershell
python -m unittest discover -s tests -v
```

Tests dùng model thay thế để không tốn API; server `app.py` không có chế độ model giả. AST/QA, SQLite và bộ kiểm tra lịch trong tests chạy thật. Test UI fixture trong `tests/ui_fixture_server.py` chỉ dùng khi kiểm thử, không khởi động khi chạy `start.cmd`.

Đã kiểm tra bằng API Gemini thật sau khi cấu hình key: Hub sinh mã và sửa secret đều đạt; MANS tạo lịch 9 phút hợp lệ. Xem LIVE-VERIFICATION.md. Các unit test vẫn dùng model thay thế để không tiêu tốn API khi chạy lại.

## Xử lý lỗi

- **Chưa có key:** chạy `cau-hinh-api.cmd` rồi đọc lại cấu hình trên web.
- **403:** kiểm tra API key, quyền project, khu vực và API được bật.
- **404 model:** đổi `GEMINI_MODEL` sang model đang được cấp quyền trong AI Studio.
- **429:** đã chạm quota; chờ hoặc kiểm tra Limits. Không tự bật billing để vượt hạn mức.
- **JSON không hợp lệ / output bị cắt:** thử lại đúng bước; có thể tăng `GEMINI_MAX_OUTPUT_TOKENS` trong giới hạn 8192.
- **Mã/lịch bị chặn:** đọc lỗi thực, yêu cầu agent sửa. Không sửa kết quả kiểm tra để biến FAIL thành PASS.
- **Port đang dùng:** chạy `python app.py --port 8767` rồi dùng đúng URL server in ra.


## Đã kiểm tra với Gemini thật — 01/11/2026

Model: `gemini-3.5-flash-lite`. Key được đọc từ `.env`, không đưa vào báo cáo hoặc Git.

| Luồng | Kết quả thực tế | Lượt gọi Gemini |
|---|---|---:|
| Hub sinh mã mới | QA và AST đạt, kết quả được chấp nhận | 2 |
| Hub sửa mã có secret mẫu | Bị chặn, Gemini sửa 1 lần, QA và AST đạt | 2 |
| MANS A/B | Cả 4 vai trò chạy; lịch 9 phút, đạt đủ bước, thời lượng, thứ tự và tài nguyên | 4 |

Lịch 9 phút là kết quả thật của lần chạy, không thay bằng lịch mẫu 8 phút. Kết quả này không chứng minh tối ưu hoặc độ chính xác trên mọi yêu cầu.

Google trả 404 cho Gemini 2.5 Flash/Flash-Lite trên key của người dùng mới, dù tên vẫn xuất hiện trong danh sách model. Vì vậy cấu hình hiện tại dùng model Flash-Lite mới đã gọi thành công. [Bảng giá chính thức](https://ai.google.dev/gemini-api/docs/pricing) có Free Tier cho Gemini 3.5 Flash-Lite; quota và khả năng miễn phí phụ thuộc project của người dùng.


## Học để hiểu code và thuyết trình

[Hướng dẫn học và trình diễn Hub-and-Spoke](HUONG-DAN-HOC-VA-THUYET-TRINH.md): kiến thức cần học, bản đồ code, kịch bản demo với thầy và câu hỏi thường gặp.


[Kiến thức cần học riêng cho Hub-and-Spoke](../docs/KIEN-THUC-CAN-HOC-HUB-AND-SPOKE.md) — đọc trước khi xem kịch bản demo.
