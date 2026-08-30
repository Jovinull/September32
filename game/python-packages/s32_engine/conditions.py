"""The requirement mini-language used by storylets, anchors and choices.

Requirements are authored as short strings so they read well in JSON and in the
debug trace, but they are **not** evaluated with :func:`eval`. Each string is
matched against a fixed table of forms; anything that does not match is a
content error caught by the validator, long before it could reach a player.

Refusing ``eval`` is not paranoia about malicious content -- we write the content
-- it is what makes the language *analysable*. Because every condition declares
which state it reads, the static reachability checker can tell that
``knows(old_letter)`` is unsatisfiable when no storylet grants ``old_letter``.
An arbitrary Python expression could not be checked that way.

Supported forms::

    day >= 3                        run day comparison
    calendar_day == 32              in-fiction calendar day
    location == rooftop             player location
    weather == rain                 current weather
    time_slot == evening            current slot
    time_slot in morning, evening   membership
    phase >= unsettling             ordered phase comparison
    month == September

    rel iris.trust >= 30            player -> iris
    rel iris->theo.respect < 20     npc -> npc
    trait curious >= 3
    flag archive_visits >= 2

    knows(old_photo)                player holds it as known
    suspects(old_photo)             suspected or known
    stance(iris, old_photo) == suspected
    npc_knows(iris, old_photo)

    seen(iris_rooftop_rain)
    not_seen(iris_rooftop_rain)
    seen_count(iris_rooftop_rain) >= 2
    days_since(iris_rooftop_rain) >= 3

    has_item(old_camera)
    anchor_done(arrival)
    commitment(meet_theo) == broken
    broken_weight(theo) >= 60
    char iris.present == true
    char iris.mood == withdrawn
    chance(0.25)                    rollback-safe weighted coin

Every form may be prefixed with ``not `` to negate it.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from s32_engine import commitments, knowledge, relationships
from s32_engine.errors import ConditionError
from s32_engine.state import days_since_seen, flag, has_seen, times_seen
from s32_engine.types import PHASES, GameState

if TYPE_CHECKING:
    from s32_engine.rng import Rng

_COMPARATORS: dict[str, Callable[[float, float], bool]] = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}

_IDENT = r"[a-z_][a-z0-9_]*"


@dataclass(frozen=True, slots=True)
class ConditionResult:
    """The outcome of one condition, kept for the debug trace.

    The trace is the whole reason this is a value object and not a bare bool:
    when a scene does not fire, a writer needs to see *which* clause failed and
    what the actual number was.
    """

    text: str
    passed: bool
    detail: str = ""

    def format(self) -> str:
        """Return a single aligned trace line."""
        mark = "PASS" if self.passed else "FAIL"
        return f"{mark} {self.text}" + (f"   [{self.detail}]" if self.detail else "")


class ConditionContext:
    """Everything a condition may read.

    Bundled into one object so the evaluator signature stays stable as the
    language grows, and so the simulator can supply a deterministic RNG without
    the conditions knowing whether they run inside Ren'Py.
    """

    __slots__ = ("rng", "state")

    def __init__(self, state: GameState, rng: Rng | None = None) -> None:
        self.state = state
        self.rng = rng


def evaluate(condition: str, ctx: ConditionContext) -> ConditionResult:
    """Evaluate a single condition string.

    Raises:
        ConditionError: If the string does not match any supported form. This is
            a content bug and should surface loudly during validation.
    """
    text = condition.strip()
    if not text:
        raise ConditionError("empty condition")

    negate = False
    if text.startswith("not "):
        negate = True
        text = text[4:].strip()

    for pattern, handler in _HANDLERS:
        match = pattern.fullmatch(text)
        if match is not None:
            passed, detail = handler(match, ctx)
            if negate:
                passed = not passed
            return ConditionResult(condition.strip(), passed, detail)

    raise ConditionError(f"unrecognised condition: {condition!r}")


def evaluate_all(
    conditions: tuple[str, ...] | list[str], ctx: ConditionContext
) -> list[ConditionResult]:
    """Evaluate every condition, without short-circuiting.

    Short-circuiting would be marginally faster and much less useful: the debug
    trace exists to show *all* the reasons a scene did not fire, not the first.
    """
    return [evaluate(c, ctx) for c in conditions]


def all_pass(results: list[ConditionResult]) -> bool:
    """Return whether every condition passed."""
    return all(r.passed for r in results)


def referenced_ids(condition: str) -> dict[str, set[str]]:
    """Return the content ids a condition refers to, grouped by kind.

    Used by the content validator to detect broken references, and by the static
    reachability checker to find requirements nothing can ever satisfy.
    """
    text = condition.strip().removeprefix("not ").strip()
    found: dict[str, set[str]] = {}

    def add(kind: str, value: str) -> None:
        found.setdefault(kind, set()).add(value)

    for pattern, kinds in _REFERENCE_PATTERNS:
        match = pattern.fullmatch(text)
        if match is None:
            continue
        for group, kind in kinds.items():
            value = match.groupdict().get(group)
            if value:
                add(kind, value)
        break
    return found


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

Handler = Callable[[re.Match[str], ConditionContext], tuple[bool, str]]


def _num_compare(actual: float, op: str, expected: float, label: str) -> tuple[bool, str]:
    """Compare two numbers and build the trace detail in one place."""
    return _COMPARATORS[op](actual, expected), f"{label}={_fmt(actual)}"


def _fmt(value: float) -> str:
    """Render a number without a trailing ``.0`` for whole values."""
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"


def _h_day(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    field = m.group("field")
    actual = ctx.state["world"]["calendar_day" if field == "calendar_day" else "day"]
    return _num_compare(actual, m.group("op"), int(m.group("value")), field)


def _h_world_str(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    field = m.group("field")
    actual = str(ctx.state["world"][field])  # type: ignore[literal-required]
    expected = m.group("value")
    op = m.group("op")
    passed = actual == expected if op == "==" else actual != expected
    return passed, f"{field}={actual}"


def _h_world_in(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    field = m.group("field")
    actual = str(ctx.state["world"][field])  # type: ignore[literal-required]
    options = {v.strip() for v in m.group("values").split(",")}
    return actual in options, f"{field}={actual}"


def _h_phase(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    expected = m.group("value")
    if expected not in PHASES:
        raise ConditionError(f"unknown phase: {expected!r}")
    actual = ctx.state["world"]["phase"]
    return _num_compare(PHASES.index(actual), m.group("op"), PHASES.index(expected), "phase")[0], (
        f"phase={actual}"
    )


def _h_rel(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    source = m.group("source") or "player"
    target = m.group("target")
    axis = m.group("axis")
    actual = relationships.get(ctx.state, target, axis, source=source)  # type: ignore[arg-type]
    return _num_compare(actual, m.group("op"), int(m.group("value")), f"{source}->{target}.{axis}")


def _h_trait(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    axis = m.group("axis")
    actual = ctx.state["traits"].get(axis, 0)
    return _num_compare(actual, m.group("op"), int(m.group("value")), f"trait.{axis}")


def _h_flag(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    name = m.group("name")
    return _num_compare(flag(ctx.state, name), m.group("op"), int(m.group("value")), f"flag.{name}")


def _h_knows(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    fact = m.group("fact")
    st = knowledge.stance(ctx.state, fact)
    return st == "known", f"stance={st}"


def _h_suspects(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    fact = m.group("fact")
    st = knowledge.stance(ctx.state, fact)
    return st in {"suspected", "known"}, f"stance={st}"


def _h_npc_knows(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    agent, fact = m.group("agent"), m.group("fact")
    st = knowledge.stance(ctx.state, fact, agent)
    return st == "known", f"{agent}:{fact}={st}"


def _h_stance(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    agent, fact = m.group("agent"), m.group("fact")
    actual = knowledge.stance(ctx.state, fact, agent)
    expected = m.group("value")
    op = m.group("op")
    passed = actual == expected if op == "==" else actual != expected
    return passed, f"{agent}:{fact}={actual}"


def _h_seen(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    sid = m.group("sid")
    seen = has_seen(ctx.state, sid)
    return seen, f"seen={seen}"


def _h_not_seen(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    sid = m.group("sid")
    seen = has_seen(ctx.state, sid)
    return not seen, f"seen={seen}"


def _h_seen_count(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    sid = m.group("sid")
    return _num_compare(
        times_seen(ctx.state, sid), m.group("op"), int(m.group("value")), f"seen[{sid}]"
    )


def _h_days_since(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    sid = m.group("sid")
    since = days_since_seen(ctx.state, sid)
    if since is None:
        # Never seen. Treated as "infinitely long ago" so a cooldown-style
        # requirement does not accidentally gate the first occurrence.
        return _COMPARATORS[m.group("op")](10**6, int(m.group("value"))), "never seen"
    return _num_compare(since, m.group("op"), int(m.group("value")), f"days_since[{sid}]")


def _h_has_item(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    item = m.group("item")
    return item in ctx.state["inventory"], f"inventory={len(ctx.state['inventory'])}"


def _h_anchor_done(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    anchor = m.group("anchor")
    return anchor in ctx.state["anchors_done"], f"anchors={len(ctx.state['anchors_done'])}"


def _h_commitment(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    cid = m.group("cid")
    actual = commitments.status(ctx.state, cid) or "none"
    expected = m.group("value")
    op = m.group("op")
    passed = actual == expected if op == "==" else actual != expected
    return passed, f"{cid}={actual}"


def _h_broken_weight(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    who = m.group("who")
    actual = commitments.broken_weight(ctx.state, who if who else None)
    return _num_compare(actual, m.group("op"), int(m.group("value")), "broken_weight")


def _h_char(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    char_id, field, op, value = (
        m.group("char"),
        m.group("field"),
        m.group("op"),
        m.group("value"),
    )
    char = ctx.state["characters"].get(char_id)
    if char is None:
        return False, "character not in state"
    actual_raw = cast("dict[str, object]", char).get(field)
    # `present` is a bool in state but is written `== true` in conditions, so it
    # is rendered rather than str()'d — otherwise the condition would have to
    # say `== True`, which reads like Python instead of like content.
    actual = ("true" if actual_raw else "false") if field == "present" else str(actual_raw)
    passed = actual == value if op == "==" else actual != value
    return passed, f"{char_id}.{field}={actual}"


def _h_char_num(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    char_id, field = m.group("char"), m.group("field")
    char = ctx.state["characters"].get(char_id)
    if char is None:
        return False, "character not in state"
    actual = int(cast("int", cast("dict[str, object]", char).get(field, 0)))
    return _num_compare(actual, m.group("op"), int(m.group("value")), f"{char_id}.{field}")


def _h_chance(m: re.Match[str], ctx: ConditionContext) -> tuple[bool, str]:
    probability = float(m.group("p"))
    if ctx.rng is None:
        raise ConditionError("chance() used without an RNG in the context")
    roll = ctx.rng.random()
    return roll < probability, f"roll={roll:.3f} < {probability}"


_HANDLERS: tuple[tuple[re.Pattern[str], Handler], ...] = (
    (
        re.compile(r"(?P<field>day|calendar_day)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>-?\d+)"),
        _h_day,
    ),
    (
        re.compile(
            r"(?P<field>location|weather|month|time_slot)\s*(?P<op>==|!=)\s*(?P<value>[A-Za-z_][A-Za-z0-9_]*)"
        ),
        _h_world_str,
    ),
    (
        re.compile(
            r"(?P<field>location|weather|time_slot)\s+in\s+(?P<values>[A-Za-z_][A-Za-z0-9_,\s]*)"
        ),
        _h_world_in,
    ),
    (re.compile(r"phase\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>[a-z_]+)"), _h_phase),
    (
        re.compile(
            rf"rel\s+(?:(?P<source>{_IDENT})->)?(?P<target>{_IDENT})\.(?P<axis>{_IDENT})"
            r"\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>-?\d+)"
        ),
        _h_rel,
    ),
    (
        re.compile(rf"trait\s+(?P<axis>{_IDENT})\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>-?\d+)"),
        _h_trait,
    ),
    (
        re.compile(rf"flag\s+(?P<name>{_IDENT})\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>-?\d+)"),
        _h_flag,
    ),
    (re.compile(rf"knows\(\s*(?P<fact>{_IDENT})\s*\)"), _h_knows),
    (re.compile(rf"suspects\(\s*(?P<fact>{_IDENT})\s*\)"), _h_suspects),
    (re.compile(rf"npc_knows\(\s*(?P<agent>{_IDENT})\s*,\s*(?P<fact>{_IDENT})\s*\)"), _h_npc_knows),
    (
        re.compile(
            rf"stance\(\s*(?P<agent>{_IDENT})\s*,\s*(?P<fact>{_IDENT})\s*\)"
            r"\s*(?P<op>==|!=)\s*(?P<value>[a-z_]+)"
        ),
        _h_stance,
    ),
    (re.compile(rf"seen\(\s*(?P<sid>{_IDENT})\s*\)"), _h_seen),
    (re.compile(rf"not_seen\(\s*(?P<sid>{_IDENT})\s*\)"), _h_not_seen),
    (
        re.compile(
            rf"seen_count\(\s*(?P<sid>{_IDENT})\s*\)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>\d+)"
        ),
        _h_seen_count,
    ),
    (
        re.compile(
            rf"days_since\(\s*(?P<sid>{_IDENT})\s*\)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>\d+)"
        ),
        _h_days_since,
    ),
    (re.compile(rf"has_item\(\s*(?P<item>{_IDENT})\s*\)"), _h_has_item),
    (re.compile(rf"anchor_done\(\s*(?P<anchor>{_IDENT})\s*\)"), _h_anchor_done),
    (
        re.compile(rf"commitment\(\s*(?P<cid>{_IDENT})\s*\)\s*(?P<op>==|!=)\s*(?P<value>[a-z_]+)"),
        _h_commitment,
    ),
    (
        re.compile(
            rf"broken_weight\(\s*(?P<who>{_IDENT})?\s*\)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>\d+)"
        ),
        _h_broken_weight,
    ),
    (
        re.compile(
            rf"char\s+(?P<char>{_IDENT})\.(?P<field>availability)"
            r"\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<value>-?\d+)"
        ),
        _h_char_num,
    ),
    (
        re.compile(
            rf"char\s+(?P<char>{_IDENT})\.(?P<field>present|mood|location|goal)"
            r"\s*(?P<op>==|!=)\s*(?P<value>[A-Za-z_][A-Za-z0-9_]*)"
        ),
        _h_char,
    ),
    (re.compile(r"chance\(\s*(?P<p>0?\.\d+|1\.0|0|1)\s*\)"), _h_chance),
)


#: Maps each condition form to the content ids it references, so the validator
#: can check them without duplicating the grammar.
_REFERENCE_PATTERNS: tuple[tuple[re.Pattern[str], dict[str, str]], ...] = tuple(
    (pattern, kinds)
    for pattern, kinds in (
        (_HANDLERS[1][0], {"value": "location_or_enum"}),
        (_HANDLERS[4][0], {"source": "character", "target": "character", "axis": "rel_axis"}),
        (_HANDLERS[5][0], {"axis": "trait_axis"}),
        (_HANDLERS[7][0], {"fact": "knowledge"}),
        (_HANDLERS[8][0], {"fact": "knowledge"}),
        (_HANDLERS[9][0], {"agent": "character", "fact": "knowledge"}),
        (_HANDLERS[10][0], {"agent": "character", "fact": "knowledge", "value": "stance"}),
        (_HANDLERS[11][0], {"sid": "storylet"}),
        (_HANDLERS[12][0], {"sid": "storylet"}),
        (_HANDLERS[13][0], {"sid": "storylet"}),
        (_HANDLERS[14][0], {"sid": "storylet"}),
        (_HANDLERS[15][0], {"item": "item"}),
        (_HANDLERS[16][0], {"anchor": "anchor"}),
        (_HANDLERS[18][0], {"who": "character"}),
        (_HANDLERS[19][0], {"char": "character"}),
        (_HANDLERS[20][0], {"char": "character"}),
    )
)
