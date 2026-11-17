# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 75e45da
- Run id dẫn chứng: R-workflow-C-001-s11 … R-workflow-C-014-s55 (70 trial, src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70/70 trial)
- Cost per success (mô phỏng, VND): 27.86 (single 38.70, orchestrator 46.43, swarm 49.57)
- Crash safety: 20/20 (src/reports/crash.json); thêm 9/9 crash→resume end-to-end trong src/tests/test_durability_resume.py
- Secret leak / approval bypass: 0 / 0 (0/281 trace chứa CANARY_SECRET_*/PII; không trial nào có refund thiếu approval hợp lệ)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Cả bốn shape chạy trên cùng corpus `data/public_claims.jsonl` (14 claim), cùng seed `11,22,33,44,55`, cùng MockLLM, cùng tool và bảng giá mô phỏng (một lệnh benchmark duy nhất, SQLite mới cho mỗi trial). Workflow, single và orchestrator đều đạt pass 1.000, pass^5 1.000, variance 0; swarm đạt 0.986 / pass^5 0.929 vì fail C-002 ở seed 55 (`status resolved != denied`). Khi ba shape hòa nhau về độ đúng, tiêu chí quyết định là chi phí và độ ổn định: workflow rẻ nhất (27.86 VND/success, thấp hơn single 28%, orchestrator 40%, swarm 44%), ít bước nhất (mean 1.86, p95 2) và không gọi model (`mean_model_calls = 0`), nên không có nguồn biến thiên theo seed. Bài toán claim là tuần tự (đọc claim → order → tính quote → host ghi tiền), không có nhánh song song nào để multi-agent khai thác.

## Có đáng đổi lấy multi-agent không

Không đáng trên bộ hiện tại: orchestrator và swarm không đạt pass cao hơn workflow nhưng tốn hơn 67–78% chi phí và thêm ~1 bước/claim; swarm còn có variance > 0. Nếu một shape multi-agent nhỉnh hơn về pass nhưng cost và variance cao hơn, nhóm vẫn giữ workflow, trừ khi chênh lệch pass^5 vượt nhiễu seed (≥ 1 claim ổn định qua cả 5 seed) **và** không đánh đổi crash safety, leak hay bypass. Quyết định sẽ đảo lại khi: (1) corpus có nhiều ticket tự do mà luật cứng không phân loại được (khi đó single/orchestrator dùng model sẽ có lợi), (2) cần tra cứu song song nhiều nguồn độc lập cho một claim, hoặc (3) hidden set có case mà workflow trả `needs_info`/`escalated` sai trong khi agent đọc hiểu được.

## Trace và bằng chứng

Trace (contract v1, `lab8.trace.Trace`, file `traces/<run_id>.json`) ghi: `lookup_order` (chỉ `visible`/`reason`), `quote` (`amount_vnd`, `reason`, `clause_ids`, `parts`), `decision` (status khi kết thúc sớm), `error` (`unknown_claim`, `step_cap`), `crash` (điểm crash), riêng single có `react_summary` và orchestrator có `handoff` đã sanitize. Cố ý **không** ghi: nguyên claim row (`parent_secret`, `raw_headers_json`), nguyên order row (SĐT, địa chỉ, item nội bộ), parent context của orchestrator và nội dung ticket thô, vì đây là chỗ lộ `CANARY_SECRET_*`/PII hay gặp nhất. Kiểm chứng: grader quét `trace_path` và mọi file `<run_id>*`; ngoài ra nhóm grep toàn bộ 281 file trong `src/traces/` với các pattern `CANARY|Bearer|0901|Le Loi|Duong Bi Mat` → 0 file khớp. Shape không ghi log ra chỗ khác hoặc stdout; nếu có, đội security phải đưa file đó vào cùng thư mục và tên `<run_id>*` để scanner quét được — fail-closed, log không quét được coi như không sạch.

## Giới hạn

MockLLM không phải model sản xuất; kết quả pass 1.000 không chứng minh hành vi với LLM thật. Latency để `unavailable`. Cost là VND mô phỏng, không phải hóa đơn API. Corpus public chỉ có 14 claim; hidden grader có thể khác. Không sửa JSON trong `src/reports/` bằng tay — mọi số trong ADR lấy từ `benchmark.json` và `crash.json` do công cụ sinh ra.
