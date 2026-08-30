"""Loading authored content from ``data/`` into an immutable library.

Content lives in JSON, one file per entity, because that is what makes it
diffable, schema-checkable and reviewable one storylet at a time. Prose does
*not* live here -- it lives in ``.rpy`` files where writers can read it. See
``docs/decisions/ADR-0006-storylet-metadata.md``.

This module does structural loading only. Cross-reference checking (does this
storylet name a character that exists?) belongs to ``s32tools.validation``,
which runs in CI and has jsonschema available; the engine must stay
dependency-free so Ren'Py can import it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from s32_engine.effects import granted_knowledge
from s32_engine.errors import ContentError
from s32_engine.types import (
    AnchorDef,
    CharacterDef,
    ContentLibrary,
    ContentTag,
    ItemDef,
    KnowledgeDef,
    LocationDef,
    Phase,
    StoryletDef,
    TimeSlot,
)

#: Directory names under ``data/``, in load order.
STORYLET_DIR = "storylets"
ANCHOR_DIR = "anchors"


def load_library(data_root: str | Path) -> ContentLibrary:
    """Load every content file under ``data_root`` into a library.

    Args:
        data_root: Path to the repository's ``data/`` directory.

    Returns:
        A populated, read-only :class:`ContentLibrary`.

    Raises:
        ContentError: On malformed JSON, a missing required field, or a
            duplicate id across files.
    """
    root = Path(data_root)
    if not root.is_dir():
        raise ContentError(f"data directory not found: {root}")

    return ContentLibrary(
        characters={c.id: c for c in _load_all(root / "characters", _character)},
        locations={loc.id: loc for loc in _load_all(root / "locations", _location)},
        knowledge={k.id: k for k in _load_all(root / "knowledge", _knowledge)},
        items={i.id: i for i in _load_all(root / "items", _item)},
        storylets={s.id: s for s in _load_all(root / STORYLET_DIR, _storylet)},
        anchors={a.id: a for a in _load_all(root / ANCHOR_DIR, _anchor)},
    )


def _load_all(directory: Path, build: Any) -> list[Any]:
    """Load and build every ``*.json`` file in a directory, sorted by name."""
    if not directory.is_dir():
        return []

    seen: dict[str, Path] = {}
    result: list[Any] = []
    for path in sorted(directory.rglob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ContentError(f"{path}: invalid JSON: {exc}") from exc
        if not isinstance(raw, dict):
            raise ContentError(f"{path}: expected a JSON object at the top level")

        entity = build(raw, path)
        if entity.id in seen:
            raise ContentError(
                f"duplicate id {entity.id!r}: defined in {seen[entity.id]} and again in {path}"
            )
        seen[entity.id] = path
        result.append(entity)
    return result


def _require(raw: dict[str, Any], key: str, path: Path) -> Any:
    """Fetch a required field or fail with the offending file named."""
    if key not in raw:
        raise ContentError(f"{path}: missing required field {key!r}")
    return raw[key]


def _tuple(raw: dict[str, Any], key: str) -> tuple[str, ...]:
    """Read an optional list-of-strings field as a tuple."""
    value = raw.get(key) or []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return tuple(str(v) for v in value)


def _character(raw: dict[str, Any], path: Path) -> CharacterDef:
    return CharacterDef(
        id=_require(raw, "id", path),
        display_name=_require(raw, "display_name", path),
        role=raw.get("role", ""),
        asset_id=raw.get("asset_id"),
        romanceable=bool(raw.get("romanceable", False)),
        tags=_tuple(raw, "tags"),
        notes=raw.get("notes", ""),
    )


def _location(raw: dict[str, Any], path: Path) -> LocationDef:
    return LocationDef(
        id=_require(raw, "id", path),
        display_name=_require(raw, "display_name", path),
        area=raw.get("area", ""),
        indoor=bool(raw.get("indoor", True)),
        background=raw.get("background"),
        tags=_tuple(raw, "tags"),
    )


def _knowledge(raw: dict[str, Any], path: Path) -> KnowledgeDef:
    return KnowledgeDef(
        id=_require(raw, "id", path),
        summary=_require(raw, "summary", path),
        category=raw.get("category", "general"),
        contradicts=_tuple(raw, "contradicts"),
        reveals_phase=raw.get("reveals_phase"),
        tags=_tuple(raw, "tags"),
    )


def _item(raw: dict[str, Any], path: Path) -> ItemDef:
    return ItemDef(
        id=_require(raw, "id", path),
        display_name=_require(raw, "display_name", path),
        kind=raw.get("kind", "object"),
        description=raw.get("description", ""),
        grants=_tuple(raw, "grants"),
        tags=_tuple(raw, "tags"),
    )


def _outcomes(raw: dict[str, Any], path: Path) -> tuple[tuple[str, ...], ...]:
    """Read the optional per-choice effect sets."""
    value = raw.get("outcomes") or []
    if not isinstance(value, list):
        raise ContentError(f"{path}: outcomes must be a list of effect lists")
    result: list[tuple[str, ...]] = []
    for index, branch in enumerate(value):
        if not isinstance(branch, list):
            raise ContentError(f"{path}: outcomes[{index}] must be a list of effect strings")
        result.append(tuple(str(effect) for effect in branch))
    return tuple(result)


def _storylet(raw: dict[str, Any], path: Path) -> StoryletDef:
    effects = _tuple(raw, "effects")
    outcomes = _outcomes(raw, path)
    declared_grants = _tuple(raw, "grants")
    # `grants` is derived from the effects when the author leaves it out, so the
    # common case has no duplication. It covers the unconditional effects AND
    # every choice outcome: a fact the player can obtain by picking option two
    # is still a fact this storylet can grant. An explicit list remains allowed
    # for the rare scene whose grant is buried in .rpy logic the analyser cannot
    # see.
    all_effects = effects + tuple(e for branch in outcomes for e in branch)
    grants = declared_grants or tuple(sorted(granted_knowledge(all_effects)))

    return StoryletDef(
        id=_require(raw, "id", path),
        label=_require(raw, "label", path),
        title=raw.get("title", raw["id"]),
        category=raw.get("category", "conversation"),
        status=raw.get("status", "prototype"),
        characters=_tuple(raw, "characters"),
        location=raw.get("location"),
        # The enum values come from JSON and are checked by the generated JSON
        # Schema, not by the loader; casting here says so explicitly rather
        # than re-validating what CI already guarantees.
        time_slots=cast("tuple[TimeSlot, ...]", _tuple(raw, "time_slots")),
        phases=cast("tuple[Phase, ...]", _tuple(raw, "phases")),
        tags=cast("tuple[ContentTag, ...]", _tuple(raw, "tags")),
        priority=int(raw.get("priority", 50)),
        weight=float(raw.get("weight", 1.0)),
        requirements=_tuple(raw, "requirements"),
        blockers=_tuple(raw, "blockers"),
        effects=effects,
        outcomes=outcomes,
        grants=grants,
        cooldown=int(raw.get("cooldown", 0)),
        repeat_policy=raw.get("repeat_policy", "once"),
        anchor=raw.get("anchor"),
        summary=raw.get("summary", ""),
        source_path=str(path),
    )


def _anchor(raw: dict[str, Any], path: Path) -> AnchorDef:
    effects = _tuple(raw, "effects")
    outcomes = _outcomes(raw, path)
    all_effects = effects + tuple(e for branch in outcomes for e in branch)
    return AnchorDef(
        id=_require(raw, "id", path),
        label=_require(raw, "label", path),
        title=raw.get("title", raw["id"]),
        order=int(_require(raw, "order", path)),
        phase=raw.get("phase", "normal"),
        requirements=_tuple(raw, "requirements"),
        effects=effects,
        outcomes=outcomes,
        grants=_tuple(raw, "grants") or tuple(sorted(granted_knowledge(all_effects))),
        summary=raw.get("summary", ""),
        source_path=str(path),
    )
