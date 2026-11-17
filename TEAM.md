# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        | Workflow + Integration |
|   2 | Nguyễn Trọng Khiêm | 2A202604109 | khiem14205@gmail.com | https://github.com/KhiemNTK | Single agent |
|   3 |        |      |       |        | Orchestrator + Handoff |
|   4 |        |      |       |        | Durability, Crash & Evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Trọng Khiêm | Single agent | f6ed10a | tests/test_single_agent.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202604109_NguyenTrongKhiem

### Phần việc phụ trách

- Người 2: Kiến trúc Single ReAct Agent (Shape B: `src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- Commit: `f6ed10a` (`feat(single): implement bounded ReAct agent with read-only tools and add unit tests`).
- Test: Thêm 5 unit test trong `src/tests/test_single_agent.py` kiểm chứng giới hạn 8 bước, từ chối write tools trong ReAct, kháng ticket delay sai lệch (C-002 s55), chống prompt injection (C-009) và bảo đảm gửi quote đầy đủ (C-014).

### Bằng chứng

- 62/62 test student cho `single` pass (`tests/test_public_matrix.py`).
- 5/5 unit test trong `tests/test_single_agent.py` pass.
- `lab8.check_submission` báo `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.
- Báo cáo chi tiết: `report/team/2A202604109_NguyenTrongKhiem.md`.
