# Hướng dẫn điền contribution và self-reflection vào REPORT.md

Tài liệu này giúp từng thành viên bổ sung phần đóng góp cá nhân vào đúng file nộp bài:
`starter_v0/artifacts/REPORT.md`.

Không tạo report cá nhân mới. Không sửa hoặc xóa phần của thành viên khác. Mỗi thành
viên chỉ bổ sung một mục con của mình trong **C2. Self-reflection của từng thành viên**,
sau đó tự kiểm tra và commit bằng Git identity của chính mình.

## 1. Thông tin cần chuẩn bị

Mỗi thành viên chuẩn bị các thông tin sau:

- Họ tên, MSSV và GitHub username.
- Vai trò hoặc phần việc được nhóm phân công.
- Branch đã làm việc và các commit do chính mình tạo.
- File, test case, evidence hoặc artifact mình trực tiếp tạo hay chỉnh sửa.
- Một quyết định kỹ thuật quan trọng và lý do chọn cách làm đó.
- Khó khăn thực tế, cách xử lý và điều đã học được.
- Một điều sẽ cải thiện nếu làm lại.

Nếu chưa xác minh được thông tin nào, ghi `TBD` và hỏi lại nhóm. Không suy đoán MSSV,
không nhận commit của người khác và không tự gán kết quả test chung thành đóng góp cá nhân.

## 2. Quy trình nhanh

### Bước 1 — Đồng bộ an toàn

Đứng tại thư mục repository và kiểm tra trạng thái trước:

```powershell
git status --short
git branch --show-current
```

Nếu đang có thay đổi chưa commit, không chạy lệnh có thể ghi đè chúng. Commit phần việc
đang làm hoặc trao đổi với nhóm trưởng trước khi đồng bộ branch.

### Bước 2 — Tìm commit của chính mình

Xem Git identity đang dùng:

```powershell
git config user.name
git config user.email
```

Tìm lịch sử theo tên hoặc email của mình:

```powershell
git log --all --author="TEN_HOAC_EMAIL_CUA_BAN" --date=short --pretty=format:"%h | %ad | %an | %s"
```

Kiểm tra một commit trước khi đưa vào report:

```powershell
git show --stat COMMIT_HASH
git show --name-status COMMIT_HASH
```

Chỉ liệt kê commit mà bạn thực sự thực hiện. Merge commit chỉ nên ghi nếu bạn là người
phụ trách PR/merge đó và điều này có ý nghĩa với phần đóng góp.

### Bước 3 — Kiểm tra nguồn phân công và bằng chứng

Đối chiếu tối thiểu các nguồn sau nếu có:

- `TEAMMATES.md`: họ tên, MSSV, username và vai trò chính thức.
- File phân công `Tong_hop_loi_va_PIC_5_nguoi_cap_nhat.xlsx` của nhóm.
- `starter_v0/artifacts/REPORT.md`: nội dung chung và số liệu đã được thống nhất.
- `starter_v0/artifacts/version_log.csv`: các phiên bản và kết quả eval.
- `starter_v0/artifacts/evidence/`: run, transcript hoặc summary liên quan.
- Git diff của từng commit: bằng chứng về file và thay đổi thực tế.

Một kết quả nhóm như `10/10` chỉ được nhắc trong reflection cá nhân khi nói rõ vai trò
của bạn, ví dụ “tôi thiết kế case”, “tôi chạy regression” hoặc “tôi sửa nguyên nhân làm
case fail”. Không viết “tôi làm hệ thống đạt 10/10” nếu kết quả đến từ nhiều người.

### Bước 4 — Thêm đúng một mục trong C2

Mở `starter_v0/artifacts/REPORT.md`, tìm:

```markdown
## C2. Self-reflection của từng thành viên
```

Thêm nội dung theo mẫu sau, bên dưới các thành viên đã có:

```markdown
### HO_TEN (`GITHUB_USERNAME`) — MSSV: MA_SO_SINH_VIEN

- **Vai trò/phần việc được nhận:** ...
- **Những gì tôi đã thay đổi trong repo chung:** ...
- **File hoặc artifact liên quan:** `path/to/file`, `path/to/evidence`.
- **Commit hash hoặc pull request:** `abc1234`, PR #N.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** ...
- **Khó khăn tôi gặp và cách tôi xử lý:** ...
- **Điều tôi học được từ phần việc này:** ...
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** ...
```

Nên viết ngôi thứ nhất (`tôi`), cụ thể và ngắn gọn. Mỗi ý cần gắn với hành động hoặc
bằng chứng có thể kiểm tra, thay vì chỉ viết “hoàn thành tốt nhiệm vụ”.

### Bước 5 — Xem lại thay đổi trước khi commit

```powershell
git diff -- starter_v0/artifacts/REPORT.md
git diff --check
```

Tự kiểm tra:

- Chỉ mục C2 của mình được thay đổi.
- Tên, MSSV và username đúng với `TEAMMATES.md`.
- Commit hash tồn tại và đúng tác giả.
- Đường dẫn file/evidence tồn tại trong repo.
- Không có API key, token, mật khẩu, dữ liệu thật hoặc nội dung bí mật.
- Không sửa số liệu chung nếu chưa được nhóm thống nhất.
- Không đánh dấu checklist “mọi thành viên hoàn tất” khi nhóm chưa xác nhận.

Sau khi review diff, thành viên tự commit bằng Git identity của mình:

```powershell
git add starter_v0/artifacts/REPORT.md
git commit -m "docs(report): add self-reflection for TEN_THANH_VIEN"
```

## 3. Prompt copy-paste cho Codex hoặc ChatGPT

Thay các giá trị trong `<...>` trước khi gửi. Nên chạy AI tại thư mục repository để AI
có thể đọc lịch sử Git và file bằng chứng.

```text
Bạn đang hỗ trợ tôi bổ sung self-reflection vào báo cáo nộp bài của nhóm.

Thông tin của tôi:
- Họ tên: <HO_TEN>
- MSSV: <MSSV hoặc TBD>
- GitHub username: <USERNAME>
- Git author name/email có thể dùng để lọc: <GIT_NAME_OR_EMAIL>
- Vai trò được phân công: <VAI_TRO hoặc yêu cầu tự đối chiếu từ nguồn trong repo>

Mục tiêu:
Điền phần self-reflection của riêng tôi vào mục
"## C2. Self-reflection của từng thành viên" trong
"starter_v0/artifacts/REPORT.md".

Nguồn phải kiểm tra trước khi viết:
1. Đọc README và cấu trúc hiện tại của starter_v0/artifacts/REPORT.md.
2. Đọc TEAMMATES.md và file phân công Tong_hop_loi_va_PIC_5_nguoi_cap_nhat.xlsx nếu có.
3. Dùng git log --all --author để tìm commit đúng Git identity của tôi.
4. Dùng git show --stat hoặc git show --name-status để xác minh từng commit được nhắc.
5. Đối chiếu các file, version_log.csv và evidence liên quan trước khi nêu kết quả test.

Quy tắc bắt buộc:
- Không tạo một report cá nhân khác; file nộp duy nhất cần sửa là REPORT.md nói trên.
- Chỉ thêm hoặc cập nhật mục con mang tên tôi trong C2.
- Không sửa phần chung, số liệu nhóm, checklist hoặc reflection của thành viên khác.
- Không nhận commit hay công việc của người khác là của tôi.
- Không bịa họ tên, MSSV, vai trò, commit, PR, file, test result hoặc quyết định kỹ thuật.
- Nếu thông tin chưa xác minh được, ghi "TBD" hoặc nêu rõ "chưa xác minh".
- Phân biệt rõ đóng góp cá nhân với kết quả chung của nhóm.
- Viết bằng tiếng Việt, ngôi thứ nhất, cụ thể, trung thực và súc tích.
- Giữ nguyên encoding UTF-8 và Markdown hiện có.
- Không tự commit, push, merge hoặc pull nếu tôi chưa yêu cầu.

Mục của tôi phải có đúng các ý:
1. Vai trò/phần việc được nhận.
2. Những gì tôi đã thay đổi trong repo chung.
3. File hoặc artifact liên quan.
4. Commit hash hoặc pull request.
5. Một quyết định kỹ thuật tôi đã đưa ra và lý do.
6. Khó khăn tôi gặp và cách tôi xử lý.
7. Điều tôi học được từ phần việc này.
8. Nếu làm lại, tôi sẽ cải thiện điều gì.

Trước khi sửa file:
- Tóm tắt bằng chứng tìm được thành bảng gồm: claim, commit, file/evidence và mức xác minh.
- Chỉ ra thông tin nào còn thiếu hoặc mâu thuẫn.
- Cho tôi xem bản nháp self-reflection và chờ tôi xác nhận.

Sau khi tôi xác nhận bản nháp:
- Chèn nội dung vào đúng mục C2.
- Chạy git diff --check.
- Hiển thị git diff chỉ cho starter_v0/artifacts/REPORT.md.
- Báo rõ những kiểm tra đã chạy và mọi thông tin vẫn còn TBD.
```

## 4. Prompt ngắn khi đã biết rõ commit của mình

```text
Hãy đọc starter_v0/artifacts/REPORT.md và kiểm tra các commit sau bằng git show:
<DANH_SACH_COMMIT_CUA_TOI>.

Soạn một mục self-reflection bằng tiếng Việt cho:
<HO_TEN> (`<GITHUB_USERNAME>`) — MSSV: <MSSV>.

Dùng đúng 8 ý trong phần C2 hiện tại. Chỉ sử dụng thông tin được xác minh từ commit,
file và evidence trong repo; phần chưa rõ ghi TBD. Phân biệt đóng góp cá nhân với kết
quả chung của nhóm. Không sửa phần người khác, không đổi số liệu chung và không tạo file
report mới. Trước tiên cho tôi xem bản nháp; chỉ sửa REPORT.md sau khi tôi xác nhận.
```

## 5. Ví dụ cách viết có bằng chứng

Không nên viết:

> Tôi phụ trách test và đã giúp nhóm hoàn thành bài rất tốt.

Nên viết:

> Tôi thiết kế năm multi-turn case trong `data/eval_group.json` để kiểm tra correction,
> cancellation và carry-over context. Tôi chạy lại suite group, lưu evidence tại
> `starter_v0/artifacts/evidence/...` và đối chiếu actual tool calls với expected behavior. Kết quả
> 10/10 là kết quả của artifact chung; phần đóng góp trực tiếp của tôi là thiết kế case,
> thực thi regression và ghi nhận mismatch để các thành viên phụ trách fix xử lý.

## 6. Checklist dành cho nhóm trưởng

Trước khi đánh dấu C3 hoàn tất, nhóm trưởng kiểm tra:

- Đủ năm mục self-reflection và đủ thông tin trong `TEAMMATES.md`.
- Mỗi reflection được chính thành viên đó review và commit.
- Commit/file/evidence được dẫn đúng, không trùng hoặc nhận nhầm ownership.
- Các con số trong reflection khớp với phần B của report.
- `git diff --check` không báo lỗi và Markdown vẫn đọc được.
- File nộp vẫn là `starter_v0/artifacts/REPORT.md`.
