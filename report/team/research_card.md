# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 · Scaling |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Kim et al., *Towards a Science of Scaling Agent Systems*, Google Research / Google DeepMind, 2025–2026, https://arxiv.org/abs/2512.08296 — benchmark có kiểm soát (nhiều kiến trúc agent × nhiều họ model × 4 benchmark agentic) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lợi ích của multi-agent phụ thuộc cấu trúc task: task song song hóa được thì phối hợp tập trung giúp tăng mạnh, còn task tuần tự chặt thì mọi biến thể multi-agent đều làm giảm hiệu quả; chi phí phối hợp (token, số lượt) tăng theo số agent |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận đo trên LLM thật và các benchmark của paper (tài chính, lập kế hoạch, duyệt web, workbench), không đo trên tác vụ refund có host ghi tiền; lab này dùng MockLLM, 14 claim public, giá mô phỏng |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Claim refund là task tuần tự (claim → order → quote → host). Đổi workflow (A) → orchestrator (C, thêm investigator) sẽ không tăng pass rate (Δ ≈ 0) nhưng tăng cost/success khoảng +50–80% và tăng mean steps ~+1 |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tool registry, seed 11,22,33,44,55, corpus data/public_claims.jsonl, bảng giá mô phỏng, evaluator lab8.metrics, SQLite mới mỗi trial. Biến duy nhất thay đổi: topology (workflow không investigator ↔ orchestrator có investigator read-only) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: chi phí phối hợp không mang lại độ đúng (thêm bước, thêm tool call vô ích). Đo bằng pass rate, pass^5, seed variance, cost/success, mean/p95 steps; leak và bypass phải giữ 0 |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `cd src && python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` (so cặp workflow ↔ orchestrator trong cùng lần chạy)
- Run id / file report: `src/reports/benchmark.json`, trial `R-workflow-C-*-s{11..55}` và `R-orchestrator-C-*-s{11..55}` (70 + 70 trial)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Pass rate 1.000 → 1.000 và pass^5 1.000 → 1.000 (Δ = 0), variance 0 → 0; cost/success 27.86 → 46.43 VND (+66.7%, nằm trong khoảng dự đoán); mean steps 1.86 → 2.79 (+0.93), p95 2 → 3; mean tool calls 2.79 → 4.64. Thêm investigator chỉ tăng chi phí phối hợp, không tăng độ đúng trên task tuần tự. Swarm (nhiều agent nhất) còn kém hơn: pass^5 0.929, cost 49.57
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Pass 1.000 ở cả hai shape là trần (ceiling effect) nên không đo được chênh lệch độ đúng nhỏ; cần corpus khó hơn hoặc LLM thật để kiểm tra vế "multi-agent làm giảm hiệu quả" của paper.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
