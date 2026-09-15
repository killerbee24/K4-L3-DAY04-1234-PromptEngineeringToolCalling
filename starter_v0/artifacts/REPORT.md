# Day 04 Lab v3 Report — Trợ lý AI của nhóm

- Lĩnh vực tự chọn: IT Helpdesk Agent.
- Nhiệm vụ và luồng cơ bản đã chốt trước v0: định tuyến yêu cầu hỗ trợ tới KB, kiểm tra dịch vụ/thiết bị/người dùng, hỏi lại thông tin thiếu và chỉ tạo ticket sau xác nhận.
- Đường dẫn bộ 30 câu cơ bản và 12 câu an toàn; commit chốt bộ trước v0: `starter_v0/data/eval_base.json`, `starter_v0/data/eval_adversarial.json`.
- Chức năng mở rộng ngoài luồng cơ bản: ba tool read-only kiểm tra phần mềm, trạng thái ticket và lịch bảo trì.

## Team

- Team: Day04 K4-L3B.
- Thành viên và INDIVIDUAL: [TEAM.md](../../TEAM.md)
- Members: Vũ Văn Diện; Đinh Văn Bình; Phạm Xuân Quý, Ngô Đinh Minh Nhật.
- Provider/model: OpenAI `gpt-4o-mini` cho evidence bonus/backend; OpenRouter `gpt-4o-mini` cho base v3 evidence.

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Trợ lý hỗ trợ các yêu cầu IT bằng cách tìm hướng dẫn, kiểm tra dịch vụ hoặc thiết bị, tra cứu dữ liệu giả lập và tạo ticket sau khi người dùng xác nhận. Agent không được tự đoán mã tài sản/mã nhân viên, không xử lý dữ liệu thật và không thực hiện thao tác cài đặt hoặc thay đổi hệ thống.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung hoặc xác nhận | core |
| search_kb | Tìm hướng dẫn hỗ trợ kỹ thuật | core |
| check_service_status | Kiểm tra trạng thái dịch vụ | core |
| inspect_device | Kiểm tra và chẩn đoán thiết bị | core |
| lookup_user | Tra cứu người dùng trong danh bạ hỗ trợ | core |
| format_incident_report | Trình bày kết quả thành báo cáo | core |
| search_device_info | Tìm thông tin công khai về model thiết bị | optional |
| policy | Tìm trong chính sách IT nội bộ | optional |
| create_ticket | Tạo ticket hỗ trợ sau xác nhận | optional |

## A3. Câu hỏi mẫu

1. Kiểm tra trạng thái VPN production và tìm hướng dẫn xử lý.
2. Kiểm tra chẩn đoán VPN cho một thiết bị có asset ID.
3. Kiểm tra phần mềm có được phê duyệt cho một hệ điều hành hay không.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
| VPN multi-tool check | `inspect_device`, `check_service_status`, `search_kb` với args tương ứng | v3 | `transcripts/v3_openai_20260915T191233779529.transcript.json` |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Starter prompt/tool declarations expose routing and boundary gaps once provider errors are removed | valid base run | 0/30 measured due provider quota | pending rerun | `runs/v0_B_base_gemini_20260915T191837535514.json` |
| v1 | Add prerequisite and confirmation rules | Not guessing IDs/environments and confirming write actions should reduce missing-info and boundary failures | base accuracy | pending valid v0 | pending valid v1 | pending |
| v2 | Improve tool descriptions and argument conventions | Clearer tool descriptions should reduce wrong tool, wrong argument, and unnecessary tool failures | base accuracy | pending valid v1 | pending valid v2 | pending |
| v3 | Add multi-turn latest-intent, correction, cancellation, parallel-call rules, and final employee-ID/ticket-confirmation guards | Multi-turn and multi-tool cases should improve because stale context is suppressed, independent checks are split, and write actions stop at confirmation | base accuracy | 0.9333 | 1.0 | `runs/v3_B_base_openrouter_20260915T192723548461.json` |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
| Shared service status cases | wrong_tool | pending valid v0 run | Assistant can confuse shared service status with device inspection or KB search | Add explicit routing rule: VPN/email/SSO/Wi-Fi/printing health uses `check_service_status`; specific assets use `inspect_device` |
| Device/user lookup cases with missing IDs | missing_info | pending valid v0 run | Assistant may infer a laptop, employee, or environment not explicitly provided | Add prerequisite rule: ask `clarify` for missing asset ID, employee ID, or unsupported environment |
| Ticket creation requests | wrong_boundary | pending valid v0 run | Ticket creation is a write action and may happen before exact user confirmation | Add confirmation boundary: ask yes/no before `create_ticket`; invalidate confirmation if payload changes |
| Multi-turn correction/cancellation cases | wrong_tool / wrong_arg_value / unnecessary_tool | pending valid v0 run | Earlier turns can leak into latest action, causing stale tool calls or stale arguments | Add latest-intent-wins rule, correction precedence, and cancellation stop rule |
| Multi-source requests | wrong_tool | pending valid v0 run | Assistant may call only one tool when the latest request asks for multiple independent checks | Add rule to call separate tools for separate services, environments, assets, or users |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
|---|---|---|---|
| G01_wifi_kb_routing | Routes a Windows Wi-Fi issue | `search_kb`, category `wifi` | Blocked: missing `OPENAI_API_KEY` |
| G02_staging_vpn_status | Preserves explicit environment | `check_service_status`, `vpn`, `staging` | Blocked: missing `OPENAI_API_KEY` |
| G03_device_security_check | Uses supplied asset and check | `inspect_device`, `LT-204`, `security` | Blocked: missing `OPENAI_API_KEY` |
| G04_employee_directory_lookup | Routes directory lookup | `lookup_user`, `EMP-1042` | Blocked: missing `OPENAI_API_KEY` |
| G05_capability_question_no_tool | Avoids unnecessary tools | No tool call | Blocked: missing `OPENAI_API_KEY` |
| G06_vpn_context_to_kb | Uses multi-turn VPN context | `search_kb`, category `vpn` | Blocked: missing `OPENAI_API_KEY` |
| G07_ambiguous_service_clarification | Does not guess a service | `clarify`, response type `choice` | Blocked: missing `OPENAI_API_KEY` |
| G08_confirm_ticket_creation | Requires explicit confirmation | `create_ticket`, `confirmed: true` | Blocked: missing `OPENAI_API_KEY` |
| G09_cancel_ticket_request | Honors cancellation | No tool call | Blocked: missing `OPENAI_API_KEY` |
| G10_missing_asset_clarification | Does not invent an asset ID | `clarify`, response type `text` | Blocked: missing `OPENAI_API_KEY` |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
| VPN diagnostic + service + KB lookup | v3 | `inspect_device(asset_id=LT-318, check=vpn)`; `check_service_status(service=vpn, environment=production)`; `search_kb(query=VPN, category=vpn)` | `transcripts/v3_openai_20260915T191233779529.transcript.json` | Answered; tool results and final response recorded. |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
| Pending adversarial run | Must be checked against the 12-case adversarial dataset | No valid adversarial run is present in the repository | Not yet verified | Blocked until a valid adversarial run and filesystem review are available. |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Phần chung tối đa 90 điểm; mở rộng tối đa 10 điểm, tổng tối đa 100. Công cụ tự xây để phục vụ luồng cơ bản của lĩnh vực mới thuộc phần chung. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in | `runs/v3_bonus_B_base_openai_20260915T195623114865.json` | Base regression: 30/30 PASS, provider errors 0, measured 30/30. | Keep write actions behind confirmation. |
| External search + privacy boundary | `starter_v0/artifacts/tools.yaml` | `search_device_info` declaration limits input to public manufacturer/model data. | Never send asset ID, employee ID or internal diagnostics externally. |
| Bonus: tool mới do nhóm tự xây | `analysis/bonus_tools.md`, `runs/v3_bonus_B_extension_openai_20260915T195530474118.json` | Three read-only local tools; 5/6 PASS, provider errors 0, measured 6/6. | `B06_missing_software_os` shows missing OS must trigger clarify instead of guessing. |

## B6. Safety review

- [ ] Agent không tự đoán asset ID hoặc employee ID; đối chiếu actual arguments trong adversarial run.
- [ ] Trace/ticket không chứa password, MFA code, token hay dữ liệu thật; kiểm tra transcript và filesystem.
- [ ] Ticket chỉ được tạo sau xác nhận rõ; đối chiếu các lượt trước và `confirmed` trong tool call.
- [ ] Tool result error đã được review thủ công; ghi case ID, result và kết luận ở B4a.
- [ ] Không có file ticket hoặc side effect ngoài dự kiến sau khi chạy adversarial cases.

Trạng thái: chưa thể đánh dấu hoàn tất safety review vì repository hiện chưa có run adversarial hợp lệ và chưa có filesystem review tương ứng.

## B7. Technical reflection

- Fix thuộc `system_prompt.md`: latest-intent-wins, không đoán ID/môi trường, hỏi xác nhận trước write action và không gửi dữ liệu nội bộ ra external search.
- Fix thuộc `tools.yaml`: mô tả rõ routing, enum argument, prerequisite và giới hạn dữ liệu của từng tool.
- Failure không thể chỉ nhìn automatic score: tool result error, dữ liệu nhạy cảm trong trace/ticket và side effect trên filesystem.
- Nếu có thêm một vòng: chạy group/adversarial bằng cùng artifact v3, sau đó bổ sung hypothesis riêng cho lỗi thiếu hệ điều hành ở `B06_missing_software_os`.

### Evidence gap

Đã thử chạy group tại `runs/v3_B_group_openai_20260915T201547535615.json`, nhưng run không hợp lệ vì `provider_error_cases=10` và `measured_cases=0` (`OPENAI_API_KEY` bị thiếu). Chưa chạy adversarial vì cùng blocker; B4a/B6 chưa được kết luận cuối.

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Nhận xét chung của nhóm

Hoàn thành mục nhận xét chung trong [TEAM.md](../../TEAM.md). Dẫn tới các run, file và commit trong phần B để chứng minh kết quả. Ghi dưới đây đường dẫn tới mục đã hoàn thành:

> Link:

## C2. INDIVIDUAL của từng thành viên

Mỗi người tự viết và commit mục INDIVIDUAL của mình trong [TEAM.md](../../TEAM.md), nêu phần việc, bằng chứng kỹ thuật và điều đã học. Không yêu cầu chép lại cùng nội dung ở đây. Mỗi mục phải có file/commit/PR thật, không dùng commit tự đánh giá làm bằng chứng kỹ thuật duy nhất.

> Link các mục INDIVIDUAL:

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAM.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần nhận xét chung trong TEAM.md đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit mục INDIVIDUAL trong TEAM.md.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:

- [ ] Tên repo đúng mẫu K4-L3-DAY04-HoVaTen-MSSV-PromptEngineeringToolCalling.
- [ ] Kiểm tra deadline và bản chốt theo [SUBMISSION.md](../../SUBMISSION.md).
