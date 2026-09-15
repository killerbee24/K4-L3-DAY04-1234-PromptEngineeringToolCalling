# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm:
- Người đại diện / MSSV:
- Tên repo: `K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt:
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| | | | | |

## Nhận xét chung

- Kết quả và bằng chứng:
- Thay đổi hiệu quả nhất:
- Giới hạn còn lại:
- Cách phân công và tích hợp:

## INDIVIDUAL

### Phạm Xuân Quý — 2A202602745

- Phần việc và file/commit/PR: Xây backend `starter_v0/app_service.py`; kết nối backend với Streamlit trong `starter_v0/app.py`; viết `starter_v0/tests/test_app_service.py`; xây ba tool read-only `check_software_approval`, `lookup_ticket_status`, `check_maintenance_window` cùng dữ liệu giả lập và `starter_v0/tests/test_bonus_tools.py`; viết bộ `starter_v0/data/eval_bonus.json` và evidence `starter_v0/analysis/bonus_tools.md`. Commit kỹ thuật: `b413f4f` (`Add backend integration and helpdesk bonus tools`).
- Quyết định, khó khăn và cách xử lý: Tách logic provider/agent/history/transcript khỏi giao diện thành `HelpdeskAppService` để frontend chỉ phụ trách hiển thị. Các tool mở rộng được thiết kế read-only để tránh side effect, trả lỗi rõ ràng cho dữ liệu không tồn tại và dùng chung cơ chế Tool Trace. Kết quả tự kiểm tra: 9/9 unit/backend test PASS, bonus eval 5/6 và base regression với artifact bonus đạt 30/30; failure còn lại đã ghi trong `analysis/bonus_tools.md`.
- Điều đã học: Sinh viên tự bổ sung phần reflection sau khi hoàn thành và tự kiểm tra công việc.
- AI/công cụ đã dùng và cách kiểm tra: Dùng OpenAI Codex để hỗ trợ đọc yêu cầu, triển khai backend/tool, viết test và phân tích run; dùng OpenAI `gpt-4o-mini` cho eval. Tự kiểm tra bằng `py_compile`, 9 unit/backend test, Streamlit AppTest không có exception, health endpoint HTTP 200, smoke test OpenAI gọi `check_service_status`, run bonus và run base regression. Không dùng AI để bịa run, metric, transcript hoặc commit.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa nộp; cập nhật thời điểm thực tế sau khi tự nộp và mở lại URL để kiểm tra.
