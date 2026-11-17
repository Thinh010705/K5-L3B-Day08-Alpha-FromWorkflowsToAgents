"""Durability host: retry, crash/resume at every point, approval binding and per-order cap.

Người 4 (durability / crash / evaluation). Không sửa lab8/durability.py; các test
này chỉ kiểm chứng host từ bên ngoài và qua ba shape của nhóm.
"""

from __future__ import annotations

import pytest

from lab8.db import connect
from lab8.durability import (
    InjectedCrash,
    committed_audit_count,
    get_refund,
    idempotency_key,
    issue_refund,
)
from lab8.policy import order_refunded_vnd

CRASH_POINTS = ("before_effect", "after_effect_before_checkpoint", "after_checkpoint")


def _ledger_rows(conn, claim_id: str) -> int:
    return conn.execute(
        "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?", (claim_id,)
    ).fetchone()["n"]


def _checkpoint(conn, claim_id: str):
    return conn.execute(
        "SELECT 1 FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'", (claim_id,)
    ).fetchone()


# --- gọi lại cùng claim ---------------------------------------------------------


def test_many_retries_of_same_claim_leave_one_row_and_one_audit(public_db):
    conn = connect(public_db)
    outcomes = [issue_refund(conn, "C-003", 150000) for _ in range(5)]
    effect = get_refund(conn, "C-003")
    rows = _ledger_rows(conn, "C-003")
    audits = committed_audit_count(conn, "C-003")
    conn.close()
    assert outcomes[0]["reason"] == "committed"
    assert all(o["reason"] == "idempotent_replay" for o in outcomes[1:])
    assert effect["idempotency_key"] == idempotency_key("C-003") == "refund:C-003"
    assert rows == 1
    assert audits == 1


# --- crash ở từng điểm rồi resume ----------------------------------------------


def test_crash_before_effect_writes_nothing_then_resume_commits_once(public_db):
    conn = connect(public_db)
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-001", 35000, crash_at="before_effect")
    assert get_refund(conn, "C-001") is None
    assert committed_audit_count(conn, "C-001") == 0
    assert _checkpoint(conn, "C-001") is None

    resumed = issue_refund(conn, "C-001", 35000)
    rows = _ledger_rows(conn, "C-001")
    audits = committed_audit_count(conn, "C-001")
    checkpoint = _checkpoint(conn, "C-001")
    conn.close()
    assert resumed["reason"] == "committed"
    assert rows == 1 and audits == 1
    assert checkpoint is not None


def test_crash_after_effect_before_checkpoint_resume_writes_checkpoint(public_db):
    conn = connect(public_db)
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-001", 35000, crash_at="after_effect_before_checkpoint")
    # Effect và audit đã commit cùng transaction; chỉ thiếu checkpoint.
    assert _ledger_rows(conn, "C-001") == 1
    assert committed_audit_count(conn, "C-001") == 1
    assert _checkpoint(conn, "C-001") is None

    resumed = issue_refund(conn, "C-001", 35000)
    rows = _ledger_rows(conn, "C-001")
    audits = committed_audit_count(conn, "C-001")
    checkpoint = _checkpoint(conn, "C-001")
    conn.close()
    assert resumed["reason"] == "idempotent_replay"
    assert rows == 1 and audits == 1
    assert checkpoint is not None


def test_crash_after_checkpoint_resume_is_pure_replay(public_db):
    conn = connect(public_db)
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-001", 35000, crash_at="after_checkpoint")
    assert _checkpoint(conn, "C-001") is not None

    resumed = issue_refund(conn, "C-001", 35000)
    rows = _ledger_rows(conn, "C-001")
    audits = committed_audit_count(conn, "C-001")
    conn.close()
    assert resumed["reason"] == "idempotent_replay"
    assert int(resumed["effect"]["amount_vnd"]) == 35000
    assert rows == 1 and audits == 1


def test_repeated_crashes_then_resume_still_one_refund(public_db):
    conn = connect(public_db)
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-011", 35000, crash_at="before_effect")
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-011", 35000, crash_at="after_effect_before_checkpoint")
    # Effect đã commit: lần gọi sau đi nhánh idempotent replay, nên crash sau
    # checkpoint không còn bắn nữa — host không ghi lại effect lần hai.
    late = issue_refund(conn, "C-011", 35000, crash_at="after_checkpoint")
    assert late["reason"] == "idempotent_replay"
    final = issue_refund(conn, "C-011", 35000)
    rows = _ledger_rows(conn, "C-011")
    audits = committed_audit_count(conn, "C-011")
    total = order_refunded_vnd(conn, "O-107")
    conn.close()
    assert final["ok"] is True
    assert rows == 1 and audits == 1
    assert total == 35000


# --- approval của claim khác ----------------------------------------------------


def test_borrowed_approval_never_pays_even_across_crash_and_retry(public_db):
    conn = connect(public_db)
    conn.execute(
        """
        INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
        VALUES ('C-STEAL', 'P-100', 'O-303', 'dùng approval của C-003', 'CANARY_SECRET_PARENT_STEAL', '{}', 'A-003')
        """
    )
    conn.commit()
    outcomes = []
    for point in (*CRASH_POINTS, None):
        # Policy chặn trước mọi crash point nên không có InjectedCrash nào được bắn.
        outcomes.append(issue_refund(conn, "C-STEAL", 150000, crash_at=point))
    effect = get_refund(conn, "C-STEAL")
    audits = committed_audit_count(conn, "C-STEAL")
    conn.close()
    assert all(o["reason"] == "approval_claim_mismatch" for o in outcomes)
    assert effect is None
    assert audits == 0


# --- order đã được refund trước đó + trần theo order ----------------------------


def test_order_already_refunded_stays_denied_on_retry(public_db):
    conn = connect(public_db)
    before = order_refunded_vnd(conn, "O-505")
    outcomes = [issue_refund(conn, "C-013", 35000) for _ in range(3)]
    after = order_refunded_vnd(conn, "O-505")
    effect = get_refund(conn, "C-013")
    conn.close()
    assert all(o["reason"] == "order_already_refunded" for o in outcomes)
    assert effect is None
    assert after == before


def test_order_cap_tops_up_once_and_replay_keeps_capped_amount(public_db):
    conn = connect(public_db)
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-014", 150000, crash_at="after_effect_before_checkpoint")
    replay = issue_refund(conn, "C-014", 150000)
    effect = get_refund(conn, "C-014")
    total = order_refunded_vnd(conn, "O-515")
    conn.close()
    # Shape gửi quote đầy đủ 150000; host trừ 30000 đã hoàn trước đó.
    assert replay["reason"] == "idempotent_replay"
    assert int(effect["amount_vnd"]) == 120000
    assert total == 150000


def test_second_claim_on_same_order_after_crash_resume_pays_nothing(public_db):
    conn = connect(public_db)
    with pytest.raises(InjectedCrash):
        issue_refund(conn, "C-001", 35000, crash_at="after_effect_before_checkpoint")
    second = issue_refund(conn, "C-010", 35000)  # cùng O-107
    total = order_refunded_vnd(conn, "O-107")
    conn.close()
    assert second["reason"] == "order_already_refunded"
    assert total == 35000


# --- end-to-end qua ba shape của nhóm ------------------------------------------


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
@pytest.mark.parametrize("point", CRASH_POINTS)
def test_shape_crash_then_resume_yields_exactly_one_refund(public_db, shape, point):
    import importlib

    run_claim = importlib.import_module(f"lab8.shapes.{shape}").run_claim
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(public_db), crash_at=point)
    result = run_claim("C-001", seed=11, store_path=str(public_db), crash_at=None)

    conn = connect(public_db)
    try:
        rows = _ledger_rows(conn, "C-001")
        audits = committed_audit_count(conn, "C-001")
        effect = get_refund(conn, "C-001")
        checkpoint = _checkpoint(conn, "C-001")
    finally:
        conn.close()
    assert result.status == "resolved"
    assert rows == 1 and audits == 1
    assert int(effect["amount_vnd"]) == 35000
    assert checkpoint is not None
