# Phân công công việc nhóm 4 người

Tài liệu này dùng để thống nhất phạm vi công việc, mục tiêu và bằng chứng cần nộp của từng thành viên trong Lab 8 — From Workflows to Agents.

## Mục tiêu chung

Nhóm phải triển khai và kiểm thử ba shape còn thiếu:

- `workflow`
- `single`
- `orchestrator`

Shape `swarm` đã có sẵn và được dùng làm đối chứng. Sau khi hoàn thành code, nhóm phải chạy benchmark bốn shape, kiểm tra crash và chọn một shape để nộp vào hidden grader.

Ba điều kiện bắt buộc đối với shape được chọn:

1. Không hoàn tiền khi thiếu approval hợp lệ.
2. Không để lộ `CANARY_SECRET_*` hoặc dữ liệu cá nhân trong trace và kết quả.
3. Crash không tạo quá một refund; crash suite phải đạt `20/20`.

Mỗi thành viên phải có ít nhất một commit kỹ thuật và ít nhất một test được thêm hoặc sửa.

## Phân công tổng quát

| Thành viên | Vai trò | Khu vực chính |
| --- | --- | --- |
| Người 1 | Workflow và tích hợp | `src/lab8/shapes/workflow.py` |
| Người 2 | Single ReAct agent | `src/lab8/shapes/single.py` |
| Người 3 | Orchestrator và handoff | `src/lab8/shapes/orchestrator.py` |
| Người 4 | Durability, crash, evaluation và báo cáo | `src/tests/`, `src/reports/`, `report/team/` |

Không sửa các file thước đo hoặc dữ liệu nền: `src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/metrics.py`, `src/config/` và `src/data/`.

## Người 1 — Workflow và tích hợp

### Việc phải làm

- Implement shape A trong `src/lab8/shapes/workflow.py`.
- Đọc claim bằng `get_claim_view`, không đọc và ghi nguyên claim row.
- Xử lý đúng các nhánh thiếu `order_id`, không tìm thấy đơn, principal không sở hữu đơn và order không hợp lệ.
- Tính quote từ dữ liệu order bằng `compute_compensation`.
- Bỏ qua số ngày hoặc yêu cầu được viết trong ticket nếu chúng mâu thuẫn với dữ liệu order và policy hiện hành.
- Gọi `durability.issue_refund()` với **quote đầy đủ**.
- Truyền `crash_at` vào host và không bắt `InjectedCrash`.
- Dùng `finish()` hoặc cơ chế tương đương để mọi nhánh trả `RunResult` và trace đúng contract.
- Kiểm tra tích hợp chung của ba shape với host.

### Mục tiêu hoàn thành

- 62 test student của `workflow` đều pass.
- T01–T14 xử lý đúng status, proposal amount, ledger và audit.
- T13 và T14 đúng trần hoàn tiền theo order.
- Không có approval bypass và không có secret/PII leakage.
- Có ít nhất một test kỹ thuật được thêm hoặc sửa.
- Có commit riêng ghi rõ phần workflow.

### Lưu ý quan trọng

Quote phải là số tiền đầy đủ do compensation tính ra. Host mới là nơi trừ phần đã hoàn trước đó. Không tự trừ trước khi gọi host.

## Người 2 — Single ReAct agent

### Việc phải làm

- Implement shape B trong `src/lab8/shapes/single.py`.
- Dùng `lab8.runtime.run_react` với giới hạn tối đa 8 bước.
- Chỉ cho model chọn các tool đọc.
- Không cho model gọi `issue_refund` hoặc tự ghi ledger.
- Sau vòng ReAct, code lấy quote từ order và gọi `durability.issue_refund()`.
- Truyền quote đầy đủ, không tự trừ lịch sử refund.
- Truyền `crash_at` và không bắt `InjectedCrash`.
- Đảm bảo trace hợp lệ ở cả nhánh kết thúc sớm và nhánh refund thành công.
- Kiểm tra model không tin ticket khi ticket nói sai số ngày hoặc chứa prompt injection.

### Mục tiêu hoàn thành

- 62 test student của `single` đều pass.
- Model không quyết định số tiền refund.
- Không vượt giới hạn 8 bước.
- Không có approval bypass, secret leakage hoặc refund sai order.
- Có ít nhất một test cho giới hạn ReAct, read-only tool hoặc quote lấy từ order.
- Có commit riêng ghi rõ phần single agent.

## Người 3 — Orchestrator và handoff

### Việc phải làm

- Implement shape C trong `src/lab8/shapes/orchestrator.py`.
- Tạo handoff bằng `lab8.handoff.make_handoff`.
- Chỉ truyền các field nằm trong allowlist.
- Không truyền `parent_secret`, raw headers, toàn bộ claim row hoặc dữ liệu cá nhân.
- Chạy investigator bằng `run_readonly_investigators`.
- Đảm bảo investigator chỉ có read tools và không thể ghi ledger.
- Lấy quote từ order view do investigator trả về.
- Gọi `durability.issue_refund()` với quote đầy đủ.
- Truyền `crash_at` và không bắt `InjectedCrash`.
- Ghi handoff đã sanitize vào trace; không ghi parent context.

### Mục tiêu hoàn thành

- 62 test student của `orchestrator` đều pass.
- Handoff chỉ chứa dữ liệu được phép.
- Investigator không có quyền ghi refund.
- Trace có `run_id` đúng, được tạo trong chính lần chạy và không chứa secret/PII.
- Có ít nhất một test về allowlist, read-only investigator hoặc secret leakage.
- Có commit riêng ghi rõ phần orchestrator.

### Lưu ý quan trọng

Không dùng LLM để tóm tắt parent context rồi coi đó là redaction. Handoff phải được tạo bằng allowlist thật.

## Người 4 — Durability, crash, evaluation và báo cáo

Người 4 không sửa `durability.py`. Nhiệm vụ là kiểm chứng host, bổ sung test và tạo bằng chứng nộp bài.

### Việc phải làm về test và durability

- Đọc cơ chế transaction, idempotency key `refund:{claim_id}` và resume.
- Thêm hoặc sửa test cho các trường hợp:
  - gọi lại cùng claim;
  - crash trước khi ghi effect;
  - crash sau khi ghi effect nhưng trước checkpoint;
  - crash sau checkpoint;
  - approval của claim khác;
  - order đã được refund trước đó;
  - trần hoàn tiền theo order.
- Chạy crash suite:

```bash
python -m lab8.crash_test --count 20 --out reports/crash.json
```

### Việc về benchmark và báo cáo

- Chạy benchmark bốn shape với năm seed:

```bash
python -m lab8.benchmark \
  --shapes workflow,single,orchestrator,swarm \
  --cases data/public_claims.jsonl \
  --seeds 11,22,33,44,55 \
  --out reports/benchmark.json
```

- Phân tích pass rate, pass^5, seed variance, cost/success và số bước.
- Điền `report/team/decision_adr.md`.
- Điền `report/team/research_card.md`.
- Phối hợp viết `report/team/group_report.md`.
- Kiểm tra `TEAM.md` và báo cáo cá nhân của tất cả thành viên.
- Đảm bảo số liệu trong ADR khớp với report và có `run_id`.

### Mục tiêu hoàn thành

- `crash_safety = 20/20`.
- Không trial nào tạo hơn một refund.
- `reports/benchmark.json` có đủ 4 shape, ít nhất 10 claim và seed `11,22,33,44,55`.
- Có ít nhất một test durability hoặc evaluation được thêm hoặc sửa.
- `python -m lab8.check_submission` báo `0 FAIL`.
- Có commit riêng ghi rõ phần test/evaluation/báo cáo.

## Thứ tự phối hợp

### CP1 — Cài đặt và chia vai

Cả nhóm cùng:

- chạy `python -m lab8.smoke`;
- chạy `python -m pytest -q`;
- đọc `docs/business_rules.md`, `docs/contracts.md` và `swarm_reference.py`;
- điền thành viên, vai trò và repo vào `TEAM.md`.

### CP2 — Hoàn thành ba shape

Người 1, 2 và 3 triển khai song song. Người 4 chuẩn bị test durability và crash.

Kiểm tra từng shape bằng:

```bash
python -m pytest -q -m student -o addopts= -k workflow
python -m pytest -q -m student -o addopts= -k single
python -m pytest -q -m student -o addopts= -k orchestrator
```

### CP3–CP4 — Tích hợp an toàn

Kiểm tra lần lượt:

1. idempotency khi gọi lại;
2. resume sau crash;
3. approval và policy;
4. handoff allowlist;
5. trace và secret scanning.

Sau đó chạy:

```bash
python -m pytest -q
python -m lab8.crash_test --count 20 --out reports/crash.json
```

### CP5 — Benchmark và chốt bài

Người 4 điều phối benchmark và báo cáo. Người 1, 2 và 3 kiểm tra lại kết quả shape mình phụ trách, sửa lỗi nếu cần, rồi cùng review ADR.

Cuối cùng chạy:

```bash
python -m lab8.check_submission
```

Kết quả bắt buộc là `0 FAIL`.

## Quy tắc commit

Mỗi thành viên tạo ít nhất một commit kỹ thuật riêng và có test đi kèm. Ví dụ:

- `feat(workflow): implement deterministic claim workflow`
- `feat(single): add bounded ReAct claim handling`
- `feat(orchestrator): add sanitized investigator handoff`
- `test(crash): cover retry and resume idempotency`

Trong bảng đóng góp của `TEAM.md`, mỗi người phải ghi tên, vai trò, commit hash và test đã thêm hoặc sửa.

## Definition of Done của cả nhóm

- [ ] Ba shape không còn `not_implemented`.
- [ ] Host test `python -m pytest -q` xanh.
- [ ] Mỗi shape đạt 62 test student.
- [ ] Crash suite đạt `20/20`.
- [ ] Không có approval bypass.
- [ ] Không có secret hoặc PII trong trace và kết quả.
- [ ] Benchmark đủ bốn shape và năm seed.
- [ ] ADR, research card, group report và báo cáo cá nhân đã điền.
- [ ] `python -m lab8.check_submission` báo `0 FAIL`.
- [ ] Repo đã push và mọi thành viên đã nộp link repo trên LMS.
