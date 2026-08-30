"""Promises the player makes, and the consequences of keeping or missing them.

Commitments are the smallest mechanism that produces the causality the design
asks for: agreeing to meet Theo at five and then skipping class with Iris should
not merely subtract a number, it should leave Theo somewhere he would not
otherwise have been.

A commitment is data, not a callback. Nothing here schedules work; the director
reads commitment state when picking the next scene, and the calendar expires
overdue ones when the day rolls over.
"""

from __future__ import annotations

from s32_engine.containers import new_dict, new_list
from s32_engine.types import CommitmentState, CommitmentStatus, GameState

#: Statuses that still occupy the player's attention.
OPEN_STATUSES: frozenset[CommitmentStatus] = frozenset({"active"})


def make(
    state: GameState,
    commitment_id: str,
    *,
    kind: str,
    participants: list[str],
    due_day: int,
    due_time: str = "",
    importance: int = 50,
) -> CommitmentState:
    """Record a new commitment, replacing any earlier one with the same id.

    Args:
        state: Run state to mutate.
        commitment_id: Stable id, e.g. ``"meet_theo_clubroom"``. Reused ids
            replace the old record, which is the right behaviour for a promise
            that is renegotiated.
        kind: Free-form category (``"meeting"``, ``"favour"``, ``"secret"``).
        participants: Character ids involved, excluding the player.
        due_day: Run day the promise comes due.
        due_time: Optional time slot, purely for presentation.
        importance: ``0..100``. Weights how hard breaking it lands.

    Returns:
        The stored record.
    """
    record: CommitmentState = new_dict(
        {
            "id": commitment_id,
            "kind": kind,
            "participants": new_list(participants),
            "made_day": state["world"]["day"],
            "due_day": due_day,
            "due_time": due_time,
            "importance": max(0, min(100, importance)),
            "status": "active",
            "resolved_day": 0,
        }
    )
    existing = _index(state, commitment_id)
    if existing is None:
        state["commitments"].append(record)
    else:
        state["commitments"][existing] = record
    return record


def _index(state: GameState, commitment_id: str) -> int | None:
    """Return the list index of a commitment, or ``None``."""
    for i, record in enumerate(state["commitments"]):
        if record["id"] == commitment_id:
            return i
    return None


def get(state: GameState, commitment_id: str) -> CommitmentState | None:
    """Return a commitment record by id, or ``None``."""
    index = _index(state, commitment_id)
    return None if index is None else state["commitments"][index]


def status(state: GameState, commitment_id: str) -> CommitmentStatus | None:
    """Return a commitment's status, or ``None`` if it was never made."""
    record = get(state, commitment_id)
    return None if record is None else record["status"]


def resolve(
    state: GameState, commitment_id: str, new_status: CommitmentStatus
) -> CommitmentState | None:
    """Close out a commitment.

    Only ``active`` commitments can be resolved; resolving an already-resolved
    one is a no-op rather than an error, so a scene reachable by two routes does
    not have to guard the call.
    """
    record = get(state, commitment_id)
    if record is None or record["status"] != "active":
        return record
    record["status"] = new_status
    record["resolved_day"] = state["world"]["day"]
    return record


def fulfil(state: GameState, commitment_id: str) -> CommitmentState | None:
    """Mark a commitment kept."""
    return resolve(state, commitment_id, "fulfilled")


def break_(state: GameState, commitment_id: str) -> CommitmentState | None:
    """Mark a commitment broken by the player's own choice."""
    return resolve(state, commitment_id, "broken")


def excuse(state: GameState, commitment_id: str) -> CommitmentState | None:
    """Mark a commitment missed for a reason the other party accepts.

    Distinct from ``broken`` on purpose: the story should be able to tell the
    difference between letting someone down and being genuinely prevented.
    """
    return resolve(state, commitment_id, "excused")


def expire_overdue(state: GameState) -> list[str]:
    """Expire every active commitment whose due day has passed.

    Called by :func:`s32_engine.state.advance_time` when the day rolls over.

    Returns:
        Ids of the commitments that just expired.
    """
    today = state["world"]["day"]
    expired: list[str] = []
    for record in state["commitments"]:
        if record["status"] == "active" and record["due_day"] < today:
            record["status"] = "expired"
            record["resolved_day"] = today
            expired.append(record["id"])
    return expired


def open_commitments(state: GameState) -> list[CommitmentState]:
    """Return every still-open commitment, soonest due first."""
    return sorted(
        (r for r in state["commitments"] if r["status"] in OPEN_STATUSES),
        key=lambda r: (r["due_day"], r["id"]),
    )


def due_today(state: GameState) -> list[CommitmentState]:
    """Return open commitments that come due on the current day."""
    today = state["world"]["day"]
    return [r for r in open_commitments(state) if r["due_day"] == today]


def broken_weight(state: GameState, participant: str | None = None) -> int:
    """Return the summed importance of commitments the player broke.

    Used as a soft gate: a character does not need a bespoke flag to react to
    "you keep doing this to me", they need a number that grows.
    """
    total = 0
    for record in state["commitments"]:
        if record["status"] != "broken":
            continue
        if participant is not None and participant not in record["participants"]:
            continue
        total += record["importance"]
    return total
