"""JSON Schema generation for authored content.

The schemas are **generated**, not hand-written, and the generator reads the
enum tuples out of :mod:`s32_engine.types`. That is the whole point: a schema
maintained by hand drifts from the code within a month, and the failure mode is
content that validates in CI and crashes in the game.

Draft 2020-12 is used throughout. It is the current published draft, and
``jsonschema`` implements it fully.

Regenerate with ``s32 schemas`` and commit the result; CI checks that the
committed files match what the generator produces.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from s32_engine.types import (
    COMMITMENT_STATUSES,
    CONTENT_STATUSES,
    CONTENT_TAGS,
    KNOWLEDGE_STANCES,
    PHASES,
    PRIORITY_MAX,
    PRIORITY_MIN,
    REPEAT_POLICIES,
    STORYLET_CATEGORIES,
    TIME_SLOTS,
)

DRAFT = "https://json-schema.org/draft/2020-12/schema"
BASE_URI = "https://september32.invalid/schemas"

#: Content ids are lowercase snake_case with no leading digit. Enforced by
#: schema rather than convention because ids appear in save files and in the
#: condition language, where a stray capital or hyphen is a silent mismatch.
ID_PATTERN = "^[a-z][a-z0-9_]*$"

#: A Ren'Py label. Same shape, but conventionally prefixed ``s32_``.
LABEL_PATTERN = "^[a-z][a-z0-9_]*$"


def _id(description: str) -> dict[str, Any]:
    return {"type": "string", "pattern": ID_PATTERN, "description": description}


def _id_list(description: str) -> dict[str, Any]:
    return {
        "type": "array",
        "items": {"type": "string", "pattern": ID_PATTERN},
        "uniqueItems": True,
        "description": description,
    }


def _enum_list(values: tuple[str, ...], description: str) -> dict[str, Any]:
    return {
        "type": "array",
        "items": {"enum": list(values)},
        "uniqueItems": True,
        "description": description,
    }


def _expression_list(description: str) -> dict[str, Any]:
    # The grammar itself is checked by the engine's parser during
    # `s32 validate`; JSON Schema only guarantees the shape and rejects blanks.
    return {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
        "description": description,
    }


def character_schema() -> dict[str, Any]:
    """Schema for ``data/characters/*.json``."""
    return {
        "$schema": DRAFT,
        "$id": f"{BASE_URI}/character.schema.json",
        "title": "Character",
        "description": (
            "A character's narrative identity. Deliberately separate from any art "
            "asset: `asset_id` points at whichever sprite currently represents "
            "them, and changing it must never require touching the story."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "display_name", "role"],
        "properties": {
            "id": _id("Stable id used in conditions, effects and save files."),
            "display_name": {"type": "string", "minLength": 1},
            "role": {"type": "string"},
            "asset_id": {
                "oneOf": [{"type": "string", "pattern": "^[a-z0-9_]+$"}, {"type": "null"}],
                "description": (
                    "Asset identity from assets/catalog/assets.toml, or null for an art gap."
                ),
            },
            "romanceable": {"type": "boolean", "default": False},
            "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
            "notes": {"type": "string"},
        },
    }


def location_schema() -> dict[str, Any]:
    """Schema for ``data/locations/*.json``."""
    return {
        "$schema": DRAFT,
        "$id": f"{BASE_URI}/location.schema.json",
        "title": "Location",
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "display_name", "area"],
        "properties": {
            "id": _id("Stable location id, used by `location ==` conditions."),
            "display_name": {"type": "string", "minLength": 1},
            "area": {"type": "string", "minLength": 1},
            "indoor": {"type": "boolean", "default": True},
            "background": {
                "oneOf": [{"type": "string", "pattern": "^[a-z0-9_]+$"}, {"type": "null"}],
                "description": "Ren'Py image name. May reference an asset not yet installed.",
            },
            "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        },
    }


def knowledge_schema() -> dict[str, Any]:
    """Schema for ``data/knowledge/*.json``."""
    return {
        "$schema": DRAFT,
        "$id": f"{BASE_URI}/knowledge.schema.json",
        "title": "Knowledge fact",
        "description": (
            "One discrete fact agents may hold differing beliefs about. "
            f"Stances: {', '.join(KNOWLEDGE_STANCES)}."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "summary"],
        "properties": {
            "id": _id("Stable fact id, used by knows()/suspects()/know()."),
            "summary": {"type": "string", "minLength": 1},
            "category": {"type": "string"},
            "contradicts": _id_list("Facts that cannot be true at the same time as this one."),
            "reveals_phase": {"oneOf": [{"enum": list(PHASES)}, {"type": "null"}]},
            "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        },
    }


def item_schema() -> dict[str, Any]:
    """Schema for ``data/items/*.json``."""
    return {
        "$schema": DRAFT,
        "$id": f"{BASE_URI}/item.schema.json",
        "title": "Item",
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "display_name"],
        "properties": {
            "id": _id("Stable item id, used by item()/has_item()."),
            "display_name": {"type": "string", "minLength": 1},
            "kind": {"type": "string"},
            "description": {"type": "string"},
            "grants": _id_list("Knowledge facts holding this item implies."),
            "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        },
    }


def storylet_schema() -> dict[str, Any]:
    """Schema for ``data/storylets/*.json``."""
    return {
        "$schema": DRAFT,
        "$id": f"{BASE_URI}/storylet.schema.json",
        "title": "Storylet",
        "description": (
            "Metadata for one pre-written scene. Contains no prose: `label` names "
            "the Ren'Py label that holds the writing."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "label", "category"],
        "properties": {
            "id": _id("Stable id. Once a storylet is `active`, this must not change."),
            "label": {
                "type": "string",
                "pattern": LABEL_PATTERN,
                "description": "Ren'Py label holding the scene. Convention: s32_st_<id>.",
            },
            "title": {
                "type": "string",
                "description": "Human title for reports and debug screens.",
            },
            "category": {"enum": list(STORYLET_CATEGORIES)},
            "status": {"enum": list(CONTENT_STATUSES), "default": "prototype"},
            "characters": _id_list("Characters who must be present for this to fire."),
            "location": {
                "oneOf": [{"type": "string", "pattern": ID_PATTERN}, {"type": "null"}],
                "description": "Required location, or null for anywhere.",
            },
            "time_slots": _enum_list(TIME_SLOTS, "Allowed slots. Empty means any."),
            "phases": _enum_list(PHASES, "Allowed escalation phases. Empty means any."),
            "tags": _enum_list(CONTENT_TAGS, "Content tags, used for the pacing budget report."),
            "priority": {
                "type": "integer",
                "minimum": PRIORITY_MIN,
                "maximum": PRIORITY_MAX,
                "default": 50,
                "description": "Hard tier. Only the highest-priority eligible storylets compete.",
            },
            "weight": {
                "type": "number",
                "exclusiveMinimum": 0,
                "default": 1.0,
                "description": "Relative likelihood within a priority tier, damped by repeats.",
            },
            "requirements": _expression_list("All must pass. See s32_engine.conditions."),
            "blockers": _expression_list("Any that passes blocks the storylet."),
            "effects": _expression_list("Applied after the scene plays. See s32_engine.effects."),
            "outcomes": {
                "type": "array",
                "items": _expression_list("One choice's effects."),
                "description": (
                    "Alternative effect sets the scene's own choices produce, in the "
                    "order the choices appear. Declare these: a state change that "
                    "exists only inside .rpy prose is invisible to validation, "
                    "reachability analysis and simulation, which will then report "
                    "any content depending on it as unreachable."
                ),
            },
            "grants": _id_list(
                "Knowledge granted. Derived from `effects` when omitted; set it "
                "explicitly only when the grant happens inside the .rpy label."
            ),
            "cooldown": {
                "type": "integer",
                "minimum": 0,
                "default": 0,
                "description": "Minimum days between repeats. Requires repeat_policy != once.",
            },
            "repeat_policy": {"enum": list(REPEAT_POLICIES), "default": "once"},
            "anchor": {
                "oneOf": [{"type": "string", "pattern": ID_PATTERN}, {"type": "null"}],
                "description": "Anchor this storylet belongs to, if any.",
            },
            "summary": {"type": "string", "description": "What this scene is for. Write it."},
        },
    }


def anchor_schema() -> dict[str, Any]:
    """Schema for ``data/anchors/*.json``."""
    return {
        "$schema": DRAFT,
        "$id": f"{BASE_URI}/anchor.schema.json",
        "title": "Anchor scene",
        "description": (
            "A dramatic beat that must happen, in order. Anchors carry structure; "
            "storylets fill the space between them."
        ),
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "label", "order", "phase"],
        "properties": {
            "id": _id("Stable anchor id, used by anchor_done()."),
            "label": {"type": "string", "pattern": LABEL_PATTERN},
            "title": {"type": "string"},
            "order": {"type": "integer", "minimum": 0, "description": "Strict ordering key."},
            "phase": {"enum": list(PHASES)},
            "requirements": _expression_list("Conditions for this anchor to become ready."),
            "effects": _expression_list("Applied when the anchor plays."),
            "outcomes": {
                "type": "array",
                "items": _expression_list("One choice's effects."),
                "description": (
                    "Per-choice effect sets, as on a storylet. Anchors carry most "
                    "of the early relationship movement; leaving these undeclared "
                    "makes later thresholds look unreachable."
                ),
            },
            "grants": _id_list("Knowledge granted. Derived from `effects` when omitted."),
            "summary": {"type": "string"},
        },
    }


#: Filename -> builder. Filenames match the ``data/`` subdirectory they govern.
SCHEMAS: dict[str, Any] = {
    "character.schema.json": character_schema,
    "location.schema.json": location_schema,
    "knowledge.schema.json": knowledge_schema,
    "item.schema.json": item_schema,
    "storylet.schema.json": storylet_schema,
    "anchor.schema.json": anchor_schema,
}

#: ``data/`` subdirectory -> schema filename.
DIRECTORY_SCHEMAS: dict[str, str] = {
    "characters": "character.schema.json",
    "locations": "location.schema.json",
    "knowledge": "knowledge.schema.json",
    "items": "item.schema.json",
    "storylets": "storylet.schema.json",
    "anchors": "anchor.schema.json",
}


def render(name: str) -> str:
    """Return the serialised schema text for one filename."""
    return json.dumps(SCHEMAS[name](), indent=2, ensure_ascii=False) + "\n"


def write_all(target: Path) -> list[Path]:
    """Write every schema into ``target``, creating it if needed."""
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name in sorted(SCHEMAS):
        path = target / name
        path.write_text(render(name), encoding="utf-8")
        written.append(path)
    return written


def check_all(target: Path) -> list[str]:
    """Return a list of schema files that are missing or out of date.

    Used by ``s32 validate`` and by CI, so that a change to an engine enum
    cannot be merged without the schemas being regenerated alongside it.
    """
    stale = []
    for name in sorted(SCHEMAS):
        path = target / name
        if not path.exists():
            stale.append(f"{name}: missing")
        elif path.read_text(encoding="utf-8") != render(name):
            stale.append(f"{name}: out of date")
    return stale


#: Extra enum tuples exported for documentation generators.
EXPORTED_ENUMS: dict[str, tuple[str, ...]] = {
    "time_slots": TIME_SLOTS,
    "phases": PHASES,
    "content_tags": CONTENT_TAGS,
    "storylet_categories": STORYLET_CATEGORIES,
    "repeat_policies": REPEAT_POLICIES,
    "content_statuses": CONTENT_STATUSES,
    "knowledge_stances": KNOWLEDGE_STANCES,
    "commitment_statuses": COMMITMENT_STATUSES,
}
