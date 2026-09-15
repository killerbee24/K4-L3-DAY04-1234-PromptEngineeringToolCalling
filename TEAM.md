# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Day04 K4-L3B IT Helpdesk.
- Người đại diện / MSSV: Vũ Văn Điền / 2A202602418.
- Tên repo: `K4-L3-DAY04-VuVanDien-2A202602418-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: `https://github.com/killerbee24/K4-L3-DAY04-VuVanDien-2A202602418-PromptEngineeringToolCalling`, branch `main`, commit chốt là HEAD của branch `main` khi nộp.
- Deadline áp dụng và link thông báo đổi hạn nếu có: Theo `SUBMISSION.md`.

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Vũ Văn Điền | 2A202602418 | KillerBee244 | Prompt Engineering & Experiment Lead: phân tích v0, cải tiến v1-v3, chạy base/group/adversarial, ghi version log và report evidence | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/`; commits `c79a568`, `f48b383` |
| Đinh Văn Bình | 2A202602830 | binhdinhvan | Evaluation, Safety & Report: viết eval group, chuẩn bị report, phân tích adversarial và kiểm tra safety | `starter_v0/data/eval_group.json`, `starter_v0/artifacts/REPORT.md`; commit `fb17324` |
| Phạm Xuân Quý | 2A202602745 | quycute2003 | Backend integration & Bonus tools: service layer, unit tests, transcript/eval bonus, three read-only tools | `starter_v0/app_service.py`, `starter_v0/tests/`, `starter_v0/tools/`, `starter_v0/data/eval_bonus.json`; commit `b413f4f` |
| Ngô Đinh Minh Nhật | 2A202602569 | minhnhatuet | Frontend/UI: Streamlit chat UI, provider/model/version display, tool trace, transcript download, demo transcripts | `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/transcripts/`; commit `c6cc594` |

## Nhận xét chung

- Kết quả và bằng chứng: Base v0 hợp lệ đạt 21/30, sau v1-v3 đạt 30/30; group eval đạt 9/10; adversarial eval đạt 12/12. Evidence chính nằm trong `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/`, `starter_v0/transcripts/` và `starter_v0/artifacts/REPORT.md`.
- Thay đổi hiệu quả nhất: Prompt v1-v3 thêm ranh giới không tự đoán ID/môi trường, xác nhận trước write action, latest-intent-wins và guard không gửi dữ liệu nội bộ ra external search.
- Giới hạn còn lại: Group case `G09_cancel_ticket_request` còn fail vì model gọi `search_kb` sau khi người dùng hủy ticket và hỏi self-help; không có write action hay exfiltration.
- Cách phân công và tích hợp: Diện phụ trách prompt/eval/version log; Bình phụ trách eval group và safety/report; Quý phụ trách backend/bonus tools/test; Nhật phụ trách UI và transcript. Nhóm tích hợp qua branch `main` và chỉ dùng run có `provider_error_cases == 0`.

## INDIVIDUAL

### Vũ Văn Điền — 2A202602418

- Phần việc và file/commit/PR: Phụ trách Prompt Engineering & Experiment Lead; phân tích 9 lỗi v0 theo `wrong_tool`, `missing_info`, `wrong_boundary`; cập nhật `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`; chạy và ghi evidence base v1-v3, group và adversarial trong `starter_v0/runs/`; thêm dry-run guard cho ticket ở `starter_v0/run_eval.py` và `starter_v0/tools/create_ticket/tool.py`. Commit kỹ thuật: `c79a568`, `f48b383`.
- Quyết định, khó khăn và cách xử lý: Không hard-code case ID hay wording eval trong prompt; thay vào đó thêm rule tổng quát cho prerequisite, confirmation boundary, latest-intent-wins, multi-source routing và external-search privacy. Khi adversarial run từng tạo mock ticket file, chuyển safety eval sang dry-run để giữ trace thật nhưng không sinh side effect.
- Điều đã học: Accuracy chỉ có ý nghĩa khi provider run hợp lệ; ngoài score còn phải đọc actual calls, arguments, tool results và filesystem side effects.
- AI/công cụ đã dùng và cách kiểm tra: Dùng Codex hỗ trợ đọc rubric, chỉnh prompt/tool declaration và tổng hợp evidence; tự kiểm tra bằng các run có `provider_error_cases == 0`, `measured_cases == total_cases`, `py_compile`, unit test và review thủ công các case B2/B4a.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Cập nhật sau khi tự nộp URL repo chung.

### Phạm Xuân Quý — 2A202602745

- Phần việc và file/commit/PR: Xây backend `starter_v0/app_service.py`; kết nối backend với Streamlit trong `starter_v0/app.py`; viết `starter_v0/tests/test_app_service.py`; xây ba tool read-only `check_software_approval`, `lookup_ticket_status`, `check_maintenance_window` cùng dữ liệu giả lập và `starter_v0/tests/test_bonus_tools.py`; viết bộ `starter_v0/data/eval_bonus.json` và evidence `starter_v0/analysis/bonus_tools.md`. Commit kỹ thuật: `b413f4f` (`Add backend integration and helpdesk bonus tools`).
- Quyết định, khó khăn và cách xử lý: Tách logic provider/agent/history/transcript khỏi giao diện thành `HelpdeskAppService` để frontend chỉ phụ trách hiển thị. Các tool mở rộng được thiết kế read-only để tránh side effect, trả lỗi rõ ràng cho dữ liệu không tồn tại và dùng chung cơ chế Tool Trace. Kết quả tự kiểm tra: 9/9 unit/backend test PASS, bonus eval 5/6 và base regression với artifact bonus đạt 30/30; failure còn lại đã ghi trong `analysis/bonus_tools.md`.
- Điều đã học: Backend cho UI agent nên tách rõ state hội thoại, provider call, tool execution và transcript để frontend hiển thị đúng hành vi thật mà không phải tự suy diễn trace.
- AI/công cụ đã dùng và cách kiểm tra: Dùng OpenAI Codex để hỗ trợ đọc yêu cầu, triển khai backend/tool, viết test và phân tích run; dùng OpenAI `gpt-4o-mini` cho eval. Tự kiểm tra bằng `py_compile`, 9 unit/backend test, Streamlit AppTest không có exception, health endpoint HTTP 200, smoke test OpenAI gọi `check_service_status`, run bonus và run base regression. Không dùng AI để bịa run, metric, transcript hoặc commit.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Cập nhật sau khi tự nộp URL repo chung.

### Đinh Văn Bình — 2A202602830

- Phần việc và file/commit/PR: Viết đúng 10 case đánh giá của nhóm trong `starter_v0/data/eval_group.json`, gồm 5 single-turn và 5 multi-turn; chuẩn bị bảng B3, danh sách tool và checklist safety trong `starter_v0/artifacts/REPORT.md`. Commit kỹ thuật: `fb17324` (`Add team evaluation cases and safety report scaffold`).
- Quyết định, khó khăn và cách xử lý: Thiết kế các case tập trung vào routing tool, argument môi trường, thiếu asset ID/service, hủy yêu cầu và xác nhận trước khi tạo ticket. Expected tool chỉ dùng các tool đang được declaration và implementation hiện có; không tự tạo metric hoặc evidence khi chưa có run group/adversarial hợp lệ.
- Điều đã học: Bộ eval cần tách rõ expected behavior khỏi kết quả runtime; automatic score không đủ để kết luận safety nếu chưa kiểm tra tool result và filesystem.
- AI/công cụ đã dùng và cách kiểm tra: Dùng công cụ hỗ trợ đọc schema, đối chiếu `run_eval.py`, kiểm tra JSON hợp lệ, xác nhận đủ 10 case với tỷ lệ 5 single-turn/5 multi-turn và kiểm tra `git diff --check`. Evidence group/adversarial đã được cập nhật bằng run OpenRouter hợp lệ trong `REPORT.md`.
- Trạng thái còn lại: Group run còn 1 case fail (`G09_cancel_ticket_request`), đã ghi trung thực trong B2/B3/B7; các mục MSSV/GitHub/evidence chính đã bổ sung.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Cập nhật sau khi tự nộp URL repo chung.

### Ngô Đinh Minh Nhật — 2A202602569

- Phần việc và file/commit/PR: Phụ trách Frontend/UI; xây giao diện chat Streamlit trong `starter_v0/app.py`, hiển thị provider/model/artifact version, lịch sử nhiều lượt, tool call theo vòng, arguments, result/error, trạng thái chờ người dùng, nút phiên mới và tải transcript JSON. Commit kỹ thuật: `c6cc594` và phần UI polish trong commit tích hợp cuối.
- Quyết định, khó khăn và cách xử lý: UI dùng `HelpdeskAppService` để hiển thị trace thật từ backend thay vì dựng dữ liệu minh họa; tool error được render trực tiếp, transcript chỉ chứa metadata và hội thoại, không hiển thị API key.
- Điều đã học: Một UI demo agent tốt phải cho người xem thấy lý do agent hành động: gọi tool nào, input gì, output ra sao, đang chờ xác nhận hay đã đủ điều kiện thực hiện.
- AI/công cụ đã dùng và cách kiểm tra: Dùng Codex hỗ trợ rà rubric UI, chỉnh giao diện và kiểm tra bằng `py_compile`, unit test `tests.test_app_service`, Streamlit local health check và transcript demo trong `starter_v0/transcripts/`.
- Thời điểm đã tự nộp URL repo chung trên VLearn: Cập nhật sau khi tự nộp URL repo chung.
