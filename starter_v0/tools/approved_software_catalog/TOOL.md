---
name: approved_software_catalog
track: bonus
kind: local_catalog
provider: mock_software_catalog
requires_env: []
inputs: [query, category]
outputs: [query, category, count, results, trust_boundary]
side_effect: false
---
# approved_software_catalog

Tra cứu danh mục phần mềm được phê duyệt, hạn chế hoặc cấm sử dụng tại Northstar Labs.
Cho biết trạng thái phê duyệt (approved, restricted, prohibited), phiên bản mới nhất,
và quy trình xin cấp phép / cài đặt (self_service vs it_managed).
