# Kịch bản demo 3–5 phút

1. Mở `demo/index.html`, chọn minh họa offline. Giữ A cắt 3, sơn 2; B cắt 2, sơn 4.
2. Bấm **Bước tiếp theo**: Seeker nhận diện A/B. Nhấn mạnh đây là hai nhiệm vụ, chưa có lịch.
3. Bấm lần hai: Weaver bóc tách công đoạn. Ô chèn lỗi đang bật nên B bị đọc sai thời lượng sơn thành 5 phút.
4. Bấm lần ba: Verifier sửa thời lượng B về 4 phút, dựa trên dữ liệu yêu cầu. Ở chế độ này việc so sánh được viết bằng quy tắc để minh họa.
5. Bấm lần bốn: Architect tạo lịch. Gantt: cắt B 0–2, cắt A 2–5; sơn B 2–6, sơn A 6–8. Hai máy có thể làm đồng thời, cùng một máy không chồng lấn.
6. Bấm **Thử chèn xung đột**: hai việc cùng dùng máy bị chồng thời gian. Bộ kiểm tra báo lỗi. Mục đích là phân biệt lịch nhìn có vẻ đúng và lịch đúng ràng buộc.
7. Bấm **Làm lại**, đổi thời lượng sơn B, chạy lại để xem lịch thay đổi; tắt chèn lỗi để xem đường đi khi dữ liệu đã đúng.
8. Có thể tải kết quả JSON để đưa vào báo cáo.

## Chế độ LLM thật

Chạy server và đặt biến môi trường theo README. Mở bằng localhost, chọn LLM thật. Có thể sửa mô tả thành 2–3 sản phẩm khác. Đặt rõ mỗi bước dùng máy nào và bao nhiêu phút, các bước làm tuần tự. Nút chạy đầu tiên gọi đủ bốn agent; các lần bấm sau hiển thị kết quả từng giai đoạn. Đợi hoàn tất, không chuyển chế độ lúc đang gọi.

Verifier nhận văn bản gốc và dữ liệu Weaver, Architect nhận đúng bản Verifier trả về. Nếu bộ kiểm tra báo lỗi thì giữ nguyên kết quả để phân tích; không tự tuyên bố thành công. Quy trình này chưa có vòng tự sửa lịch sau Architect. Dữ liệu gửi đến nhà cung cấp model là mô tả bạn nhập và kết quả trung gian; chỉ dùng ví dụ học tập.

## Câu trả lời khi thầy hỏi

- **Có phải nguyên bản của tác giả?** Không. Source gốc được liên kết trong README; demo này triển khai nhỏ để giải thích cơ chế, có thêm Gantt và kiểm tra lịch.
- **Offline có dùng AI không?** Không. Nó dùng ví dụ và thuật toán nhỏ cho kết quả ổn định. Chế độ LLM mới gọi model thật.
- **Có bảo đảm tối ưu?** Bộ lập lịch offline duyệt ví dụ rất nhỏ; không thể suy rộng sang mọi bài toán. LLM không bảo đảm tối ưu hay khả thi.
- **Có phân tích rủi ro không?** Demo kiểm tra vi phạm lịch. Phân tích thời lượng bất định và rủi ro toàn diện nằm ngoài phạm vi nghiên cứu này.

## Giao diện trình diễn

Bốn ô phía trên có thể bấm để xem lại bước đã chạy. Seeker hiện thẻ nhiệm vụ; Weaver hiện công đoạn; Verifier tô vàng trường được sửa; Architect hiện Gantt và kết quả kiểm tra. Bước trước chỉ xem lại kết quả, không gọi API. Nút khôi phục lịch giúp so sánh với tình huống trùng máy.
