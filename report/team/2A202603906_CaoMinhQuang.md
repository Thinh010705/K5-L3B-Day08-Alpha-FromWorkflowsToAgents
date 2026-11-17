# Báo cáo cá nhân — 2A202603906_CaoMinhQuang

## 1. Thông tin thành viên

- Họ tên: Cao Minh Quang
- MSSV: 2A202603906
- Email: cquang2k5@gmail.com
- GitHub: quang011105

## 2. Phần việc phụ trách

- Người 1: Phụ trách triển khai Shape A — Deterministic Workflow (`src/lab8/shapes/workflow.py`) và Tích hợp hệ thống.
- Đảm bảo ranh giới an toàn: model không quyết định tiền hay ghi database, tiền do code `compute_compensation` tính, host `durability.issue_refund` là cổng ghi ledger duy nhất và kiểm tra approval, idempotency, per-order cap.
- Thiết kế và bổ sung các kiểm thử kỹ thuật (unit tests) xác minh tính đúng đắn và an toàn của workflow.

## 3. Đóng góp cụ thể

- **Triển khai toàn diện Shape A trong `src/lab8/shapes/workflow.py`:**
  - Đọc claim an toàn thông qua `get_claim_view(conn, claim_id)` (loại trừ hoàn toàn `parent_secret` và `raw_headers`).
  - Xử lý thiếu `order_id` -> trả về status `needs_info`, `proposal_amount = 0`, không ghi ledger (vượt qua T04).
  - Kiểm tra quyền sở hữu đơn bằng `lookup_order(conn, order_id, principal_id)`. Khi không tìm thấy đơn hoặc principal không sở hữu -> trả về `escalated`, `proposal_amount = 0`, không copy PII hay internal note vào trace (vượt qua T05).
  - Tính toán quote hoàn tiền từ dữ liệu order trong DB bằng `compute_compensation(conn, order)`. Tuyệt đối bỏ qua số ngày khai man hay câu lệnh prompt injection trong ticket (vượt qua T02, T06, T09).
  - Xử lý quote $\le 0$ -> trả về `denied`, `proposal_amount = 0`, không gọi `issue_refund`.
  - Xử lý quote $> 0$ -> gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` với **quote đầy đủ** để host tự trừ các khoản hoàn trước đó của đơn hàng (vượt qua T01, T03, T08, T10, T13, T14).
  - Hỗ trợ crash safety: truyền `crash_at` vào host, bắt `InjectedCrash` để ghi trace ra đĩa rồi re-raise exception cho crash harness kiểm tra (vượt qua T11 và T12).
  - Chuẩn hóa đầu ra với `finish()` đảm bảo trả về `RunResult` chuẩn và trace hợp lệ theo Trace Contract v1.
- **Xây dựng bộ kiểm thử kỹ thuật trong `src/tests/test_workflow_deterministic.py`:**
  - `test_workflow_ignores_ticket_prompt_injection`: Kiểm chứng workflow bất biến trước prompt injection và khai khống ngày trễ trong ticket.
  - `test_workflow_escalates_and_redacts_on_unauthorized_principal`: Kiểm tra xử lý chuyển cấp và bảo mật PII/secret khi đơn hàng ngoài phạm vi sở hữu.
  - `test_workflow_enforces_per_order_cap_sequential`: Kiểm thử trần bồi hoàn theo đơn hàng khi có nhiều claim kế tiếp nhau.
  - `test_workflow_trace_contract_compliance`: Xác nhận trace tuân thủ nghiêm ngặt Trace Contract v1.
- **Tích hợp và kiểm thử:**
  - Đạt 62/62 student tests cho workflow.
  - Đạt 58/58 host gate tests.

## 4. Bằng chứng

- Commit hash: `344fbc9` (`feat(workflow): implement deterministic claim workflow and unit tests`)
- File mã nguồn: `src/lab8/shapes/workflow.py`
- File unit test: `src/tests/test_workflow_deterministic.py`
- Kết quả test:
  - `python -m pytest -q -m student -o addopts= -k workflow` -> `62 passed`
  - `python -m pytest -q` -> `58 passed`

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity Assistant.
- Mục đích sử dụng: Hỗ trợ tra cứu nhanh quy tắc nghiệp vụ trong `docs/business_rules.md`, đối chiếu hợp đồng `docs/contracts.md`, tư vấn cấu trúc các test cases cho prompt injection và boundary test.
- Cách tự kiểm tra: Toàn bộ code và test được chạy và kiểm thử trực tiếp trên môi trường ảo Python 3.12 (`.venv`) cục bộ, đối chiếu kết quả với ma trận student test của đề bài.

## 6. Tự đánh giá

- Đáp ứng đầy đủ các điều kiện Must-Pass: không approval bypass, không secret/PII leak, đảm bảo tính idempotency và an toàn khi crash.

