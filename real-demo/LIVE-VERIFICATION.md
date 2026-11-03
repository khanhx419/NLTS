## Đã kiểm tra với Gemini thật — 01/11/2026

Model: `gemini-3.5-flash-lite`. Key được đọc từ `.env`, không đưa vào báo cáo hoặc Git.

| Luồng | Kết quả thực tế | Lượt gọi Gemini |
|---|---|---:|
| Hub sinh mã mới | QA và AST đạt, kết quả được chấp nhận | 2 |
| Hub sửa mã có secret mẫu | Bị chặn, Gemini sửa 1 lần, QA và AST đạt | 2 |
| MANS A/B | Cả 4 vai trò chạy; lịch 9 phút, đạt đủ bước, thời lượng, thứ tự và tài nguyên | 4 |

Lịch 9 phút là kết quả thật của lần chạy, không thay bằng lịch mẫu 8 phút. Kết quả này không chứng minh tối ưu hoặc độ chính xác trên mọi yêu cầu.

Google trả 404 cho Gemini 2.5 Flash/Flash-Lite trên key của người dùng mới, dù tên vẫn xuất hiện trong danh sách model. Vì vậy cấu hình hiện tại dùng model Flash-Lite mới đã gọi thành công. [Bảng giá chính thức](https://ai.google.dev/gemini-api/docs/pricing) có Free Tier cho Gemini 3.5 Flash-Lite; quota và khả năng miễn phí phụ thuộc project của người dùng.
