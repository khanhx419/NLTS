# Lời thuyết trình — NL2Schedule / MANS

Gợi ý thời lượng: 15–20 phút và 3–5 phút demo. Mỗi mục khớp số slide.

## Slide 1. AI Agent trong lập kế hoạch và lập lịch công việc

Hôm nay em trình bày ứng dụng AI Agent trong pha lập kế hoạch, tập trung vào lập lịch công việc. Nguồn chính là bài NL ⇒ Schedule tại ACL 2026. Bài đề xuất MANS, một quy trình bốn tác tử, cùng bộ dữ liệu và mã nguồn. Em sẽ giải thích cơ chế, phân tích kết quả rồi minh họa bằng một ví dụ nhỏ. Phạm vi là lập lịch, không phải toàn bộ quản lý dự án hay hệ thống phân tích rủi ro.

Nguồn: Trang đầu, tóm tắt; PDF trang 1.

## Slide 2. Bài toán lập lịch từ mô tả công việc

Một yêu cầu nghe đơn giản vẫn ẩn nhiều ràng buộc. Hai sản phẩm có thể làm song song, nhưng không thể chiếm cùng một máy tại cùng thời điểm. Ngoài ra, công đoạn sơn phải chờ cắt xong. Vì vậy, chỉ tóm tắt yêu cầu thành danh sách việc chưa đủ: hệ thống phải tạo được lịch có thể thực hiện.

Nguồn: Mục 1, 3; ví dụ do nhóm xây dựng; PDF trang 1.

## Slide 3. Phạm vi và ba câu hỏi nghiên cứu

Bài báo có ba câu hỏi. Thứ nhất, khả năng lập lịch trực tiếp của các LLM hiện có. Thứ hai, phân tích lỗi thay vì chỉ nhìn một điểm số tổng. Thứ ba, thiết kế quy trình đa tác tử để cải thiện. Nghiên cứu không đặt mục tiêu tự động hóa toàn bộ SDLC; điều này phù hợp với hướng thu hẹp đề tài vào một pha cụ thể.

Nguồn: Mục 1, 4; PDF trang 2.

## Slide 4. Các ràng buộc của một lịch hợp lệ

Ta cần nắm ba yếu tố để hiểu các slide sau. Một là phụ thuộc giữa công đoạn. Hai là năng lực của tài nguyên; trong ví dụ, mỗi máy chỉ làm một việc tại một thời điểm. Ba là thời lượng phải đúng. Khi đã hợp lệ, ta mới xét chất lượng lịch qua makespan. Lịch ngắn nhưng vi phạm ràng buộc không phải phương án chấp nhận được.

Nguồn: Mục 3; ví dụ minh họa; PDF trang 3.

## Slide 5. MANS: bốn agent, bốn nhiệm vụ

Bốn agent ở đây là bốn vai trò được gọi tuần tự, không nhất thiết là bốn mô hình độc lập hay bốn bot chạy song song. Seeker khoanh đúng phạm vi. Weaver làm rõ từng công đoạn. Verifier kiểm tra cấu trúc đó với văn bản gốc. Architect nhận cấu trúc đã kiểm tra để lập lịch. Phân vai giúp giảm khối lượng suy luận của mỗi lượt gọi.

Nguồn: Mục 4.3.1, Hình 5; PDF trang 7.

## Slide 6. Seeker và Weaver: trích xuất đúng công việc

Seeker chỉ tập trung xác định nhiệm vụ, tránh bị phân tán bởi các chi tiết máy và thời gian. Weaver tiếp tục bóc tách mỗi nhiệm vụ thành các bước. Ví dụ A cần cắt ba phút rồi sơn hai phút; B cần cắt hai phút rồi sơn bốn phút. Bảng này là dữ liệu có cấu trúc, chưa phải lịch vì chưa có thời điểm bắt đầu.

Nguồn: Mục 4.3.1; ví dụ do nhóm xây dựng; PDF trang 7.

## Slide 7. Verifier: kiểm tra trước khi lập lịch

Verifier không đơn giản là hỏi mô hình có chắc không. Vai trò này phải đối chiếu từng trường với đầu vào gốc. Ví dụ nếu Weaver đọc nhầm thời gian sơn B thành ba phút, Verifier cần sửa thành bốn. Đây là kiểm tra ngữ nghĩa bằng LLM, vẫn có thể sai. Sau khi Architect lập lịch, ta còn cần kiểm tra ràng buộc bằng chương trình.

Nguồn: Mục 4.3.1; lỗi giả định để minh họa; PDF trang 7.

## Slide 8. Architect: chọn thứ tự sử dụng tài nguyên

Nếu làm A trước, máy cắt làm A từ 0 đến 3 rồi B từ 3 đến 5; máy sơn làm A từ 3 đến 5 rồi B từ 5 đến 9. Nếu B trước, B được sơn từ 2 đến 6, trong lúc A được cắt từ 2 đến 5; sau đó sơn A từ 6 đến 8. Makespan giảm từ chín xuống tám phút. Đây là ví dụ tính tay của nhóm, không phải số liệu thực nghiệm trong bài.

Nguồn: Ví dụ tính toán của nhóm; nguyên lý theo mục 3, 4.3.1; PDF trang 7.

## Slide 9. Bộ dữ liệu NL ⇒ Schedule

Tác giả thu thập 135 nhiệm vụ cơ bản từ các nguồn công khai, rồi ghép thành 240 bài toán. Mỗi bối cảnh có mười trường hợp cho từng cỡ từ năm đến mười nhiệm vụ: bốn nhân mười nhân sáu bằng 240. OR-Tools cung cấp lịch tối ưu tham chiếu. Mô tả tự nhiên được tạo từ dữ liệu cấu trúc bằng pipeline data2text. Cần gọi đúng đây là dữ liệu bán tổng hợp.

Nguồn: Mục 3, Bảng 1; PDF trang 3.

## Slide 10. Thiết kế thực nghiệm và thước đo

SER đo mức thực hiện đúng các bước, TCR đo nhiệm vụ hoàn tất, còn SFR yêu cầu cả lịch đều khả thi. Vì thế SER cao không có nghĩa cả lịch dùng được. WRT đo thời gian chạy tệ nhất trong thiết lập thí nghiệm. RMD đo độ lệch makespan so với lịch tham chiếu, trên các lịch khả thi. Khi so sánh phải giữ đúng mô hình nền và quy mô bài toán.

Nguồn: Mục 4.1.1–4.1.2, 4.3.1; PDF trang 4.

## Slide 11. LLM trực tiếp vẫn khó tạo lịch khả thi

Ở nhóm năm nhiệm vụ, GPT-4.1 có SFR năm phần trăm; Gemini Flash hai mươi phần trăm; o4-mini và Gemini Pro đều ba mươi hai phẩy năm phần trăm. Các con số là kết quả của bài báo với thiết lập lúc nghiên cứu, không phải đánh giá mọi phiên bản hiện tại. Điểm đáng chú ý là ngay mô hình mạnh vẫn có nhiều lịch không khả thi.

Nguồn: Bảng 2; chỉ trích nhóm #Task=5; PDF trang 5.

## Slide 12. Tốc độ và chất lượng lịch của MANS

Bảng bốn cho thấy một sự đánh đổi. MANS có WRT 79,59 giây, so với 133,70 của Optimus cộng OR-Tools, tương ứng giảm khoảng 40,5 phần trăm. Nhưng RMD của MANS là 0,085, cao hơn 0,022; lịch khả thi của nó lệch tối ưu nhiều hơn. Vì vậy không kết luận MANS thắng mọi mặt. Bảng trên chọn bốn hàng, không phải toàn bộ sáu baseline.

Nguồn: Bảng 4; phần trăm tính từ số liệu gốc; PDF trang 8.

## Slide 13. Mỗi vai trò có đóng góp riêng

Ablation study là thí nghiệm bỏ từng thành phần để xem vai trò của nó. Với năm nhiệm vụ, MANS đầy đủ có SFR bốn mươi phần trăm. Bỏ Seeker còn hai mươi; bỏ Weaver còn ba mươi bảy phẩy năm; bỏ Verifier còn ba mươi. Điều này ủng hộ việc phân vai, nhưng SFR bốn mươi phần trăm cũng cho thấy hệ thống chưa đủ tin cậy để tự động dùng mọi đầu ra.

Nguồn: Bảng 5, mục 4.3.2; PDF trang 8.

## Slide 14. Giá trị và giới hạn của nghiên cứu

Giá trị của bài là bài toán rõ, dữ liệu có chuẩn so sánh và mã nguồn để tiếp cận cơ chế. Tuy nhiên, bài chưa giải quyết các yếu tố thực tế như máy hỏng đột ngột hoặc thời lượng bất định. Vì vậy ta chỉ xem nó là nền cho trợ lý lập lịch, không tự gán thành hệ thống phân tích rủi ro toàn diện.

Nguồn: Mục 5–6; repository chính thức; PDF trang 9.

## Slide 15. Demo: theo dõi từng bước xử lý

Em bắt đầu demo ở chế độ offline để giải thích cơ chế ổn định. Đây là minh họa do nhóm viết, không giả lập nó thành suy luận LLM. Sau đó có thể thử chèn lỗi thời lượng để Verifier sửa, hoặc chèn xung đột để bộ kiểm tra lịch phát hiện. Chế độ LLM dùng bốn lượt gọi thật khi có cấu hình API. Giao diện và kiểm tra cục bộ là phần nhóm bổ sung.

Nguồn: Demo của nhóm, dựa trên vai trò MANS mục 4.3.1; PDF trang 7.

## Slide 16. Khả năng triển khai từ mã nguồn

Có mã nguồn thực, nhưng không nên nói tải về là chạy trơn tru. Khi đọc source, nhóm thấy dữ liệu Verifier đã sửa chưa được truyền đúng sang Architect. Đây là lỗi tích hợp có thể sửa. Chương trình đánh giá chạy được trên môi trường kiểm tra, nhưng lịch mẫu không khả thi. Demo của nhóm triển khai lại phần giao diện và quy trình nhỏ, phân biệt rõ với source gốc được liên kết trong tài liệu.

Nguồn: Kiểm tra commit 47f62b0 của SCUNLP/NL2Schedule, ngày 31/10/2026; PDF trang 1.

## Slide 17. Ứng dụng vào pha lập kế hoạch dự án

Để áp dụng vào đề tài, nhóm ưu tiên một quy trình có dữ liệu đủ rõ và quy mô nhỏ. Kết quả cần được kiểm tra trước khi người quản lý quyết định. Phần phân tích tình huống tăng thời lượng là hướng mở rộng của nhóm, không phải đóng góp đã được kiểm chứng trong bài. Cũng không nên đồng nhất các xung đột lịch với toàn bộ rủi ro dự án.

Nguồn: Đề xuất áp dụng của nhóm; giới hạn gốc ở mục 6; PDF trang 9.

## Slide 18. Kết luận theo ba câu hỏi nghiên cứu

Kết luận thứ nhất là không nên đánh giá agent chỉ bằng văn bản trả lời nghe hợp lý. Thứ hai, kiểm tra đầu ra trung gian và ràng buộc là thiết yếu. Thứ ba, MANS cho thấy phân vai có ích nhưng không bảo đảm lịch luôn khả thi hay tối ưu. Với bài tập lớn, một demo nhỏ có Gantt và bộ kiểm tra rõ ràng giúp thể hiện đúng cơ chế, đồng thời có tiêu chí để đánh giá.

Nguồn: Mục 4–6, Bảng 2, 4, 5; PDF trang 8.