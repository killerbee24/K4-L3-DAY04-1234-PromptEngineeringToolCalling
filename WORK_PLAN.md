# Kế hoạch phân công nhóm — Day04 Prompt Engineering & Tool Calling

## 1. Mục tiêu chung

Hoàn thiện IT Helpdesk Agent từ baseline v0 đến v3, có bộ đánh giá cố định, kiểm thử an toàn, giao diện chat, transcript và báo cáo đầy đủ. Mọi kết luận trong report phải dẫn tới run, transcript, file hoặc commit thật.

Baseline đã chạy bằng OpenAI:

- Provider: `openai`
- Model: `gpt-4o-mini`
- Kết quả: 21/30 case PASS
- `case_accuracy`: 0.70
- `provider_error_cases`: 0
- `measured_cases`: 30/30
- Run: `starter_v0/runs/v0_B_base_openai_20260915T184035130046.json`

## 2. Nguyên tắc phối hợp

- Bốn thành viên làm song song theo vùng file riêng để hạn chế merge conflict.
- Các vòng v1, v2 và v3 phải chạy tuần tự vì mỗi vòng cần một giả thuyết, một thay đổi chính và kết quả của vòng trước.
- Không sửa `starter_v0/data/eval_base.json` hoặc đáp án cố định để tăng điểm.
- Chỉ dùng dữ liệu giả lập; không commit `.env`, API key, `.venv`, cache hoặc `tickets/`.
- Mỗi thành viên tự viết và commit mục `INDIVIDUAL` của mình trong `TEAM.md`.
- Một run chỉ được dùng làm evidence khi `provider_error_cases == 0` và `measured_cases == total_cases`.

## 3. Phân công bốn thành viên

### Thành viên 1 — Vũ Văn Diện (nhóm trưởng)

**Vai trò:** Prompt Engineering & Experiment Lead

**File sở hữu:**

- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/artifacts/tools.yaml`
- `starter_v0/artifacts/version_log.csv`
- Các run base v1, v2 và v3 trong `starter_v0/runs/`

**Công việc:**

1. Phân tích 9 case thất bại của v0 theo nhóm `wrong_tool`, `missing_info` và `wrong_boundary`.
2. Thực hiện v1 với giả thuyết về điều kiện tiên quyết: không tự đoán ID/môi trường và phải hỏi lại hoặc xác nhận khi cần.
3. Thực hiện v2 dựa trên lỗi còn lại, ưu tiên mô tả tool và quy ước argument.
4. Thực hiện v3 dựa trên lỗi còn lại, ưu tiên hội thoại nhiều lượt, sửa/hủy và hiệu lực xác nhận.
5. Ghi đủ hash, lý do, giả thuyết, metric trước/sau và đường dẫn run vào `version_log.csv`.
6. Không hard-code case ID hoặc chép nguyên wording của eval vào prompt.

**Bằng chứng bàn giao:**

- Run base hợp lệ cho v1, v2 và v3.
- `version_log.csv` có đủ bốn dòng v0–v3.
- Bảng failure analysis cho các case tiêu biểu.

### Thành viên 2 — Phạm Xuân Quý

**Vai trò:** Backend & Agent Integration

**File sở hữu dự kiến:**

- `starter_v0/app_service.py`
- `starter_v0/tests/test_app_service.py`
- `starter_v0/helpdesk_data/approved_software.json`
- `starter_v0/tools/check_software_approval/TOOL.md`
- `starter_v0/tools/check_software_approval/tool.py`
- `starter_v0/helpdesk_data/ticket_status.json`
- `starter_v0/tools/lookup_ticket_status/`
- `starter_v0/helpdesk_data/maintenance_windows.json`
- `starter_v0/tools/check_maintenance_window/`
- `starter_v0/tests/test_bonus_tools.py`
- Tài liệu chạy backend hoặc phần backend trong README của UI

**Công việc:**

1. Tái sử dụng `run_model_tool_loop()` trong `starter_v0/chat.py`; không viết lại provider hoặc tool registry.
2. Xây service quản lý session, history và từng lượt hội thoại.
3. Trả về đầy đủ nội dung để frontend hiển thị:
   - câu trả lời của agent;
   - trạng thái `answered`, `waiting_for_user` hoặc `error`;
   - các vòng gọi model;
   - tên tool, arguments, result/error;
   - provider, model và artifact version.
4. Lưu transcript JSON thật sau mỗi lượt chat.
5. Thêm kiểm thử cho session, history, trạng thái chờ xác nhận và cấu trúc transcript.
6. Hỗ trợ frontend tích hợp qua interface đã thống nhất.
7. Sau khi backend cơ bản ổn định, xây ba tool mở rộng read-only cùng dữ liệu giả lập và smoke test.

**Interface thống nhất với frontend:**

```python
send_message(session_id, user_text) -> {
    "assistant_text": "...",
    "status": "answered | waiting_for_user | error",
    "rounds": [],
    "tool_events": [],
    "artifact_version": "...",
    "provider": "openai",
    "model": "..."
}
```

**Bằng chứng bàn giao:**

- Backend chạy được với OpenAI và dữ liệu giả lập.
- Test backend PASS.
- Transcript lưu đúng, không chứa API key.
- Commit kỹ thuật riêng có thể đối chiếu.

### Thành viên 3 — [Ngô Đinh Minh Nhật - 2A202602569]

**Vai trò:** Frontend/UI

**File sở hữu dự kiến:**

- `starter_v0/app.py`
- Phần dependency UI trong `starter_v0/requirements.txt`
- Ảnh hoặc transcript demo giao diện nếu nhóm cần

**Công việc:**

1. Xây giao diện chat bằng Streamlit hoặc framework tương đương.
2. Hiển thị provider, model và artifact version đang chạy.
3. Hiển thị lịch sử hội thoại nhiều lượt.
4. Với mỗi tool call, hiển thị rõ:
   - tên tool;
   - input/arguments;
   - kết quả hoặc lỗi;
   - thứ tự vòng gọi tool.
5. Hiển thị rõ trạng thái đang chờ người dùng bổ sung thông tin hoặc xác nhận.
6. Thêm nút tạo phiên mới và tải transcript JSON.
7. Không che tool error và không hiển thị API key.

**Lệnh chạy dự kiến:**

```powershell
streamlit run app.py
```

**Bằng chứng bàn giao:**

- UI chạy được trên máy thành viên khác theo README.
- Có demo hội thoại bình thường, thiếu thông tin, nhiều lượt và tạo ticket sau xác nhận.
- Tool call, input, result/error và version đều xuất hiện trên UI.

### Thành viên 4 — [Điền họ tên và MSSV]

**Vai trò:** Evaluation, Safety & Report

**File sở hữu:**

- `starter_v0/data/eval_group.json`
- Các file phân tích trong `starter_v0/analysis/`
- `starter_v0/artifacts/REPORT.md`
- Run group và adversarial sau khi v3 ổn định

**Công việc:**

1. Viết đúng 10 case mới của nhóm:
   - 5 case single-turn;
   - 5 case multi-turn;
   - có expected tool, argument hoặc hành vi rõ ràng.
2. Không sao chép case có sẵn và không dùng hai schema sample làm case nộp.
3. Sau khi v3 ổn định, chạy bộ group và adversarial.
4. Phân tích thủ công ít nhất 3 adversarial case, gồm actual calls, tool results và kiểm tra filesystem.
5. Tổng hợp các phần B3, B4a và B6 của report.
6. Thu thập link evidence từ các thành viên; không tự bịa metric, transcript hoặc commit.

**Bằng chứng bàn giao:**

- `eval_group.json` hợp lệ và đúng cấu trúc 5+5.
- Run group và adversarial không có provider error.
- Phân tích ít nhất 3 case an toàn.
- Report dẫn tới đúng run, transcript, file và commit.

## 4. Interface giữa frontend và backend

Frontend không gọi trực tiếp OpenAI và không tự thực thi tool. Backend chịu trách nhiệm tạo provider, nạp prompt/tool declaration, giữ history, chạy agent loop và lưu transcript.

Luồng xử lý:

```text
Người dùng
    -> Frontend gửi session_id + user_text
    -> Backend ghép history và system prompt
    -> Model chọn tool
    -> Backend thực thi tool local
    -> Backend trả reply + tool trace + version
    -> Frontend hiển thị và transcript được lưu
```

## 5. Kế hoạch nhánh Git

Các nhánh đề xuất:

```text
feat/prompt-evaluation
feat/backend-chat-service
feat/frontend-streamlit
feat/eval-safety-report
```

Quy trình cho mỗi thành viên:

```powershell
git switch main
git pull
git switch -c <ten-nhanh>

# Làm một thay đổi có thể kiểm tra được
git add <cac-file-thuoc-phan-viec>
git commit -m "<mo-ta-thay-doi>"
git push -u origin <ten-nhanh>
```

Không thêm toàn bộ repository bằng `git add .` trước khi kiểm tra `git status`, tránh đưa `.env`, ticket hoặc file tạm vào commit.

## 6. Thứ tự triển khai

### Giai đoạn 1 — Chốt baseline và contract

- Ghi v0 vào `version_log.csv`.
- Commit run v0 hợp lệ.
- Thống nhất interface frontend–backend.
- Tạo bốn nhánh làm việc.

### Giai đoạn 2 — Làm song song

- Thành viên 1 chạy tuần tự v1–v3.
- Thành viên 2 xây backend và test bằng prompt hiện có.
- Thành viên 3 dựng UI với mock response theo interface, sau đó nối backend.
- Thành viên 4 viết 10 group cases và chuẩn bị khung phân tích an toàn/report.

### Giai đoạn 3 — Tích hợp

1. Merge backend.
2. Merge frontend và kiểm tra UI với backend thật.
3. Merge artifact v3 cùng các run base.
4. Chạy group, adversarial và các transcript demo bằng artifact v3.
5. Hoàn thiện report, TEAM và INDIVIDUAL.

### Giai đoạn 4 — Final checkout

- Chạy lại smoke test backend và UI trên một máy khác.
- Kiểm tra mọi run evidence có đủ số case và không có provider error.
- Kiểm tra transcript/tool result, không chỉ nhìn PASS/FAIL.
- Kiểm tra `git status`, `.gitignore` và lịch sử commit của từng thành viên.
- Xác nhận repo không chứa `.env`, API key, dữ liệu thật, cache hoặc ticket phát sinh.
- Mỗi thành viên tự nộp cùng URL repo trên VLearn và ghi thời điểm thực tế vào `TEAM.md`.

## 7. Chức năng mở rộng sau khi hoàn thành phần chung

Frontend và backend phục vụ yêu cầu UI bắt buộc nên không tự động được tính bonus. Chỉ làm bonus sau khi phần chung ổn định.

Các tool bonus đã triển khai:

- `check_software_approval`: kiểm tra một tên phần mềm và phiên bản có nằm trong catalog giả lập được phê duyệt hay không.
- `lookup_ticket_status`: tra cứu read-only trạng thái ticket giả lập.
- `check_maintenance_window`: tra cứu lịch bảo trì giả lập và phân biệt với trạng thái dịch vụ hiện tại.

Đây là các chức năng mới ngoài luồng Helpdesk cơ bản đã chốt gồm kiểm tra trạng thái, chẩn đoán thiết bị, tìm hướng dẫn và tạo ticket.

Phân công tool mở rộng:

- Phạm Xuân Quý: xây dữ liệu, implementation, `TOOL.md` và unit/smoke test cho ba tool.
- Vũ Văn Diện: tích hợp declaration vào `artifacts/tools.yaml` sau khi v3 core đã được chốt, tránh làm thay đổi thí nghiệm base giữa chừng.
- Thành viên 3: không hard-code tên tool; UI hiển thị trace của tool mở rộng qua cơ chế tool event chung.
- Thành viên 4: viết bộ eval bonus riêng, kiểm tra safety và bổ sung evidence vào mục B5 của report.

Bonus cần có đủ:

- Dữ liệu giả lập riêng.
- `TOOL.md` và `tool.py`.
- Đăng ký trong tool registry và khai báo trong `tools.yaml`.
- Output JSON ổn định và lỗi rõ ràng khi input không tồn tại.
- Smoke test, eval case và demo UI.
- Guardrail không gửi asset ID, employee ID hoặc diagnostic nội bộ ra dịch vụ ngoài.

Input/output dự kiến:

```text
check_software_approval(
    software_name: string,
    version: string,
    operating_system: string
)

-> {
    status: "approved | upgrade_required | not_approved | not_found",
    matched_product: "...",
    requested_version: "...",
    approved_versions: [],
    operating_system: "...",
    recommendation: "...",
    source: "mock_approved_software_catalog"
}
```

Tool này chỉ đọc catalog giả lập, không tự cài phần mềm, không thay đổi thiết bị và không gửi dữ liệu ra web. Nếu tên phần mềm hoặc hệ điều hành không rõ, agent phải dùng `clarify` thay vì tự đoán.

## 8. Definition of Done

- [ ] Có run base v0, v1, v2 và v3 hợp lệ.
- [ ] `version_log.csv` có giả thuyết, hash, metric và đường dẫn run.
- [ ] Có đúng 10 case nhóm: 5 single-turn + 5 multi-turn.
- [ ] Có run 12 adversarial case và phân tích ít nhất 3 case.
- [ ] Backend quản lý được chat nhiều lượt và transcript.
- [ ] UI hiển thị tool call, input, result/error, provider/model và version.
- [ ] Có transcript cho luồng bình thường, thiếu thông tin, nhiều lượt và hành động ghi dữ liệu sau xác nhận.
- [ ] `REPORT.md` và `TEAM.md` đầy đủ evidence.
- [ ] Mỗi thành viên có commit kỹ thuật và tự viết mục `INDIVIDUAL`.
- [ ] Không có secret, dữ liệu thật hoặc ticket phát sinh trong repository.
