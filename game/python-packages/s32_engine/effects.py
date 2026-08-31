"""The effect mini-language storylets and choices use to change the world.

Like :mod:`s32_engine.conditions`, effects are short strings matched against a
fixed grammar rather than executed as Python. The payoff is the same: the static
analyser can read a storylet and know that it grants ``old_photo``, which is how
``s32 validate`` can report that a requirement nothing satisfies is unreachable.

Supported forms::

    rel player->iris.trust += 3    player -> iris, delta
    rel player->iris.trust -= 2
    rel player->iris.trust = 40    absolute (reserved for anchors)
    rel iris->theo.respect += 5    npc -> npc

    trait curious += 1
    flag archive_visits += 1
    flag lights_left_on = 1

    know(old_photo)                player now knows it
    know(old_photo, archive_box)   ... with a source tag
    suspect(old_photo)
    disprove(old_photo)
    npc_stance(iris, old_photo, suspected)

    item(old_camera)               add to inventory
    drop_item(old_camera)

    phase = unsettling
    weather = rain
    location = rooftop
    time += 1                      advance N time slots

    char iris.present = true
    char iris.mood = withdrawn
    char iris.availability += 10

    commit(meet_theo, theo, 1, 60) id, participant, days from now, importance
    fulfil(meet_theo)
    break(meet_theo)
    excuse(meet_theo)

    event(found_the_photo)         push onto the recent-event window
    anchor_done(arrival)
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import cast

from s32_engine import commitments, knowledge, relationships
from s32_engine.errors import EffectError
from s32_engine.state import (
    advance_time,
    bump_flag,
    note_event,
    set_flag,
    set_location,
)
from s32_engine.types import (
    PHASES,
    TRAIT_MAX,
    TRAIT_MIN,
    WEATHERS,
    GameState,
    Phase,
    RelationshipAxis,
    Weather,
)

_IDENT = r"[a-z_][a-z0-9_]*"


def apply_effect(effect: str, state: GameState) -> str:
    """Apply one effect string to the state.

    Returns:
        A short human description of what changed, for the debug log.

    Raises:
        EffectError: If the string does not match any supported form.
    """
    text = effect.strip()
    if not text:
        raise EffectError("empty effect")

    for pattern, handler in _HANDLERS:
        match = pattern.fullmatch(text)
        if match is not None:
            return handler(match, state)

    raise EffectError(f"unrecognised effect: {effect!r}")


def apply_all(effects: tuple[str, ...] | list[str], state: GameState) -> list[str]:
    """Apply effects in order and return the per-effect descriptions.

    Order matters and is preserved: an effect may legitimately depend on one
    written above it (grant a fact, then advance the phase that fact unlocks).
    """
    return [apply_effect(e, state) for e in effects]


def granted_knowledge(effects: tuple[str, ...] | list[str]) -> set[str]:
    """Return the knowledge ids these effects grant to the *player*.

    Static analysis depends on this: a requirement of ``knows(x)`` is
    unsatisfiable unless some storylet's effects appear in this set for ``x``.
    NPC-only stance changes are excluded, since they cannot satisfy a
    player-facing ``knows()``.
    """
    granted: set[str] = set()
    for effect in effects:
        match = _KNOW_PATTERN.fullmatch(effect.strip())
        if match is not None:
            granted.add(match.group("fact"))
    return granted


def referenced_ids(effect: str) -> dict[str, set[str]]:
    """Return the content ids an effect refers to, grouped by kind."""
    text = effect.strip()
    found: dict[str, set[str]] = {}
    for pattern, kinds in _REFERENCE_PATTERNS:
        match = pattern.fullmatch(text)
        if match is None:
            continue
        for group, kind in kinds.items():
            value = match.groupdict().get(group)
            if value:
                found.setdefault(kind, set()).add(value)
        break
    return found


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

Handler = Callable[[re.Match[str], GameState], str]


def _h_rel_no_direction(m: re.Match[str], state: GameState) -> str:
    """Reject the old direction-less form, by name, with the fix in the message.

    ``rel iris.trust += 3`` used to mean the *player's* trust toward Iris,
    defaulting the source. It read to most people as Iris trusting the player
    more, which is the opposite, and the notation gave a reader nothing to check
    against. Both directions must now be written.
    """
    del state
    target, axis, op = m.group("target"), m.group("axis"), m.group("op")
    raise EffectError(
        f"ambiguous relationship direction in 'rel {target}.{axis} {op} ...': "
        f"write 'rel player->{target}.{axis}' for the player's stance toward "
        f"{target}, or 'rel {target}->player.{axis}' for theirs toward the player"
    )


def _h_rel(m: re.Match[str], state: GameState) -> str:
    source = m.group("source")
    target, axis, op, value = (
        m.group("target"),
        m.group("axis"),
        m.group("op"),
        int(m.group("value")),
    )
    if op == "=":
        result = relationships.set_axis(
            state, source, target, cast("RelationshipAxis", axis), value
        )
    else:
        delta = value if op == "+=" else -value
        result = relationships.change(state, source, target, cast("RelationshipAxis", axis), delta)
    return f"{source}->{target}.{axis}={result}"


def _h_trait(m: re.Match[str], state: GameState) -> str:
    axis, op, value = m.group("axis"), m.group("op"), int(m.group("value"))
    current = state["traits"].get(axis, 0)
    new = value if op == "=" else current + (value if op == "+=" else -value)
    state["traits"][axis] = max(TRAIT_MIN, min(TRAIT_MAX, new))
    return f"trait.{axis}={state['traits'][axis]}"


def _h_flag(m: re.Match[str], state: GameState) -> str:
    name, op, value = m.group("name"), m.group("op"), int(m.group("value"))
    if op == "=":
        set_flag(state, name, value)
        result = value
    else:
        result = bump_flag(state, name, value if op == "+=" else -value)
    return f"flag.{name}={result}"


def _h_know(m: re.Match[str], state: GameState) -> str:
    fact = m.group("fact")
    source = m.group("source") or ""
    knowledge.grant(state, fact, source=source)
    return f"know({fact})"


def _h_suspect(m: re.Match[str], state: GameState) -> str:
    fact = m.group("fact")
    knowledge.suspect(state, fact, source=m.group("source") or "")
    return f"suspect({fact})"


def _h_disprove(m: re.Match[str], state: GameState) -> str:
    fact = m.group("fact")
    knowledge.disprove(state, fact, source=m.group("source") or "")
    return f"disprove({fact})"


def _h_npc_stance(m: re.Match[str], state: GameState) -> str:
    agent, fact, target = m.group("agent"), m.group("fact"), m.group("stance")
    result = knowledge.set_stance(state, fact, target, agent=agent)  # type: ignore[arg-type]
    return f"{agent}:{fact}={result}"


def _h_item(m: re.Match[str], state: GameState) -> str:
    item = m.group("item")
    if item not in state["inventory"]:
        state["inventory"].append(item)
    return f"item+{item}"


def _h_drop_item(m: re.Match[str], state: GameState) -> str:
    item = m.group("item")
    if item in state["inventory"]:
        state["inventory"].remove(item)
    return f"item-{item}"


def _h_phase(m: re.Match[str], state: GameState) -> str:
    value = m.group("value")
    if value not in PHASES:
        raise EffectError(f"unknown phase: {value!r}")
    # Phase only ever moves forward. A scene that lowers it is almost certainly
    # an authoring mistake, and silently allowing it would let a late-game
    # storylet drag the whole run back to `normal`.
    current = state["world"]["phase"]
    if PHASES.index(value) < PHASES.index(current):
        raise EffectError(f"phase cannot move backwards: {current} -> {value}")
    state["world"]["phase"] = cast("Phase", value)
    return f"phase={value}"


def _h_weather(m: re.Match[str], state: GameState) -> str:
    value = m.group("value")
    if value not in WEATHERS:
        raise EffectError(f"unknown weather: {value!r}")
    state["world"]["weather"] = cast("Weather", value)
    return f"weather={value}"


def _h_location(m: re.Match[str], state: GameState) -> str:
    set_location(state, m.group("value"))
    return f"location={m.group('value')}"


def _h_time(m: re.Match[str], state: GameState) -> str:
    slots = int(m.group("value"))
    advance_time(state, slots)
    world = state["world"]
    return f"time=day {world['day']} {world['time_slot']}"


def _h_char_set(m: re.Match[str], state: GameState) -> str:
    char_id, field, value = m.group("char"), m.group("field"), m.group("value")
    char = state["characters"].get(char_id)
    if char is None:
        raise EffectError(f"unknown character in effect: {char_id!r}")
    if field == "present":
        char["present"] = value == "true"
    else:
        # `field` is validated by the grammar, but mypy cannot narrow a runtime
        # string to a TypedDict key. The cast is where that gap is stated.
        fields = cast("dict[str, object]", char)
        fields[field] = value
    return f"{char_id}.{field}={value}"


def _h_char_num(m: re.Match[str], state: GameState) -> str:
    char_id, field, op, value = (
        m.group("char"),
        m.group("field"),
        m.group("op"),
        int(m.group("value")),
    )
    char = state["characters"].get(char_id)
    if char is None:
        raise EffectError(f"unknown character in effect: {char_id!r}")
    fields = cast("dict[str, object]", char)
    current = int(cast("int", fields.get(field, 0)))
    new = max(0, min(100, value if op == "=" else current + (value if op == "+=" else -value)))
    fields[field] = new
    return f"{char_id}.{field}={new}"


def _h_commit(m: re.Match[str], state: GameState) -> str:
    cid = m.group("cid")
    participant = m.group("who")
    days = int(m.group("days"))
    importance = int(m.group("importance") or 50)
    commitments.make(
        state,
        cid,
        kind=m.group("kind") or "meeting",
        participants=[participant],
        due_day=state["world"]["day"] + days,
        importance=importance,
    )
    return f"commit({cid}) due day {state['world']['day'] + days}"


def _h_commit_resolve(m: re.Match[str], state: GameState) -> str:
    verb, cid = m.group("verb"), m.group("cid")
    handler = {
        "fulfil": commitments.fulfil,
        "break": commitments.break_,
        "excuse": commitments.excuse,
    }[verb]
    handler(state, cid)
    return f"{verb}({cid})"


def _h_event(m: re.Match[str], state: GameState) -> str:
    note_event(state, m.group("name"))
    return f"event({m.group('name')})"


def _h_anchor_done(m: re.Match[str], state: GameState) -> str:
    anchor = m.group("anchor")
    if anchor not in state["anchors_done"]:
        state["anchors_done"].append(anchor)
    return f"anchor_done({anchor})"


_KNOW_PATTERN = re.compile(rf"know\(\s*(?P<fact>{_IDENT})\s*(?:,\s*(?P<source>{_IDENT})\s*)?\)")

_HANDLERS: tuple[tuple[re.Pattern[str], Handler], ...] = (
    (
        re.compile(
            rf"rel\s+(?P<source>{_IDENT})->(?P<target>{_IDENT})\.(?P<axis>{_IDENT})"
            r"\s*(?P<op>\+=|-=|=)\s*(?P<value>-?\d+)"
        ),
        _h_rel,
    ),
    # Must come after the explicit form, and exists only to fail usefully.
    (
        re.compile(
            rf"rel\s+(?P<target>{_IDENT})\.(?P<axis>{_IDENT})"
            r"\s*(?P<op>\+=|-=|=)\s*(?P<value>-?\d+)"
        ),
        _h_rel_no_direction,
    ),
    (re.compile(rf"trait\s+(?P<axis>{_IDENT})\s*(?P<op>\+=|-=|=)\s*(?P<value>-?\d+)"), _h_trait),
    (re.compile(rf"flag\s+(?P<name>{_IDENT})\s*(?P<op>\+=|-=|=)\s*(?P<value>-?\d+)"), _h_flag),
    (_KNOW_PATTERN, _h_know),
    (
        re.compile(rf"suspect\(\s*(?P<fact>{_IDENT})\s*(?:,\s*(?P<source>{_IDENT})\s*)?\)"),
        _h_suspect,
    ),
    (
        re.compile(rf"disprove\(\s*(?P<fact>{_IDENT})\s*(?:,\s*(?P<source>{_IDENT})\s*)?\)"),
        _h_disprove,
    ),
    (
        re.compile(
            rf"npc_stance\(\s*(?P<agent>{_IDENT})\s*,\s*(?P<fact>{_IDENT})\s*,"
            rf"\s*(?P<stance>{_IDENT})\s*\)"
        ),
        _h_npc_stance,
    ),
    (re.compile(rf"item\(\s*(?P<item>{_IDENT})\s*\)"), _h_item),
    (re.compile(rf"drop_item\(\s*(?P<item>{_IDENT})\s*\)"), _h_drop_item),
    (re.compile(r"phase\s*=\s*(?P<value>[a-z_]+)"), _h_phase),
    (re.compile(r"weather\s*=\s*(?P<value>[a-z_]+)"), _h_weather),
    (re.compile(rf"location\s*=\s*(?P<value>{_IDENT})"), _h_location),
    (re.compile(r"time\s*\+=\s*(?P<value>\d+)"), _h_time),
    (
        re.compile(
            rf"char\s+(?P<char>{_IDENT})\.(?P<field>availability)\s*(?P<op>\+=|-=|=)\s*(?P<value>-?\d+)"
        ),
        _h_char_num,
    ),
    (
        re.compile(
            rf"char\s+(?P<char>{_IDENT})\.(?P<field>present|mood|location|goal)"
            rf"\s*=\s*(?P<value>{_IDENT}|true|false)"
        ),
        _h_char_set,
    ),
    (
        re.compile(
            rf"commit\(\s*(?P<cid>{_IDENT})\s*,\s*(?P<who>{_IDENT})\s*,\s*(?P<days>\d+)"
            rf"(?:\s*,\s*(?P<importance>\d+))?(?:\s*,\s*(?P<kind>{_IDENT}))?\s*\)"
        ),
        _h_commit,
    ),
    (re.compile(rf"(?P<verb>fulfil|break|excuse)\(\s*(?P<cid>{_IDENT})\s*\)"), _h_commit_resolve),
    (re.compile(rf"event\(\s*(?P<name>{_IDENT})\s*\)"), _h_event),
    (re.compile(rf"anchor_done\(\s*(?P<anchor>{_IDENT})\s*\)"), _h_anchor_done),
)


#: Keyed by handler rather than by position in ``_HANDLERS``. An earlier
#: version indexed the tuple, which meant inserting one pattern silently
#: re-pointed every entry after it at the wrong grammar.
def _pattern_for(handler: Handler) -> re.Pattern[str]:
    """Return the first pattern bound to ``handler``."""
    for pattern, bound in _HANDLERS:
        if bound is handler:
            return pattern
    raise KeyError(handler)


_REFERENCE_PATTERNS: tuple[tuple[re.Pattern[str], dict[str, str]], ...] = tuple(
    (_pattern_for(handler), kinds)
    for handler, kinds in (
        (_h_rel, {"source": "character", "target": "character", "axis": "rel_axis"}),
        (_h_trait, {"axis": "trait_axis"}),
        (_h_know, {"fact": "knowledge"}),
        (_h_suspect, {"fact": "knowledge"}),
        (_h_disprove, {"fact": "knowledge"}),
        (_h_npc_stance, {"agent": "character", "fact": "knowledge", "stance": "stance"}),
        (_h_item, {"item": "item"}),
        (_h_drop_item, {"item": "item"}),
        (_h_location, {"value": "location"}),
        (_h_char_num, {"char": "character"}),
        (_h_char_set, {"char": "character"}),
        (_h_commit, {"who": "character"}),
        (_h_anchor_done, {"anchor": "anchor"}),
    )
)
