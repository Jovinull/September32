"""Relationship direction, which used to be implicit and used to be wrong.

Every authoring layer defaulted the source of a relationship edge to the player,
so ``rel iris.trust += 3`` stored the *player's* trust toward Iris. All 114
places the content used it meant the opposite -- Iris warming to the player in
response to something the player did -- and nothing caught it, because the only
two conditions that read a relationship read the same wrong edge and were
therefore consistent with the writes.

The fix is that there is no default any more, anywhere. These tests hold that:
the grammars refuse the old form by name, the Python API takes source before
target, and a save written under the old default is repaired on load.

docs/narrative-design/RELATIONSHIP_DIRECTION.md
"""

from __future__ import annotations

import json

import pytest

from s32_engine import conditions, effects, relationships
from s32_engine.conditions import ConditionContext
from s32_engine.errors import ConditionError, EffectError
from s32_engine.state import migrate_state, new_state
from s32_engine.version import SAVE_SCHEMA_VERSION
from s32tools import paths

# ---------------------------------------------------------------------------
# The grammars
# ---------------------------------------------------------------------------


def test_a_condition_without_a_direction_is_refused(state):
    with pytest.raises(ConditionError, match="ambiguous relationship direction"):
        conditions.evaluate("rel iris.trust >= 5", ConditionContext(state))


def test_an_effect_without_a_direction_is_refused(state):
    with pytest.raises(EffectError, match="ambiguous relationship direction"):
        effects.apply_effect("rel iris.trust += 5", state)


def test_the_refusal_names_both_directions(state):
    """A rejection that does not say what to write instead is a puzzle.

    Whoever hit this wrote one agent and meant one of two edges, and the tool
    knows which two they are.
    """
    with pytest.raises(ConditionError) as excinfo:
        conditions.evaluate("rel mara.suspicion >= 5", ConditionContext(state))
    message = str(excinfo.value)
    assert "player->mara.suspicion" in message
    assert "mara->player.suspicion" in message


def test_both_directions_are_independent(state):
    effects.apply_effect("rel iris->player.trust += 40", state)

    assert relationships.get(state, "iris", "player", "trust") == 40
    assert relationships.get(state, "player", "iris", "trust") == 0


def test_the_trace_shows_the_direction(state):
    """A debug line that reads ``iris->player.trust=0`` cannot be misread."""
    effects.apply_effect("rel iris->player.trust += 7", state)
    result = conditions.evaluate("rel iris->player.trust >= 5", ConditionContext(state))
    assert result.passed
    assert "iris->player.trust" in result.detail


def test_pair_strings_need_an_arrow():
    assert relationships.parse_pair("iris->player") == ("iris", "player")
    with pytest.raises(ValueError, match="needs an explicit direction"):
        relationships.parse_pair("iris")


# ---------------------------------------------------------------------------
# The content
# ---------------------------------------------------------------------------


def _relationship_expressions(library) -> list[tuple[str, str]]:
    """Return every ``(where, expression)`` mentioning a relationship."""
    found: list[tuple[str, str]] = []
    sources = [*library.storylets.values(), *library.anchors.values()]
    for source in sources:
        groups = [
            source.requirements,
            getattr(source, "blockers", ()),
            source.effects,
            *(branch for branch in source.outcomes),
        ]
        for group in groups:
            for text in group:
                if text.strip().startswith("rel "):
                    found.append((source.id, text.strip()))
    return found


def test_no_authored_relationship_omits_its_direction(real_library):
    """The migration, held.

    Checked over the real content rather than by grepping, so a scene that
    reaches the same expression by a different route is covered too.
    """
    bare = [
        (where, text) for where, text in _relationship_expressions(real_library) if "->" not in text
    ]
    assert not bare


def test_authored_relationships_name_real_agents(real_library):
    known = set(real_library.characters) | {"player"}
    for where, text in _relationship_expressions(real_library):
        pair = text.split()[1].split(".")[0]
        source, target = relationships.parse_pair(pair)
        assert source in known, f"{where}: {text}"
        assert target in known, f"{where}: {text}"
        assert source != target, f"{where}: {text}"


def test_the_prose_uses_the_same_arrow_notation():
    """The Ren'Py helper and the JSON grammar must not diverge.

    Two notations for one concept is how the direction gets lost again: a
    writer who has learned one reads the other as if it were the same.
    """
    import re

    call = re.compile(r'\brel(?:_get)?\(\s*"([^"]*)"')
    for path in sorted((paths.game_dir() / "story").rglob("*.rpy")):
        for pair in call.findall(path.read_text(encoding="utf-8")):
            assert "->" in pair, f"{path.name}: rel({pair!r}, ...) has no direction"


def test_documents_declare_direction_too():
    """Document view effects are effects, and were migrated with the rest."""
    from s32_engine.documents import load_documents

    for document in load_documents(paths.data_dir()).documents.values():
        for text in document.view_effects:
            if text.strip().startswith("rel "):
                assert "->" in text, f"{document.id}: {text}"


# ---------------------------------------------------------------------------
# Saves
# ---------------------------------------------------------------------------


def test_a_v2_save_has_its_edges_repaired(library):
    """The whole cast's feelings about the player were filed backwards.

    A save is not authoring syntax, so it cannot simply be declared wrong: the
    player earned those numbers. The v2 grammar had no way to express the
    player's own stance, so every ``player->x`` edge in an old save was written
    by the broken default and flipping is a lossless repair.
    """
    old = new_state(library, seed=1)
    old["relationships"]["player->iris"] = {"trust": 40, "familiarity": 12}
    old["relationships"]["mara->june"] = {"suspicion": 9}
    raw = json.loads(json.dumps(dict(old)))
    raw["save_schema_version"] = 2

    migrated = migrate_state(raw)

    assert migrated["save_schema_version"] == SAVE_SCHEMA_VERSION
    assert migrated["relationships"]["iris->player"]["trust"] == 40
    assert migrated["relationships"]["iris->player"]["familiarity"] == 12
    assert "player->iris" not in migrated["relationships"]
    # An NPC-to-NPC edge was never affected by the default and must not move.
    assert migrated["relationships"]["mara->june"]["suspicion"] == 9


def test_a_correct_edge_wins_over_a_flipped_one(library):
    """A save written by a build that already had both forms keeps the new one."""
    old = new_state(library, seed=1)
    old["relationships"]["player->iris"] = {"trust": 40}
    old["relationships"]["iris->player"] = {"trust": 7}
    raw = json.loads(json.dumps(dict(old)))
    raw["save_schema_version"] = 2

    migrated = migrate_state(raw)

    assert migrated["relationships"]["iris->player"]["trust"] == 7


def test_a_current_save_is_left_alone(library):
    state = new_state(library, seed=1)
    state["relationships"]["iris->player"] = {"trust": 5}
    raw = json.loads(json.dumps(dict(state)))

    migrated = migrate_state(raw)

    assert migrated["relationships"]["iris->player"]["trust"] == 5
    # `new_state` pre-seeds an empty vector per character; a current save is
    # not rewritten, so those stay exactly where they were.
    assert migrated["relationships"]["player->iris"]["trust"] == 0
