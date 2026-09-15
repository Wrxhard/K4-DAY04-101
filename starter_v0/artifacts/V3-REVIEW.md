# V3 — Context & Clarify

> Báo cáo này ghi kết quả tại commit 24bc3e7. Đợt bổ sung rule chung cho enum
> ngoài lựa chọn được ghi trong [V3-ENUM-REVIEW.md](V3-ENUM-REVIEW.md);
> không dùng điểm dưới đây thay cho kết quả của artifact mới.

V3 được phát triển trên nhánh `phuc`, từ v2 đã merge vào `main` tại `08da03c`.
Giữ nguyên declaration của `inspect_device` và `search_kb`, gồm hai thay đổi
của bạn B: required `check` và bỏ required `query`. Không sửa runtime hoặc
bộ eval cố định.

## Kết quả đo

Provider: `openai`, model: `gpt-4o-mini`, temperature: 0.

| Phạm vi / metric | V2 trên main | V3 cuối |
|---|---:|---:|
| Toàn bộ base | 23/30 | 27/30 |
| Routing accuracy | 0.8333 | 1.0000 |
| Argument accuracy | 0.7667 | 0.9000 |
| Multi-turn | 8/10 | 10/10 |
| Nhóm v3 trong base | 11/16 | 16/16 |
| Bộ bổ sung context/template | Chưa đo | 5/5 |
| Provider errors | 0 | 0 |

Nhóm v3 gồm H07, H10, H11, H12, H19, H20 và M01–M10. Các điểm nhóm được
tính từ cùng run base, không phải bộ expected khác. Tất cả case trong mỗi run
đều được đo. Đây là evidence của lần chạy, không đảm bảo model luôn lặp lại
cùng kết quả.

- [Run v2 từ main](evidence/v2-main/v2_B_base_openai_20260914T233056387420.json)
- [Run base v3 cuối](evidence/v3/v3_B_base_openai_20260914T234002732456.json)
- [Run bổ sung v3 cuối](evidence/v3/v3_B_group_openai_20260914T233927577254.json)
- [Prompt cuối](evidence/v3/final/system_prompt.md)
- [Schema cuối](evidence/v3/final/tools.yaml)
- [Bộ bổ sung](eval_v3_context.json)

Artifact cuối: `v3+pe4245255ece0+tfb01eb4f33de`.

## Những thay đổi thuộc v3

- Lượt cuối quyết định nhiệm vụ. Lịch sử chỉ cung cấp ngữ cảnh còn hiệu lực;
  correction thay giá trị cũ, cancellation hoặc đổi intent thay nhiệm vụ cũ.
- Giữ ID, environment, chủ đề, hệ điều hành, findings và report settings khi
  chúng vẫn liên quan. Không gọi lại nhiệm vụ đã bị hủy hoặc thay thế.
- Thiếu ID dùng clarify text. Laptop Wi-Fi thiếu mã máy phải hỏi asset ID,
  không hỏi environment của dịch vụ dùng chung.
- Thiếu hoặc mơ hồ service/environment phải hỏi lại; đủ thông tin thì đọc trực
  tiếp. Service status là kết quả tool, không bắt user biết trước.
- Tạo ticket cần clarify yes_no với payload đã tóm tắt. Payload thay đổi làm
  xác nhận cũ mất hiệu lực; không gọi create_ticket để hỏi xác nhận.
- Đổi template dùng lại findings và title, trừ khi user sửa title. Không tự
  fetch lại hay tạo ticket; thiếu findings thì clarify.
- Description được làm rõ cho clarify, status, ticket và report. Schema yêu
  cầu response_type; environment không còn default production và trở thành
  required, để model không dùng mặc định thay cho câu hỏi làm rõ.

Tất cả enum giữ nguyên. Declaration của inspect_device, search_kb, lookup_user,
policy và search_device_info giữ nguyên so với snapshot v2.

## Lỗi còn lại thuộc arguments v2

| Case | Hành vi chưa đúng ở run cuối |
|---|---|
| H03 | Chọn đúng search_kb nhưng category không đúng email |
| H13 | Chọn đủ status/device nhưng check=all thay vì vpn |
| H17 | Chọn đủ ba nguồn nhưng check=all thay vì vpn |

Evaluator gắn failure_type theo nhãn của case; cả ba observed mismatch thực
tế đều là wrong_arg_value. Không sửa phần check/category của bạn B để đẩy
điểm toàn bộ base lên 30/30 trong công việc v3 này.

## Kiểm chứng và giới hạn

- Kiểm tra schema/registry/signature và git diff whitespace đã qua.
- Hash của mỗi run mới khớp một snapshot đã lưu. Giữ cả các lần thất bại,
  không thay thế run cũ bằng run thành công.
- Review tool results của base và bộ bổ sung cuối: không có error và không
  tạo ticket. Hai case template cuối giữ title đúng và findings đã có.
- Bộ bổ sung có 5 case, được gắn suite=group do CLI hỗ trợ nhãn đó; đây **không
  phải** bộ team eval 10 case bắt buộc của lab.
- Fixture đổi template ở revision 1 dùng dấu hai chấm khiến ranh giới title
  và findings không rõ với model. Revision 2 tách `incident_title` và findings
  rõ ràng. Input cũ và kết quả cũ vẫn nằm trong attempt1/attempt2; không so
  điểm bổ sung hai revision như cùng một dataset. Bộ base không thay đổi.
- Chưa chạy lại adversarial cho v3 này. Không dùng điểm adversarial của các
  bản v1 trộn phạm vi để tuyên bố v3 an toàn. Runtime vẫn tin boolean confirmed
  từ model, chưa có kiểm soát xác nhận độc lập với model.
- Hai ticket mock do đo baseline v2 tạo ra đã được chuyển sang thư mục local
  ignored `analysis/v3-generated-tickets/`. Không đưa tickets hoặc .env lên git.

## Chạy lại

Từ `starter_v0`, dùng môi trường provider đã cấu hình:

```powershell
python run_eval.py --provider openai --model gpt-4o-mini --version v3 --suite base --runs-dir artifacts/evidence/v3
python run_eval.py --provider openai --model gpt-4o-mini --version v3 --suite group --eval-cases artifacts/eval_v3_context.json --runs-dir artifacts/evidence/v3
```
