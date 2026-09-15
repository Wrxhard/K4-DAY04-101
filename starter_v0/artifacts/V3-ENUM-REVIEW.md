# V3 — đối chiếu Case 1–5, 8 và 9

Đợt này bổ sung trên commit `24bc3e7`, nhánh `phuc`. Chỉ sửa prompt và
description để làm rõ context/clarify. Mọi enum, required, default và cấu
trúc schema giữ nguyên; không sửa phần Case 6/7 của bạn B hay agent loop.

| Ghi chú người dùng | Phân nhóm và xử lý |
|---|---|
| Case 1 | Routing và format ID thuộc v1/v2; hỏi lại khi thiếu ID thuộc v3. Giữ cách đã xác nhận: laptop dùng LT, directory dùng EMP, vẫn hỗ trợ DT/PR. Không ép người hỏi danh sách thiết bị theo EMP phải có LT. |
| Case 2 | V3: lượt cuối xác định nhiệm vụ; lịch sử chỉ cung cấp context còn hiệu lực. |
| Case 3 | V3: thiếu dữ liệu cần thiết gọi clarify rồi chờ, không bịa ID. Làm rõ thêm nguồn employee_id trong description. |
| Case 4 | V3 confirmation: hỏi yes_no cho payload trước action; không gọi create_ticket để hỏi xác nhận. |
| Case 5 | V3: thiếu service/environment phải clarify. Trạng thái thực tế là output của tool, không bắt user cung cấp. |
| Case 8 / H19 | V3: lựa chọn ngoài enum hoặc không thể ánh xạ chắc chắn thì clarify choice với các giá trị hợp lệ theo thứ tự schema. Không dùng giá trị gần nhất, default hoặc context cũ. |
| Case 9 / M09 | V3: correction thay giá trị cũ, payload đổi làm confirmation cũ mất hiệu lực; hỏi xác nhận mới. |

## Evidence mới nhất

Model `gpt-4o-mini`, provider `openai`, temperature 0.
Artifact: `v3+p6bc6638acb14+t8dfda9bdfe9e`.

| Kiểm tra | Kết quả |
|---|---:|
| Base | 27/30 |
| Routing | 30/30 |
| Nhóm v3 trong base: H07, H10–H12, H19–H20 và M01–M10 | 16/16 |
| Multi-turn | 10/10 |
| Enum mới: environment lạ, template lạ, check lạ, correction sang environment lạ | 4/4 |
| Bộ context/template trước đó, theo expected nguyên bản | 4/5 |
| Provider errors | 0 |

- [Base cuối](evidence/v3-enum/v3_B_base_openai_20260914T234759473590.json)
- [Enum cuối](evidence/v3-enum/v3_B_group_openai_20260914T234652192703.json)
- [Context cuối](evidence/v3-enum/v3_B_group_openai_20260914T234718165212.json)
- [Bộ enum bổ sung](eval_v3_enum_clarify.json)
- [Snapshot cuối](evidence/v3-enum/final/system_prompt.md)

H19, M09, missing-ID và xác nhận ticket đều pass trong base cuối. Ba lỗi
H03/H13/H17 còn lại là category/check arguments v2, không chỉnh trong đợt này.

Một case context V3T04 được chấm fail vì expected là clarify text, còn actual
là clarify choice với đủ dịch vụ hợp lệ. Review trace: agent hỏi đúng service
còn thiếu, không đoán và không gọi status. Giữ nguyên expected và công khai
4/5; không đổi test để biến lệch định dạng này thành PASS.

## Điều tra và sửa

Baseline rule enum đạt 2/4: template lạ bị hỏi nhầm findings, check lạ bị
ánh xạ thành hardware. Rule chung trong prompt chưa đủ: một lượt sau còn
truyền nguyên check không hợp lệ vào inspect_device. Vì vậy bổ sung guard
clarify tại description tool và parameter check; không thay tập giá trị enum.
Sau sửa, cả bốn case gọi clarify choice với tập hợp options đúng.

Các bản trước, attempts và kết quả thất bại được giữ nguyên trong
`evidence/v3-enum/`. Hash mỗi run khớp snapshot tương ứng. Bộ enum 4 case và
bộ context 5 case là supplemental, không phải team suite 10 case bắt buộc.

Kiểm tra schema bỏ qua description cho kết quả giống hệt bản trước đợt sửa;
registry/signature hợp lệ. Đã review final tool results: không có error hoặc
ticket được tạo. Không chạy lại adversarial trong đợt này; các điểm trên không
phải cam kết chống mọi tấn công hoặc đảm bảo model luôn có cùng hành vi.
