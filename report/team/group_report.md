# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Alpha (lớp L3B)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `<HASH>`

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn tiền giao hàng trễ của LogiX-VN bằng bốn "shape" (workflow, single agent, orchestrator, swarm) và chọn một shape để nộp hidden grader. Ba ràng buộc cứng: không hoàn tiền khi thiếu approval hợp lệ, không lộ `CANARY_SECRET_*`/PII trong trace và kết quả, crash không tạo quá một refund.

Nhóm 4 người chia theo khu vực code để làm song song mà không đụng file của nhau:

| Người | Phần việc |
| --- | --- |
| 1 | Workflow (`src/lab8/shapes/workflow.py`) và tích hợp |
| 2 | Single ReAct agent (`src/lab8/shapes/single.py`) |
| 3 | Orchestrator và handoff (`src/lab8/shapes/orchestrator.py`) |
| 4 | Durability, crash, evaluation và báo cáo (`src/tests/`, `src/reports/`, `report/team/`) |

Thứ tự: CP1 cả nhóm đọc `docs/business_rules.md`, `docs/contracts.md` và `swarm_reference.py`; CP2 ba shape làm song song, Người 4 viết test durability; CP3–CP4 kiểm tra idempotency, resume, approval, handoff, trace; CP5 benchmark, ADR và `check_submission`.

## 3. Giải pháp

Ranh giới chung của cả ba shape: **code/host quyết định tiền, model không quyết định**. Mọi shape đọc claim qua `get_claim_view` (không chạm `parent_secret`, `raw_headers_json`), tính quote đầy đủ bằng `compute_compensation` từ dữ liệu order, rồi gọi `durability.issue_refund()` với quote đầy đủ. Host là nơi duy nhất kiểm tra approval, trừ phần đã hoàn của order và ghi ledger + audit trong cùng một transaction SQLite, với idempotency key `refund:{claim_id}`. Shape truyền `crash_at` vào host và không bắt `InjectedCrash`. Kết quả trả qua `finish()` để `refund_effects` và `committed_audit_count` lấy từ ledger.

- **Workflow (A)**: luồng tất định, không gọi model. Xử lý lần lượt các nhánh thiếu `order_id` (`needs_info`), không tìm thấy đơn / principal không sở hữu đơn (`escalated`), order không đủ điều kiện (`denied`), rồi quote → host. Bỏ qua số ngày/yêu cầu viết trong ticket nếu mâu thuẫn với order.
- **Single (B)**: vòng `run_react` tối đa 8 bước, model chỉ được chọn tool đọc (`lookup_order`, `lookup_refund_history`, `compute_compensation`). Sau vòng ReAct, code lấy quote từ order và tự gọi host; model không có `issue_refund`.
- **Orchestrator (C)**: tạo handoff bằng `make_handoff` với allowlist thật (không dùng LLM tóm tắt làm redaction), chạy investigator bằng `run_readonly_investigators` chỉ với tool đọc, lấy quote từ order view investigator trả về, rồi orchestrator gọi host.

Trace (contract v1) ghi các event `lookup_order`, `quote`, `decision`, `error`, `crash`, cộng `react_summary` (single) và `handoff` đã sanitize (orchestrator). Không ghi nguyên claim/order row, parent context hay ticket thô.

## 4. Kết quả

Benchmark: 4 shape × 14 claim × 5 seed (`11,22,33,44,55`), MockLLM, giá mô phỏng, SQLite mới mỗi trial (`src/reports/benchmark.json`).

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean steps | p95 steps | Mean tool calls |
| --- | --: | --: | --: | --: | --: | --: | --: | --: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 1.86 | 2 | 2.79 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 38.70 | 2.00 | 2 | 3.64 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 46.43 | 2.79 | 3 | 4.64 |
| swarm (tham chiếu) | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 | 3 | 4.66 |

Swarm fail 1/70 trial: `R-swarm-C-002-s55`, `status resolved != denied`.

- Crash safety: **20/20** (`src/reports/crash.json`). Ngoài ra `src/tests/test_durability_resume.py` chạy crash→resume end-to-end cho workflow, single, orchestrator ở 3 điểm crash: 9/9 đều đúng một refund, một audit `refund_committed`, có checkpoint.
- Host test `python -m pytest -q`: 82 passed. Student matrix `-m student`: 248 passed (62 test mỗi shape).
- Secret/PII: 0/281 file trace khớp pattern `CANARY|Bearer|0901|Le Loi|Duong Bi Mat`. Approval bypass: 0.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md` (chọn **workflow**). Phiếu nghiên cứu và ablation: xem `report/team/research_card.md` (R1 · Scaling: thêm investigator không tăng pass nhưng tăng cost/success +66.7%).

## 5. Khó khăn và cách xử lý

- **Thiếu môi trường**: lần đầu chạy `python -m pytest` báo `No module named pytest`, `crash_test` báo `No module named 'yaml'`. Xử lý: `python -m pip install -r src/requirements.txt`.
- **Hiểu sai điểm crash khi viết test**: test ban đầu giả định crash `after_checkpoint` vẫn bắn sau khi effect đã commit, và fail với `DID NOT RAISE InjectedCrash`. Đọc lại `durability.py`: khi ledger đã có effect, host đi nhánh `idempotent_replay` và trả sớm, nên không chạy tới crash point. Đây là hành vi đúng (không ghi lại effect), nên nhóm sửa test để khẳng định `idempotent_replay` thay vì sửa host.
- **Quote đầy đủ hay đã trừ**: dễ tự trừ phần đã hoàn trước khi gọi host, làm sai C-014. Nhóm thống nhất shape luôn gửi quote đầy đủ (150000) và host tự trừ (còn 120000); có test khóa hành vi này cả sau crash.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`; cost là VND mô phỏng. Corpus public chỉ có 14 claim và ba shape đều chạm trần 1.000, nên benchmark không phân biệt được chênh lệch độ đúng nhỏ giữa chúng. Kết luận "workflow là đủ" sẽ thay đổi nếu hidden set có nhiều ticket tự do mà luật cứng không phân loại được, hoặc nếu một claim cần tra cứu song song nhiều nguồn độc lập. Hướng cải thiện: chạy tự kiểm trên `student_drop/`, gắn nhãn lỗi swarm theo MAST (bonus B2), và thử LLM thật để kiểm tra variance theo seed.

## 8. Tài liệu tham khảo

- Kim et al., *Towards a Science of Scaling Agent Systems*, Google Research, https://arxiv.org/abs/2512.08296
- `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md` của lab.
