# Team

## Thông tin nhóm

- Tên nhóm: Alpha
- Lớp: L3B
- Repo nhóm: `K5-L3B-Day08-Alpha-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/Thinh010705/K5-L3B-Day08-Alpha-FromWorkflowsToAgents.git, branch main

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Cao Minh Quang | 2A202603906 | cquang2k5@gmail.com | https://github.com/quang011105 | Workflow + Integration |
|   2 | Nguyễn Trọng Khiêm | 2A202604109 | khiem14205@gmail.com | https://github.com/KhiemNTK | Single agent |
|   3 | Nguyễn Năng Thịnh | 2A202604028 | thinh010705@gmail.com | https://github.com/Thinh010705 | Orchestrator + Handoff |
|   4 |        |      |       |        | Durability, Crash & Evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Cao Minh Quang | Workflow và tích hợp | 344fbc9 | tests/test_workflow_deterministic.py |
| Nguyễn Trọng Khiêm | Single agent | 73110d5 | tests/test_single_agent.py |
| Nguyễn Năng Thịnh | Orchestrator và handoff | 59bd15a | tests/test_orchestrator_security.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603906_CaoMinhQuang

### Phần việc phụ trách

- Người 1: Triển khai Shape A — Deterministic Workflow (`src/lab8/shapes/workflow.py`) và Tích hợp hệ thống.

### Đóng góp cụ thể

- Triển khai toàn diện logic xử lý claim theo Shape A deterministic workflow trong `src/lab8/shapes/workflow.py`.
- Tuân thủ ranh giới an toàn: đọc claim bằng `get_claim_view`, không rò rỉ PII/secret; tính quote bằng `compute_compensation`; truyền quote đầy đủ vào `durability.issue_refund` để host xử lý per-order cap và approval; xử lý re-raise `InjectedCrash` và ghi trace đạt chuẩn Trace Contract v1.
- Viết 4 bài kiểm thử kỹ thuật trong `src/tests/test_workflow_deterministic.py` kiểm chứng prompt injection invariance, PII/secret isolation, và order cap enforcement.
- Đạt 62/62 student tests cho workflow và 64/64 host gate tests.

### Bằng chứng

- Commit: `344fbc9` (`feat(workflow): implement deterministic claim workflow and unit tests`)
- File test: `src/tests/test_workflow_deterministic.py`
- Báo cáo chi tiết: `report/team/2A202603906_CaoMinhQuang.md`

## 2A202604109_NguyenTrongKhiem

### Phần việc phụ trách

- Người 2: Kiến trúc Single ReAct Agent (Shape B: `src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- Triển khai vòng lặp ReAct `run_react` với `max_steps=8` trong `src/lab8/shapes/single.py`. Model chỉ được gọi các công cụ đọc (`lookup_order`, `lookup_refund_history`, `compute_compensation`), host là nơi duy nhất ghi tiền qua `durability.issue_refund`.
- Thêm 5 unit test trong `src/tests/test_single_agent.py` kiểm chứng giới hạn 8 bước, từ chối write tools trong ReAct, kháng ticket delay sai lệch (C-002 s55), chống prompt injection (C-009) và bảo đảm gửi quote đầy đủ (C-014).

### Bằng chứng

- Commit: `73110d5` (`feat(single): implement bounded ReAct agent with read-only tools and add unit tests`)
- File test: `src/tests/test_single_agent.py`
- Báo cáo chi tiết: `report/team/2A202604109_NguyenTrongKhiem.md`

## 2A202604028_NguyenNangThinh

### Phần việc phụ trách

- Người 3: Kiến trúc Orchestrator và Handoff (Shape C: `src/lab8/shapes/orchestrator.py`).

### Đóng góp cụ thể

- Triển khai Orchestrator và Handoff allowlist trong `src/lab8/shapes/orchestrator.py`. Tạo handoff bằng `make_handoff()` chỉ chứa field được phép, investigator chỉ có tool đọc (`lookup_order`, `lookup_policy`, `compute_compensation`), không chứa secret hay PII.
- Thêm unit test trong `src/tests/test_orchestrator_security.py` kiểm chứng trace không lộ secret, parent_secret hay raw_headers.

### Bằng chứng

- Commit: `59bd15a` (`feat(orchestrator): implement sanitized investigator handoff`)
- File test: `src/tests/test_orchestrator_security.py`
- Báo cáo chi tiết: `report/team/2A202604028_NguyenNangThinh.md`

## MSSV_HoTen

### Phần việc phụ trách

- Người 4: Durability, crash, evaluation và báo cáo.

### Đóng góp cụ thể

-

### Bằng chứng

-
