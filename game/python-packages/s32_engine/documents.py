"""Archive documents: inspectable artefacts, distinct from scenes and from facts.

Three things the project keeps apart on purpose:

``storylet``
    A narrative event. It happens, it has effects, it is over.
``document``
    An object the player can pick up and read, repeatedly, at any time.
``knowledge``
    What somebody believes. A document may *cause* a belief; it is not one.

Opening a document may have a story effect. That does not make it a storylet, and
conflating the two would mean the archive's contents could only be examined at
the moment a scene offered them — which is the opposite of what an archive is.

A document is authored as data (``data/documents/*.json``) for the same reason a
storylet is: so the tooling can check it. Its **effects are declared**, and they
apply exactly once, the first time the player reads it. That constraint is why
this module exists at all rather than the viewer screen simply calling
``learn()``: a change the tooling cannot see makes later content look dead, and
that has already happened twice in this project.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from s32_engine.errors import ContentError
from s32_engine.types import GameState

#: The block kinds a page may contain.
#:
#: Deliberately few. This is a document renderer, not a publishing engine — a
#: kind is added when a document needs it, and `image_placeholder` exists
#: precisely so that art which does not exist yet is visibly absent rather than
#: quietly substituted.
BlockKind = Literal[
    "heading",
    "text",
    "field",
    "date",
    "stamp",
    "separator",
    "note",
    "image_placeholder",
]
BLOCK_KINDS: tuple[BlockKind, ...] = (
    "heading",
    "text",
    "field",
    "date",
    "stamp",
    "separator",
    "note",
    "image_placeholder",
)

#: What kind of object a document is. Drives presentation -- the viewer picks a
#: paper stock and a layout from it -- and nothing else, so adding one is a
#: presentation decision rather than a model change.
DocumentType = Literal[
    "catalogue_record",
    "ledger_page",
    "photograph_card",
    "letter",
    "clipping",
    "works_docket",
    "transfer_card",
    "student_notice",
]
DOCUMENT_TYPES: tuple[DocumentType, ...] = (
    "catalogue_record",
    "ledger_page",
    "photograph_card",
    "letter",
    "clipping",
    "works_docket",
    "transfer_card",
    "student_notice",
)


@dataclass(frozen=True, slots=True)
class Block:
    """One element on a page.

    ``text`` carries the visible content and stays a plain string so that it
    participates in translation. ``label`` is the left-hand side of a ``field``
    row. Nothing here is baked into a raster image: a document whose words live
    only in a picture cannot be translated or read by a screen reader.
    """

    kind: BlockKind
    text: str = ""
    label: str = ""


@dataclass(frozen=True, slots=True)
class Page:
    """One side of one piece of paper."""

    blocks: tuple[Block, ...] = ()


@dataclass(frozen=True, slots=True)
class DocumentDef:
    """An archive item the player can open and read.

    ``fictional_source`` and the asset that renders it are different things and
    are never conflated: the first is where the object came from in the story,
    the second is where the pixels came from. See
    ``docs/legal/ASSET_LICENSING.md``.
    """

    id: str
    type: DocumentType
    title: str
    pages: tuple[Page, ...]
    archive_reference: str = ""
    fictional_source: str = ""
    source_location: str | None = None
    unlock_conditions: tuple[str, ...] = ()
    view_effects: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    summary: str = ""
    source_path: str = ""

    @property
    def page_count(self) -> int:
        """Number of pages."""
        return len(self.pages)


@dataclass(frozen=True, slots=True)
class DocumentLibrary:
    """Every authored document, loaded once and read-only."""

    documents: dict[str, DocumentDef] = field(default_factory=dict)

    def ids(self) -> list[str]:
        """Return document ids in a stable order."""
        return sorted(self.documents)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_documents(data_root: str | Path) -> DocumentLibrary:
    """Load ``data/documents/*.json``.

    An absent directory is not an error: a project with no documents is a valid
    project, and the viewer simply has nothing to show.
    """
    directory = Path(data_root) / "documents"
    if not directory.is_dir():
        return DocumentLibrary()

    documents: dict[str, DocumentDef] = {}
    for path in sorted(directory.rglob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ContentError(f"{path}: invalid JSON: {exc}") from exc

        document = _document(raw, path)
        if document.id in documents:
            raise ContentError(f"duplicate document id {document.id!r} in {path}")
        documents[document.id] = document
    return DocumentLibrary(documents=documents)


def _document(raw: dict[str, object], path: Path) -> DocumentDef:
    """Build one document, naming the file on any problem."""
    for required in ("id", "type", "title", "pages"):
        if required not in raw:
            raise ContentError(f"{path}: missing required field {required!r}")

    pages_raw = raw["pages"]
    if not isinstance(pages_raw, list) or not pages_raw:
        raise ContentError(f"{path}: pages must be a non-empty list")

    pages: list[Page] = []
    for index, page_raw in enumerate(pages_raw):
        if not isinstance(page_raw, dict):
            raise ContentError(f"{path}: page {index} must be an object")
        blocks_raw = page_raw.get("blocks") or []
        if not isinstance(blocks_raw, list):
            raise ContentError(f"{path}: page {index} blocks must be a list")

        blocks: list[Block] = []
        for block_index, block_raw in enumerate(blocks_raw):
            if not isinstance(block_raw, dict):
                raise ContentError(f"{path}: page {index} block {block_index} must be an object")
            kind = block_raw.get("kind")
            if kind not in BLOCK_KINDS:
                raise ContentError(
                    f"{path}: page {index} block {block_index} has unknown kind {kind!r}; "
                    f"expected one of {', '.join(BLOCK_KINDS)}"
                )
            blocks.append(
                Block(
                    kind=kind,
                    text=str(block_raw.get("text", "")),
                    label=str(block_raw.get("label", "")),
                )
            )
        pages.append(Page(blocks=tuple(blocks)))

    def strings(key: str) -> tuple[str, ...]:
        value = raw.get(key) or []
        if not isinstance(value, list):
            raise ContentError(f"{path}: {key} must be a list")
        return tuple(str(item) for item in value)

    return DocumentDef(
        id=str(raw["id"]),
        type=raw["type"],  # type: ignore[arg-type]
        title=str(raw["title"]),
        pages=tuple(pages),
        archive_reference=str(raw.get("archive_reference", "")),
        fictional_source=str(raw.get("fictional_source", "")),
        source_location=raw.get("source_location"),  # type: ignore[arg-type]
        unlock_conditions=strings("unlock_conditions"),
        view_effects=strings("view_effects"),
        tags=strings("tags"),
        summary=str(raw.get("summary", "")),
        source_path=str(path),
    )


# ---------------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------------


def documents_read(state: GameState) -> list[str]:
    """Return the ids the player has already read, in order of first reading."""
    return state["documents_read"]


def has_read(state: GameState, document_id: str) -> bool:
    """Return whether this document has already been read."""
    return document_id in documents_read(state)


def is_unlocked(state: GameState, document: DocumentDef, rng: object = None) -> bool:
    """Return whether the player may open this document.

    A document with no ``unlock_conditions`` is always readable. Conditions use
    the same grammar as storylet requirements, so a document can be gated on
    knowledge, an item, a place or a prior scene without a second language.
    """
    from s32_engine.conditions import ConditionContext, evaluate

    if not document.unlock_conditions:
        return True
    ctx = ConditionContext(state, rng)  # type: ignore[arg-type]
    return all(evaluate(condition, ctx).passed for condition in document.unlock_conditions)


def mark_read(state: GameState, document: DocumentDef) -> list[str]:
    """Record a first reading and apply the document's effects, once.

    Returns:
        The effect descriptions applied, or an empty list if it had already been
        read. Re-reading a document is free and changes nothing — an archive the
        player is punished for revisiting is an archive they stop revisiting.
    """
    from s32_engine.effects import apply_all

    if has_read(state, document.id):
        return []

    documents_read(state).append(document.id)
    return apply_all(document.view_effects, state)


def readable(state: GameState, library: DocumentLibrary, rng: object = None) -> list[DocumentDef]:
    """Return every currently unlocked document, in stable order."""
    return [
        library.documents[document_id]
        for document_id in library.ids()
        if is_unlocked(state, library.documents[document_id], rng)
    ]
