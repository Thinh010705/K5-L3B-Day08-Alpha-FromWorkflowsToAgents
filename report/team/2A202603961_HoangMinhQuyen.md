# Báo cáo cá nhân — 2A202603961_HoangMinhQuyen

## 1. Thông tin thành viên

- Họ tên: Hoàng Minh Quyền
- MSSV: 2A202603961
- Email: quyentryhard@gmail.com
- GitHub: https://github.com/EddyTryToCode

## 2. Phần việc phụ trách

Người 4 — Durability, crash, evaluation và báo cáo: kiểm chứng host `src/lab8/durability.py` (không sửa), bổ sung test durability, chạy crash suite và benchmark bốn shape, điền ADR, research card, group report và kiểm tra `TEAM.md`.

## 3. Đóng góp cụ thể

- Commit `<HASH>` — `test(crash): cover retry, crash/resume idempotency, approval binding and order cap`.
- Thêm `src/tests/test_durability_resume.py` (18 test):
  - gọi lại cùng claim 5 lần → 1 dòng ledger, 1 audit, key `refund:C-003`;
  - crash `before_effect` → không ghi gì, resume commit đúng một lần;
  - crash `after_effect_before_checkpoint` → effect + audit đã có, thiếu checkpoint; resume là `idempotent_replay` và ghi checkpoint;
  - crash `after_checkpoint` → resume là replay thuần;
  - crash liên tiếp nhiều điểm → vẫn một refund, tổng order O-107 = 35000;
  - approval của claim khác (C-STEAL dùng A-003) → luôn `approval_claim_mismatch`, kể cả khi retry với crash point;
  - order đã hoàn trước (C-013) → retry vẫn `order_already_refunded`, tổng order không đổi;
  - trần theo order (C-014) → sau crash và replay vẫn là 120000, tổng O-515 = 150000;
  - claim thứ hai trên cùng order sau crash/resume → không trả thêm;
  - end-to-end 3 shape × 3 điểm crash → đúng một refund, một audit, có checkpoint.
- Sinh và commit bằng chứng `src/reports/crash.json` (20/20) và `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed).
- Quyết định kỹ thuật: chọn **workflow** cho hidden grader (pass^5 1.000, variance 0, rẻ nhất 27.86 VND/success). Với ablation R1, so workflow ↔ orchestrator trong cùng một lần benchmark để chỉ đổi topology.
- Phát hiện khi viết test: sau khi effect đã commit, host trả `idempotent_replay` sớm nên crash `after_checkpoint` không bắn nữa. Đây là hành vi đúng; test được viết để khóa hành vi này thay vì sửa host.

## 4. Bằng chứng

- Commit: `<HASH>`
- Test: `src/tests/test_durability_resume.py` — `python -m pytest -q` → 82 passed.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
- `src/reports/benchmark.json`: run id `R-workflow-C-001-s11` … `R-workflow-C-014-s55`; swarm fail duy nhất `R-swarm-C-002-s55`.
- Quét trace: 0/281 file trong `src/traces/` chứa `CANARY|Bearer|0901|Le Loi|Duong Bi Mat`.
- `report/team/decision_adr.md`, `report/team/research_card.md`, `report/team/group_report.md`.

## 5. Công cụ AI đã dùng

Claude Code: đọc `durability.py`/`crash_test.py`, gợi ý khung test, chạy pytest/benchmark và soạn nháp báo cáo. Tự kiểm tra bằng cách chạy lại toàn bộ `pytest -q`, crash suite, benchmark và `check_submission`; đối chiếu từng số trong ADR với `benchmark.json`; khi một test fail thì đọc lại code host để xác định test sai chứ không phải host sai.

## 6. Tự đánh giá

Hoàn thành phần durability và evaluation: crash 20/20, đủ test cho các trường hợp được giao, benchmark đủ 4 shape × 5 seed, báo cáo có số liệu và run id khớp file report. Hạn chế: ablation chỉ dùng corpus public và MockLLM, ba shape chạm trần 1.000 nên chưa đo được chênh lệch độ đúng nhỏ.
