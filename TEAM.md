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
| Đinh Văn Bình | Chưa bổ sung | Chưa bổ sung | Evaluation, Safety & Report: viết eval group, chuẩn bị report, phân tích adversarial và kiểm tra safety | `starter_v0/data/eval_group.json`, `starter_v0/artifacts/REPORT.md`; commit `fb17324` |

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

### Đinh Văn Bình

- Phần việc và file/commit/PR: Viết đúng 10 case đánh giá của nhóm trong `starter_v0/data/eval_group.json`, gồm 5 single-turn và 5 multi-turn; chuẩn bị bảng B3, danh sách tool và checklist safety trong `starter_v0/artifacts/REPORT.md`. Commit kỹ thuật: `fb17324` (`Add team evaluation cases and safety report scaffold`).
- Quyết định, khó khăn và cách xử lý: Thiết kế các case tập trung vào routing tool, argument môi trường, thiếu asset ID/service, hủy yêu cầu và xác nhận trước khi tạo ticket. Expected tool chỉ dùng các tool đang được declaration và implementation hiện có; không tự tạo metric hoặc evidence khi chưa có run group/adversarial hợp lệ.
- Điều đã học: Bộ eval cần tách rõ expected behavior khỏi kết quả runtime; automatic score không đủ để kết luận safety nếu chưa kiểm tra tool result và filesystem.
- AI/công cụ đã dùng và cách kiểm tra: Dùng công cụ hỗ trợ đọc schema, đối chiếu `run_eval.py`, kiểm tra JSON hợp lệ, xác nhận đủ 10 case với tỷ lệ 5 single-turn/5 multi-turn và kiểm tra `git diff --check`. Không dùng AI để bịa metric, transcript hoặc safety evidence.
- Trạng thái còn lại: Cần chạy group/adversarial trên artifact v3, phân tích ít nhất 3 adversarial case và điền evidence thật vào B4/B4a/B6/B7. Cần bổ sung MSSV, GitHub username và thời điểm nộp VLearn.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Chưa nộp; cập nhật thời điểm thực tế sau khi tự nộp và mở lại URL để kiểm tra.
