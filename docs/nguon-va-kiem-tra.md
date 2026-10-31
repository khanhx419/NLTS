# Đối chiếu nguồn

Nguồn chính: https://aclanthology.org/2026.acl-long.1648.pdf (21 trang). Số trang trong slide tính từ trang PDF đầu tiên, không dùng số trang kỷ yếu 35620–35640.

| Slide | Căn cứ |
|---|---|
| 1–3 | Trang 1–2, mục 1, RQ1–RQ3 |
| 4 | Trang 3, định nghĩa bài toán; ví dụ riêng |
| 5–7 | Trang 7, Hình 5, mục 4.3.1; dữ liệu A/B là ví dụ riêng |
| 8 | Tính tay hai lịch A/B: 9 và 8 phút; không phải thực nghiệm tác giả |
| 9 | Trang 3–4, mục 3: 135 nhiệm vụ cơ bản, 240 trường hợp, 4 bối cảnh, 5–10 nhiệm vụ |
| 10 | Trang 4–5, mục 4.1; trang 7–8 mục 4.3 |
| 11 | Trang 5, Bảng 2, #Task=5: SFR GPT-4.1=.050; Flash=.200; o4-mini=.325; Pro=.325 |
| 12 | Trang 8, Bảng 4: MANS WRT=79.59s, RMD=.085; Optimus+OR Tools=133.70s, .022. Giảm WRT=(133.70−79.59)/133.70≈40.47%. Không gọi RMD=.085 là tỷ lệ an toàn. |
| 13 | Trang 8, Bảng 5, #Task=5: SFR đầy đủ=.400; bỏ Seeker=.200; bỏ Weaver=.375; bỏ Verifier=.300 |
| 14,17,18 | Mục 5–6 và diễn giải có ghi rõ phần áp dụng của nhóm |
| 15–16 | Demo riêng; source gốc commit 47f62b052c6585f6ab1a10ca948378db22666078 |

## Kiểm tra source gốc ngày 31/10/2026

- Có Python source, prompt, 4 JSONL datasets, yêu cầu numpy/openai/scipy, script dự đoán và đánh giá.
- `LLM_tools/api_call.py` có placeholder key/base URL.
- `utils/prompts.py`: Architect đang nhận `tasks_steps_output` từ Weaver thay vì `output` đã sửa bởi Verifier. Demo viết lại đã truyền đúng dữ liệu đã xác nhận.
- Script chạy ở gốc nhưng đường dẫn `../data/cooking.jsonl` cần đổi thành `data/cooking.jsonl`.
- Chạy bộ đánh giá nguyên bản với `schedule_example.jsonl`, instance 1, `data/cooking.jsonl`: SER=.3103448275862069; TCR=.2; SF=False. Đây là một mẫu, không thay thế kết quả benchmark trong bài.
- Chưa thấy LICENSE ở bản kiểm tra. Repo này chỉ dẫn nguồn, không tái phân phối mã gốc hay PDF.

## Giới hạn kiểm tra demo của nhóm

Kiểm tra chương trình offline và pipeline mock không đồng nghĩa xác nhận độ chính xác LLM. Bộ kiểm tra lịch chỉ so với cấu trúc nhiệm vụ đang có; nếu Verifier vẫn đọc sai văn bản, bộ kiểm tra không tự phát hiện toàn bộ sai lệch ngữ nghĩa.
