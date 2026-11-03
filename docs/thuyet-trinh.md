# Lời thuyết trình — NL2Schedule / MANS

## Slide 1. AI Agent trong lập kế hoạch và lập lịch công việc

Hôm nay em trình bày ứng dụng AI Agent trong pha lập kế hoạch, tập trung vào lập lịch công việc. Nguồn chính là bài NL ⇒ Schedule tại ACL 2026. Bài đề xuất MANS, một quy trình bốn tác tử, cùng bộ dữ liệu và mã nguồn. Em sẽ giải thích cơ chế, phân tích kết quả rồi minh họa bằng một ví dụ nhỏ. Phạm vi là lập lịch, không phải toàn bộ quản lý dự án hay hệ thống phân tích rủi ro.

Nguồn: Trang đầu, tóm tắt; PDF trang 1.

## Slide 2. Từ bảng dữ liệu đến lập lịch trực tiếp từ văn bản

Cách truyền thống bắt đầu từ yêu cầu của người dùng, nhưng chương trình tính lịch không tự đọc hiểu mô tả đó. Con người phải chuyển yêu cầu thành bảng số, hay ma trận. Ví dụ, bảng ghi sản phẩm A dùng máy cắt trong ba phút, rồi dùng máy sơn trong hai phút. Bộ giải, tiếng Anh là solver, là chương trình tìm cách sắp xếp thời gian sao cho đúng các điều kiện đã nhập. Đầu ra là thời điểm bắt đầu và kết thúc của từng công đoạn. Ở hướng LLM kết hợp bộ giải, LLM giúp chuyển văn bản thành mô hình toán và mã mà bộ giải sử dụng; bộ giải vẫn chịu trách nhiệm tính lịch. Với MANS, LLM đảm nhiệm cả việc hiểu văn bản, tách nhiệm vụ, kiểm tra thông tin và đề xuất lịch cụ thể qua bốn vai trò. End-to-end không có nghĩa chỉ một lượt gọi LLM, mà là đi từ mô tả bằng lời tới lịch mà không cần con người mã hóa ma trận hoặc dùng bộ giải bên ngoài để tính lịch trong luồng MANS. Lịch do LLM tạo vẫn cần kiểm tra tính hợp lệ.

Nguồn: Mục 1–2, 4.3.1 và Hình 1: Matrix2Schedule, LLM + solver, MANS; PDF trang 1.

## Slide 3. Phạm vi và ba câu hỏi nghiên cứu

Bài báo có ba câu hỏi. Thứ nhất, khả năng lập lịch trực tiếp của các LLM hiện có. Thứ hai, phân tích lỗi thay vì chỉ nhìn một điểm số tổng. Thứ ba, thiết kế quy trình đa tác tử để cải thiện. Nghiên cứu không đặt mục tiêu tự động hóa toàn bộ SDLC; điều này phù hợp với hướng thu hẹp đề tài vào một pha cụ thể.

Nguồn: Mục 1, 4; PDF trang 2.

## Slide 4. Ràng buộc và mục tiêu lập lịch

Slide này phân biệt ràng buộc và mục tiêu. Ràng buộc là điều kiện lịch bắt buộc phải đáp ứng: cắt xong mới sơn, không dùng trùng một máy tại cùng thời điểm, và mỗi công đoạn có đủ thời lượng yêu cầu. Ví dụ cắt A cần ba phút thì thời điểm kết thúc phải cách thời điểm bắt đầu đúng ba phút, vì công đoạn không bị ngắt quãng. Khi lịch đã hợp lệ, ta mới xét mục tiêu giảm makespan, tức thời điểm hoàn thành công đoạn cuối cùng. Hai lịch tám và chín phút đều có thể hợp lệ; lịch tám phút tốt hơn theo mục tiêu này.

Nguồn: Mục 3: ràng buộc thứ tự, máy và mục tiêu makespan; ví dụ minh họa; PDF trang 3.

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

## Slide 9. Nguồn dữ liệu, cách tạo bài toán và mục đích đánh giá

Tác giả cần bộ bài toán có cả mô tả tự nhiên và đáp án để kiểm tra LLM có lập lịch đúng hay không. Vì dữ liệu dự án công nghiệp đầy đủ thường khó tiếp cận, họ tổng hợp và đối chiếu nhiều nguồn công khai. Phụ lục A.1, Bảng 6 liệt kê sách như Fundamentals of Modern Manufacturing và Automotive Handbook, website Toyota, DMG MORI, cùng các trò chơi mô phỏng Construction Simulator, Big Pharma và Overcooked 2. Từ các nguồn này, tác giả xây dựng 135 nhiệm vụ cơ bản: 28 về sản xuất, 29 về xây dựng, 32 về dược phẩm và 46 về nấu ăn. Một nhiệm vụ gồm nhiều công đoạn, mỗi công đoạn có máy cần dùng, thời lượng và thứ tự thực hiện. Sau đó, tác giả nhóm các nhiệm vụ có dùng chung máy thành 13 nhóm, để khi ghép bài toán sẽ xuất hiện cạnh tranh tài nguyên. Trong từng nhóm, họ lấy từ năm đến mười nhiệm vụ để tạo một bài toán lập lịch. Có bốn lĩnh vực, sáu cỡ bài toán từ năm đến mười nhiệm vụ, và mười bài cho mỗi tổ hợp lĩnh vực với cỡ bài, nên tổng là bốn nhân sáu nhân mười bằng 240. Tác giả dùng mẫu câu rồi GPT-4 để tạo và làm mượt mô tả ngôn ngữ tự nhiên từ cấu trúc công việc. OR-Tools tạo lịch tối ưu tham chiếu. Vì thế mỗi bài có ba phần: mô tả bằng văn bản, cấu trúc công đoạn đúng và lịch tham chiếu. Khi đánh giá, LLM nhận mô tả văn bản để sinh lịch; tác giả đối chiếu đầu ra với cấu trúc công việc và lịch tham chiếu để đo việc thực hiện đúng công đoạn, tính khả thi và chất lượng thời gian hoàn thành. Bộ này phục vụ đánh giá và so sánh các phương pháp trong nghiên cứu; không phải 240 dự án công nghiệp thu thập nguyên trạng.

Nguồn: Mục 3, Bảng 1; phụ lục A.1–A.3, Bảng 6. Dữ liệu tổng hợp, không phải 240 dự án thực tế.; PDF trang 12.

## Slide 10. Đo lịch đúng ở ba mức: bước, nhiệm vụ và toàn bộ lịch

Ba chỉ số tương ứng với ba mức kiểm tra khác nhau. SER, Overall Steps Execution Rate, đo phần công đoạn được thực hiện đúng, lấy trung bình theo nhiệm vụ rồi theo các lịch; không mặc nhiên tính bằng tổng bước đúng chia tổng bước của mọi bài. TCR, Average Task Completion Rate, đo tỷ lệ nhiệm vụ hoàn thành trọn vẹn, lấy trung bình theo lịch. SFR, Schedule Feasibility Rate, đo tỷ lệ các lịch hoàn toàn khả thi trong số lịch được sinh. Ba ví dụ trên là ví dụ độc lập để hiểu cách đọc chỉ số, không phải số liệu thí nghiệm. Một lịch vẫn có thể hoàn thành vài nhiệm vụ nhưng không đạt điều kiện toàn bộ lịch. Vì thế khi đánh giá ứng dụng thực tế phải nhìn SFR thay vì chỉ nhìn mức thực hiện đúng từng phần.

Nguồn: Mục 4.1.2, công thức 1–3; ví dụ minh họa cách đọc chỉ số; PDF trang 5.

## Slide 11. Có bao nhiêu lịch được tạo ra hoàn toàn hợp lệ?

Biểu đồ dùng cùng thước đo SFR đã được định nghĩa trước. Bốn hàng mô hình trả lời trực tiếp lấy từ Bảng 2, nhóm bài có năm nhiệm vụ. Hàng MANS lấy từ Bảng 3, cùng quy mô năm nhiệm vụ và dùng Gemini 2.5 Flash không thinking làm mô hình nền. Cặp so sánh phù hợp nhất ở đây là Flash trực tiếp hai mươi phần trăm với MANS bốn mươi phần trăm, vì giữ cùng mô hình nền. Các mô hình khác cho bối cảnh tham khảo, không phải kiểm soát hết mọi yếu tố so sánh. MANS cải thiện tỷ lệ lịch hợp lệ, nhưng bốn mươi phần trăm cũng có nghĩa sáu mươi phần trăm lịch chưa đạt điều kiện toàn bộ. Kết quả này không chứng minh hệ thống sẵn sàng tự động lập lịch trong thực tế.

Nguồn: Bảng 2 và 3, nhóm #Task=5; MANS dùng Gemini 2.5 Flash không thinking; PDF trang 7.

## Slide 12. Phân biệt thời gian sinh lịch và thời gian làm công việc

Cần tách hai đồng hồ. WRT là thời gian máy tính chạy để tạo câu trả lời, lấy trường hợp lâu nhất trong thiết lập thí nghiệm; nó không phải thời gian trung bình và không phải thời gian các công việc diễn ra. Makespan là độ dài kế hoạch: thời điểm công đoạn cuối cùng hoàn tất tính từ mốc không. RMD đo mức makespan lệch tương đối so với tham chiếu, rồi lấy trung bình. Ví dụ tham chiếu mười phút, lịch hợp lệ mười một phút, độ lệch là một phần mười tức mười phần trăm. Chỉ số RMD được dùng để đánh giá chất lượng thời gian của những lịch đã khả thi; nó không thay thế việc xem SFR. Hai ví dụ số trên để giải thích khái niệm, không phải số liệu trong Bảng 4.

Nguồn: Mục 3, 4.3.1 và Bảng 4; ví dụ minh họa đơn vị và độ lệch; PDF trang 8.

## Slide 13. Đánh đổi: sinh lịch nhanh hơn, nhưng lịch chưa ngắn bằng

Bảng này tách hai mặt thay vì nói chung MANS tốt hơn. Các giá trị RMD gốc là 0,023, 0,022 và 0,085, được đổi thành phần trăm để dễ đọc. WRT của MANS là 79,59 giây, thấp hơn 133,70 giây của Optimus cộng OR-Tools khoảng 40,5 phần trăm. Đây là so sánh thời gian chạy lâu nhất, không kết luận mọi lần chạy hay thời gian trung bình đều nhanh hơn từng ấy. Ở mặt chất lượng lịch khả thi, RMD của MANS là tám phẩy năm phần trăm, cao hơn hai phẩy hai phần trăm của Optimus cộng OR-Tools. Vì vậy lịch MANS xa thời gian tối ưu hơn theo chỉ số báo cáo này. RMD được tính trên lịch khả thi của từng phương pháp; không dùng nó để bỏ qua khác biệt SFR hoặc tuyên bố một phương pháp thắng ở mọi bài. Hai hệ CoE, Chain of Experts, và Optimus là các baseline LLM kết hợp solver trong bài.

Nguồn: Bảng 4; RMD đổi từ số thập phân sang %; phần trăm WRT tính từ số gốc; PDF trang 8.

## Slide 14. Bỏ từng vai trò để kiểm tra chúng có thực sự hữu ích

Thí nghiệm này được gọi là ablation study, tức bỏ một thành phần để kiểm tra phần đó có đóng góp hay không. Ta giữ cùng thiết lập và quy mô năm nhiệm vụ. Bản đầy đủ tạo được bốn mươi phần trăm lịch hợp lệ. Bỏ Seeker còn hai mươi, bỏ Weaver còn ba mươi bảy phẩy năm, bỏ Verifier còn ba mươi. Do đó dữ liệu ủng hộ việc chia vai trò, đặc biệt là nhận diện đúng phạm vi công việc. Không cộng các tỷ lệ giảm với nhau, vì mỗi hàng là một cấu hình thử riêng. Kết quả cho thấy ích lợi tương đối của các vai trò, không chứng minh bản đầy đủ luôn đúng.

Nguồn: Mục 4.3.2, Bảng 5, nhóm #Task=5; PDF trang 8.

## Slide 15. Nghiên cứu đã làm được gì và còn thiếu bằng chứng nào?

Bài này không chỉ là một bài nêu tầm nhìn: tác giả đã xây bộ đánh giá, triển khai MANS và thực hiện thí nghiệm. Tuy vậy, có thực nghiệm không đồng nghĩa đã đạt độ tin cậy để vận hành. Cần đọc cùng lúc tỷ lệ lịch hợp lệ, độ lệch thời gian, tốc độ và phạm vi dữ liệu. Các giới hạn dữ liệu bán tổng hợp, số nhiệm vụ nhỏ, thời lượng bất định và tài nguyên động đều được bài thừa nhận. Nghiên cứu có giá trị như một phương pháp và bộ đánh giá cho bài toán mới, nhưng không phải bằng chứng rằng hệ thống có thể tự động ra quyết định lập lịch mà không kiểm tra. Việc có mã công khai cũng không tự chứng minh mọi người đều tái lập được toàn bộ kết quả.

Nguồn: Mục 3–6, Bảng 3–5; liên kết mã nguồn ở trang đầu; PDF trang 9.

## Slide 16. Áp dụng vào lập kế hoạch: đề xuất lịch và kiểm tra trước khi dùng

Đây là cách nhóm diễn giải khả năng áp dụng, không phải một vòng kiểm tra bên ngoài đã được tác giả chứng minh trong MANS nguyên bản. Hệ thống có thể hỗ trợ biến yêu cầu thành phương án, nhưng trước khi dùng cần chương trình kiểm tra ràng buộc và người quản lý xem xét. Bộ kiểm tra cũng chỉ có ý nghĩa khi cấu trúc công việc đối chiếu là đúng; nếu đọc sai yêu cầu từ đầu thì cần kiểm tra lại với văn bản gốc. Phạm vi này phù hợp một trợ lý lập kế hoạch có giám sát. Không gọi đây là giải pháp tự động hoàn chỉnh hay hệ thống phân tích rủi ro toàn diện.

Nguồn: Hướng áp dụng của nhóm dựa trên kết quả và giới hạn mục 4–6; PDF trang 9.

## Slide 17. Kết luận: MANS cải thiện cách lập lịch, chưa bảo đảm mọi đầu ra

Kết luận cần giữ đúng mức bằng chứng. MANS là phương pháp đã triển khai và đánh giá, không chỉ một ý tưởng. Trong thiết lập được báo cáo, chia vai trò giúp cải thiện một số chỉ số và giảm thời gian chạy lâu nhất so với các cấu hình LLM cộng solver được so sánh. Nhưng SFR vẫn thấp và chất lượng thời gian của lịch khả thi chưa tốt nhất. Vì thế nghiên cứu không chứng minh rằng MANS đủ tin cậy để dùng tự động trong vận hành thực tế. Điểm học được là cách đặt bài toán từ văn bản tới lịch, xây chuẩn đánh giá và kiểm tra tác dụng của từng vai trò. Nếu mục tiêu triển khai đòi hỏi mọi lịch đều đúng mà không cần kiểm tra, kết quả của bài hiện chưa đáp ứng tiêu chí đó.

Nguồn: Mục 4–6; Bảng 2–5; PDF trang 9.