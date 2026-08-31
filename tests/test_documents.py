"""The archive document model.

The behaviour that matters is state, not pixels: does a document unlock when it
should, does its effect apply exactly once, does re-reading cost nothing, and
does the save migration that carries the read-list actually run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from s32_engine import knowledge
from s32_engine.documents import (
    BLOCK_KINDS,
    has_read,
    is_unlocked,
    load_documents,
    mark_read,
    readable,
)
from s32_engine.errors import ContentError
from s32_engine.state import migrate_state, new_state
from s32_engine.version import SAVE_SCHEMA_VERSION
from s32tools import paths


@pytest.fixture
def docs(tmp_path: Path):
    """A small synthetic document library covering the features that exist."""
    directory = tmp_path / "documents"
    directory.mkdir()

    (directory / "open.json").write_text(
        json.dumps(
            {
                "id": "open",
                "type": "catalogue_record",
                "title": "Always readable",
                "pages": [{"blocks": [{"kind": "heading", "text": "OPEN"}]}],
            }
        ),
        encoding="utf-8",
    )
    (directory / "locked.json").write_text(
        json.dumps(
            {
                "id": "locked",
                "type": "ledger_page",
                "title": "Needs a fact",
                "unlock_conditions": ["knows(photo)"],
                "view_effects": ["rel iris->player.trust += 3", "know(date, the_document)"],
                "pages": [
                    {"blocks": [{"kind": "date", "text": "14 SEPTEMBER"}]},
                    {"blocks": [{"kind": "date", "text": ""}]},
                ],
            }
        ),
        encoding="utf-8",
    )
    return load_documents(tmp_path)


def test_documents_load_with_pages_and_blocks(docs):
    assert set(docs.ids()) == {"locked", "open"}
    assert docs.documents["locked"].page_count == 2
    assert docs.documents["open"].pages[0].blocks[0].kind == "heading"


def test_an_absent_directory_is_not_an_error(tmp_path: Path):
    """A project with no documents is a valid project."""
    assert load_documents(tmp_path).documents == {}


def test_an_unlocked_document_is_readable(state, docs):
    assert is_unlocked(state, docs.documents["open"])


def test_a_locked_document_stays_locked(state, docs):
    assert not is_unlocked(state, docs.documents["locked"])
    knowledge.grant(state, "photo")
    assert is_unlocked(state, docs.documents["locked"])


def test_readable_lists_only_what_is_unlocked(state, docs):
    assert [d.id for d in readable(state, docs)] == ["open"]
    knowledge.grant(state, "photo")
    assert [d.id for d in readable(state, docs)] == ["locked", "open"]


def test_first_reading_applies_the_effects(state, docs):
    from s32_engine import relationships

    changes = mark_read(state, docs.documents["locked"])

    assert has_read(state, "locked")
    assert relationships.get(state, "iris", "player", "trust") == 3
    assert knowledge.knows(state, "date")
    assert len(changes) == 2


def test_re_reading_changes_nothing(state, docs):
    """Re-reading is free.

    An archive the player is punished for revisiting is one they stop revisiting.
    """
    from s32_engine import relationships

    mark_read(state, docs.documents["locked"])
    for _ in range(5):
        assert mark_read(state, docs.documents["locked"]) == []

    assert relationships.get(state, "iris", "player", "trust") == 3
    assert state["documents_read"].count("locked") == 1


def test_reading_order_is_preserved(state, docs):
    mark_read(state, docs.documents["locked"])
    mark_read(state, docs.documents["open"])
    assert state["documents_read"] == ["locked", "open"]


def test_a_fresh_state_has_read_nothing(library):
    assert new_state(library, seed=1)["documents_read"] == []


def test_a_v1_save_gains_the_read_list(library):
    """The first real save migration.

    A save written before the viewer existed has read nothing, so an empty list
    is correct rather than a lossy default.
    """
    old = dict(new_state(library, seed=1))
    old["save_schema_version"] = 1
    del old["documents_read"]

    migrated = migrate_state(old)

    assert migrated["documents_read"] == []
    assert migrated["save_schema_version"] == SAVE_SCHEMA_VERSION


def test_a_v1_save_with_data_keeps_everything_else(library):
    old: dict[str, Any] = dict(new_state(library, seed=1))
    old["save_schema_version"] = 1
    del old["documents_read"]
    old["inventory"].append("camera")

    migrated = migrate_state(old)

    assert migrated["inventory"] == ["camera"]
    assert migrated["documents_read"] == []


# ---------------------------------------------------------------------------
# Malformed content is refused loudly
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"id": "x", "type": "letter", "title": "t"}, "missing required field 'pages'"),
        ({"id": "x", "type": "letter", "title": "t", "pages": []}, "non-empty list"),
        (
            {
                "id": "x",
                "type": "letter",
                "title": "t",
                "pages": [{"blocks": [{"kind": "interpretive_dance"}]}],
            },
            "unknown kind",
        ),
    ],
)
def test_malformed_documents_name_the_problem(tmp_path: Path, payload, message):
    directory = tmp_path / "documents"
    directory.mkdir()
    (directory / "bad.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ContentError, match=message):
        load_documents(tmp_path)


def test_duplicate_ids_are_refused(tmp_path: Path):
    directory = tmp_path / "documents"
    directory.mkdir()
    for name in ("a.json", "b.json"):
        (directory / name).write_text(
            json.dumps(
                {
                    "id": "same",
                    "type": "letter",
                    "title": "t",
                    "pages": [{"blocks": []}],
                }
            ),
            encoding="utf-8",
        )

    with pytest.raises(ContentError, match="duplicate document id"):
        load_documents(tmp_path)


# ---------------------------------------------------------------------------
# The project's real documents
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def real_documents():
    return load_documents(paths.data_dir())


def test_the_real_documents_load(real_documents):
    assert len(real_documents.documents) >= 3


def test_every_document_uses_known_block_kinds(real_documents):
    for document in real_documents.documents.values():
        for page in document.pages:
            for block in page.blocks:
                assert block.kind in BLOCK_KINDS, f"{document.id}: {block.kind}"


def test_document_conditions_and_effects_parse(real_documents, real_library):
    """Conditions and effects must parse.

    A typo in an unlock condition would make a document silently unopenable.
    """
    from s32_engine.conditions import ConditionContext, evaluate
    from s32_engine.effects import _HANDLERS
    from s32_engine.rng import Rng

    probe = new_state(real_library, seed=0)
    ctx = ConditionContext(probe, Rng(probe))

    for document in real_documents.documents.values():
        for condition in document.unlock_conditions:
            evaluate(condition, ctx)
        for effect in document.view_effects:
            assert any(pattern.fullmatch(effect.strip()) for pattern, _ in _HANDLERS), (
                f"{document.id}: effect {effect!r} does not parse"
            )


def test_documents_only_reference_facts_that_exist(real_documents, real_library):
    from s32_engine import conditions, effects

    for document in real_documents.documents.values():
        for condition in document.unlock_conditions:
            for fact in conditions.referenced_ids(condition).get("knowledge", set()):
                assert fact in real_library.knowledge, f"{document.id}: {fact}"
        for effect in document.view_effects:
            for fact in effects.referenced_ids(effect).get("knowledge", set()):
                assert fact in real_library.knowledge, f"{document.id}: {fact}"


def test_the_class_photograph_is_still_a_declared_gap(real_documents):
    """The central image is NEEDS COMMISSION and must stay visibly absent.

    Substituting an unrelated photograph of real people, or generating one,
    would weaken one of the game's central objects to remove a TODO.
    See docs/production/ART_GAP_ANALYSIS.md.
    """
    card = real_documents.documents["photograph_card_unlisted"]
    placeholders = [
        block for page in card.pages for block in page.blocks if block.kind == "image_placeholder"
    ]
    assert placeholders, "the photograph card must declare its missing image"
    assert "PENDING" in placeholders[0].text.upper()


def test_documents_carry_no_baked_in_text(real_documents):
    """Text stays real text so it can be translated and read at any size."""
    for document in real_documents.documents.values():
        assert document.title
        for page in document.pages:
            for block in page.blocks:
                if block.kind in {"heading", "text", "field", "note"}:
                    assert block.text or block.label, f"{document.id}: empty {block.kind}"
