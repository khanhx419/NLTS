# NL2Schedule / MANS chạy thật

**NL2Schedule / MANS** dùng Gemini API thật. Python kiểm tra kết quả độc lập. Không có lịch mẫu tự thế chỗ khi API lỗi.

## Khởi động trên Windows

Yêu cầu: Python 3.10 trở lên, có mạng khi gọi Gemini. Chỉ dùng thư viện chuẩn Python, không cần pip install.

1. Tạo key tại [Google AI Studio](https://aistudio.google.com/apikey), chọn project Free Tier nếu muốn sử dụng hạn mức miễn phí.
2. Mở **cau-hinh-api.cmd**. Dán key khi được hỏi; ký tự được ẩn. Model mặc định: `gemini-3.5-flash-lite`.
3. Mở **start.cmd**, giữ cửa sổ server chạy.
4. Mở [MANS](http://127.0.0.1:8766/mans).

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

Tests dùng model thay thế để không tốn API; server `app.py` không có chế độ model giả. SQLite và bộ kiểm tra lịch trong tests chạy thật. Test UI fixture trong `tests/ui_fixture_server.py` chỉ dùng khi kiểm thử, không khởi động khi chạy `start.cmd`.

Đã kiểm tra API Gemini thật: bốn vai trò chạy và tạo lịch 9 phút hợp lệ. Xem LIVE-VERIFICATION.md.

## Xử lý lỗi

- **Chưa có key:** chạy `cau-hinh-api.cmd` rồi đọc lại cấu hình trên web.
- **403:** kiểm tra API key, quyền project, khu vực và API được bật.
- **404 model:** đổi `GEMINI_MODEL` sang model đang được cấp quyền trong AI Studio.
- **429:** đã chạm quota; chờ hoặc kiểm tra Limits. Không tự bật billing để vượt hạn mức.
- **JSON không hợp lệ / output bị cắt:** thử lại đúng bước; có thể tăng `GEMINI_MAX_OUTPUT_TOKENS` trong giới hạn 8192.
- **Lịch bị chặn:** đọc lỗi thực, yêu cầu agent sửa. Không sửa kết quả kiểm tra để biến FAIL thành PASS.
- **Port đang dùng:** chạy `python app.py --port 8767` rồi dùng đúng URL server in ra.

