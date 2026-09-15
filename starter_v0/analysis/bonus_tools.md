# Bonus tool evidence — v3_bonus

- Phụ trách triển khai: Phạm Xuân Quý — 2A202602745
- Phạm vi cá nhân: backend integration, ba bonus tool read-only, unit test và bonus evidence; không bao gồm thí nghiệm prompt core v0–v3.

## Phạm vi mở rộng

Ba tool read-only dùng dữ liệu giả lập đã được thêm sau khi chốt chuỗi thí nghiệm core v0–v3:

| Tool | Chức năng | Side effect |
|---|---|---|
| `check_software_approval` | Kiểm tra phần mềm/phiên bản theo hệ điều hành trong approved catalog | Không |
| `lookup_ticket_status` | Tra cứu trạng thái một ticket giả lập bằng ticket ID | Không |
| `check_maintenance_window` | Tra lịch bảo trì của một dịch vụ và môi trường | Không |

Artifact: `v3_bonus+pd0ce0d8719ee+t3896d84f4932`.

## Kiểm thử

- Unit/backend tests: 9/9 PASS.
- Registry và declaration: 12/12 tên tool khớp nhau.
- Bonus eval: 5/6 PASS; `provider_error_cases=0`; `measured_cases=6/6`.
- Base regression: 30/30 PASS; `provider_error_cases=0`; `measured_cases=30/30`.

Evidence:

- `runs/v3_bonus_B_extension_openai_20260915T195530474118.json`
- `runs/v3_bonus_B_base_openai_20260915T195623114865.json`
- `data/eval_bonus.json`
- `tests/test_bonus_tools.py`

## Failure còn lại

- `B06_missing_software_os`: yêu cầu không nêu hệ điều hành nhưng agent tự điền `Windows 11` thay vì dùng `clarify`. Tool implementation không có side effect, tuy nhiên đây vẫn là lỗi `missing_info` cần ghi trung thực.

## Safety

- Cả ba tool chỉ đọc JSON cục bộ và không gọi web.
- Dữ liệu ticket, phần mềm và lịch bảo trì đều là dữ liệu giả lập cố định.
- ID hoặc phần mềm không tồn tại trả lỗi rõ ràng; không tự tạo record.
- Không tool nào cài phần mềm, thay đổi ticket hoặc lên lịch bảo trì.
- UI hiển thị các tool qua trace chung, gồm arguments và result/error.
