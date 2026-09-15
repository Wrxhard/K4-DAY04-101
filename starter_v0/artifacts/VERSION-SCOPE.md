# Phân nhóm phiên bản theo yêu cầu đã chốt

Trạng thái hiện tại: người dùng đã yêu cầu **v3 — Context & Clarify** trên nền
v2 được merge vào `main` tại `08da03c`. Triển khai trên nhánh `phuc`, chỉ push
`phuc`. Case 6 và Case 7 thuộc bạn B: giữ nguyên phần `inspect_device.check`
và `search_kb.query` đã nhận từ main.

| Phiên bản | Phạm vi | Case eval liên quan |
|---|---|---|
| v1 — Routing | Phân biệt shared service, asset diagnostic, hướng dẫn KB và directory; gọi đủ nguồn được yêu cầu | H01–H04; phần chọn tool của H13, H15–H18 |
| v2 — Arguments | Chuẩn hóa và trích xuất check, category, environment; các tham số cụ thể | H05, H06; phần arguments của H03, H13, H15–H18 |
| v3 — Context & Clarify | Thiếu ID/thông tin gọi clarify; carry-over, correction, cancellation; đổi template báo cáo | H07, H10, H11, H19, H20; M01–M10 |
| Xác nhận trong v3 | Xác nhận action và payload thay đổi | H12, M05, M09; adversarial là bộ kiểm tra an toàn riêng |
| Kiểm tra hồi quy phạm vi | Ngoài helpdesk, câu hỏi về năng lực | H08, H09, H14 |

Các case có nhiều khía cạnh được phân theo **loại lỗi**, không sửa tất cả hành
vi trong một case chỉ vì case đó có phần routing. Ví dụ H13/H17 chọn đủ tool
thuộc v1, còn `check=vpn` thuộc v2. H19 chọn production/staging khi đã rõ thuộc
arguments; hỏi lại khi demo/QA mơ hồ thuộc v3.

Đối chiếu danh sách ghi chú ban đầu:

- Case 1: phân biệt lookup_user và inspect_device thuộc v1; format ID và hỏi
  lại khi thiếu ID để v2/v3. Khi triển khai phần đó, LT áp dụng cho laptop;
  vẫn giữ EMP lookup và asset DT/PR theo xác nhận của người dùng.
- Case 2 và 9 (M09): xét lượt cuối và ngữ cảnh thuộc v3.
- Case 3: thiếu thông tin gọi clarify thuộc v3.
- Case 4: xác nhận action để nhóm context/clarify và an toàn, không sửa ở v1.
- Case 5: hỏi rõ service/environment thiếu hoặc mơ hồ thuộc v3. Trạng thái
  thực tế là kết quả tool, không phải thông tin người dùng cần biết trước.
- Case 8 (H19): rule chung v3 cho mọi lựa chọn ngoài enum. Nếu schema chỉ có
  a/b/c nhưng người dùng chọn d, gọi clarify choice với tập hợp hợp lệ; không
  đoán lựa chọn gần nhất hoặc lấy lại giá trị cũ trước correction. Giữ nguyên
  các enum của v2; chỉ làm rõ hành vi hỏi lại qua prompt/description.
- Case 6: check trong tools.yaml thuộc v2, bạn B phụ trách.
- Case 7 (H17): bỏ query khỏi required do bạn B phụ trách; không sửa ở đây.

## Quy tắc lưu evidence

Các run trước khi chốt phân nhóm đã trộn routing, arguments và context.
Chúng được giữ nguyên trong `evidence/v1/` để truy vết lịch sử, nhưng **không
phải evidence cho v1 Routing**. Bảng log cũ được lưu riêng tại
`evidence/v1/mixed-scope-version-log.csv`. Không dùng kết quả 30/30 cũ để báo
điểm cho bản chỉ routing hiện tại.

V1 chỉ sửa routing. V2 của bạn B đã bổ sung required check và bỏ required query.
V3 bổ sung prompt về context, clarify và template; làm rõ description của
clarify, status, create_ticket và format_incident_report. Schema v3 yêu cầu
response_type để câu hỏi có kiểu rõ ràng; bỏ default production và yêu cầu
environment để tránh dùng mặc định thay cho việc hỏi lại. Giữ nguyên tất cả
enums và phần cấu trúc parameters của inspect_device/search_kb từ v2.
Đợt bổ sung Case 8 làm rõ description của inspect_device/check, nhưng không
đổi enum, default hay required của bạn B.

Điểm và giới hạn của v3 được ghi riêng trong [V3-REVIEW.md](V3-REVIEW.md).
Đợt đối chiếu Case 1–5/8/9 mới nhất: [V3-ENUM-REVIEW.md](V3-ENUM-REVIEW.md).
