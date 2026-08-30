"""Structural types for authored content and runtime state.

Authored content (the ``*Def`` dataclasses) is immutable and never saved: it is
rebuilt from ``data/`` every launch, so editing it does not break existing
saves.

Runtime state uses ``TypedDict`` over plain builtins rather than dataclasses,
because Ren'Py's rollback only tracks its own revertable containers. See
``docs/decisions/ADR-0007-save-and-persistent-state.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

# ---------------------------------------------------------------------------
# Enumerations, expressed as Literal aliases plus a parallel tuple. The tuples
# are the single source of truth the JSON Schemas are generated from, so an
# enum can never drift between the engine and the content validator.
# ---------------------------------------------------------------------------

TimeSlot = Literal[
    "early_morning", "morning", "midday", "afternoon", "evening", "night", "late_night"
]
TIME_SLOTS: tuple[TimeSlot, ...] = (
    "early_morning",
    "morning",
    "midday",
    "afternoon",
    "evening",
    "night",
    "late_night",
)

Weather = Literal["clear", "overcast", "rain", "storm", "fog", "wind", "heat", "cold"]
WEATHERS: tuple[Weather, ...] = (
    "clear",
    "overcast",
    "rain",
    "storm",
    "fog",
    "wind",
    "heat",
    "cold",
)

#: Escalation phase. September 32 is designed to earn its horror, so the pacing
#: budget is first-class state rather than an implicit chapter number.
#: See ``docs/narrative-design/PACING.md``.
Phase = Literal["normal", "odd", "unsettling", "impossible", "consequences"]
PHASES: tuple[Phase, ...] = ("normal", "odd", "unsettling", "impossible", "consequences")

RelationshipAxis = Literal[
    "trust",
    "attraction",
    "respect",
    "resentment",
    "fear",
    "dependency",
    "suspicion",
    "familiarity",
]
RELATIONSHIP_AXES: tuple[RelationshipAxis, ...] = (
    "trust",
    "attraction",
    "respect",
    "resentment",
    "fear",
    "dependency",
    "suspicion",
    "familiarity",
)

TraitAxis = Literal[
    "curious",
    "direct",
    "gentle",
    "sarcastic",
    "impulsive",
    "reserved",
    "skeptical",
    "empathetic",
]
TRAIT_AXES: tuple[TraitAxis, ...] = (
    "curious",
    "direct",
    "gentle",
    "sarcastic",
    "impulsive",
    "reserved",
    "skeptical",
    "empathetic",
)

KnowledgeStance = Literal["unknown", "suspected", "known", "false_belief", "disproven"]
KNOWLEDGE_STANCES: tuple[KnowledgeStance, ...] = (
    "unknown",
    "suspected",
    "known",
    "false_belief",
    "disproven",
)

CommitmentStatus = Literal["active", "fulfilled", "broken", "excused", "expired"]
COMMITMENT_STATUSES: tuple[CommitmentStatus, ...] = (
    "active",
    "fulfilled",
    "broken",
    "excused",
    "expired",
)

RepeatPolicy = Literal["once", "cooldown", "repeatable"]
REPEAT_POLICIES: tuple[RepeatPolicy, ...] = ("once", "cooldown", "repeatable")

StoryletCategory = Literal["anchor", "conversation", "investigation", "ambient", "interstitial"]
STORYLET_CATEGORIES: tuple[StoryletCategory, ...] = (
    "anchor",
    "conversation",
    "investigation",
    "ambient",
    "interstitial",
)

ContentTag = Literal[
    "slice_of_life",
    "romance",
    "friendship",
    "mystery",
    "investigation",
    "horror",
    "school",
    "archive",
    "character",
    "meta",
    "anchor",
]
CONTENT_TAGS: tuple[ContentTag, ...] = (
    "slice_of_life",
    "romance",
    "friendship",
    "mystery",
    "investigation",
    "horror",
    "school",
    "archive",
    "character",
    "meta",
    "anchor",
)

ContentStatus = Literal["prototype", "draft", "active", "retired"]
CONTENT_STATUSES: tuple[ContentStatus, ...] = ("prototype", "draft", "active", "retired")

#: Bounds shared by every relationship axis and every player trait axis.
AXIS_MIN = 0
AXIS_MAX = 100
TRAIT_MIN = 0
TRAIT_MAX = 100

PRIORITY_MIN = 0
PRIORITY_MAX = 100

#: Reserved agent id for the player character in belief and relationship maps.
PLAYER = "player"


# ---------------------------------------------------------------------------
# Authored content definitions (immutable, rebuilt from data/ each launch)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CharacterDef:
    """A character as the story knows them, independent of any art asset.

    ``asset_id`` is deliberately separate from ``id``: the narrative identity
    must never be held hostage by whichever placeholder sprite happens to be
    installed. See ``docs/decisions/ADR-0005-character-art-consistency.md``.
    """

    id: str
    display_name: str
    role: str
    asset_id: str | None = None
    romanceable: bool = False
    tags: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True, slots=True)
class LocationDef:
    """A place a scene can be set in."""

    id: str
    display_name: str
    area: str
    indoor: bool = True
    background: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class KnowledgeDef:
    """A discrete fact that agents may hold differing beliefs about.

    ``contradicts`` links facts that cannot both be true. It is what lets the
    archive present mutually exclusive evidence while the engine still knows
    which contradiction the player has actually noticed.
    """

    id: str
    summary: str
    category: str
    contradicts: tuple[str, ...] = ()
    reveals_phase: Phase | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ItemDef:
    """A physical object or archive document the player can hold or catalogue."""

    id: str
    display_name: str
    kind: str
    description: str = ""
    grants: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class StoryletDef:
    """One pre-written narrative unit and the conditions under which it fits.

    A storylet holds no prose. It points at a Ren'Py ``label`` that does. That
    split is what makes the content simultaneously writer-friendly (the ``.rpy``
    file) and machine-checkable (this metadata). See ADR-0006.
    """

    id: str
    label: str
    title: str
    category: StoryletCategory
    status: ContentStatus = "prototype"
    characters: tuple[str, ...] = ()
    location: str | None = None
    time_slots: tuple[TimeSlot, ...] = ()
    phases: tuple[Phase, ...] = ()
    tags: tuple[ContentTag, ...] = ()
    priority: int = 50
    weight: float = 1.0
    requirements: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    #: Alternative effect sets the scene's own choices can produce, one tuple
    #: per choice. The prose stays in the ``.rpy``; the state consequences are
    #: declared here because a change the tools cannot see is a change that
    #: makes later content look unreachable. Kept in the same order as the
    #: choices appear, so a writer can check them side by side.
    outcomes: tuple[tuple[str, ...], ...] = ()
    grants: tuple[str, ...] = ()
    cooldown: int = 0
    repeat_policy: RepeatPolicy = "once"
    anchor: str | None = None
    summary: str = ""
    source_path: str = ""


@dataclass(frozen=True, slots=True)
class AnchorDef:
    """A dramatic beat that must happen, gating the storylets around it.

    Anchors stop a quality-based narrative from turning into structureless
    drift: storylets fill the space *between* anchors, anchors carry the shape.
    """

    id: str
    label: str
    title: str
    order: int
    phase: Phase
    requirements: tuple[str, ...] = ()
    effects: tuple[str, ...] = ()
    #: Per-choice effect sets, as on :class:`StoryletDef`. Anchors carry most of
    #: the early relationship movement, so leaving theirs undeclared would make
    #: every later threshold look unreachable.
    outcomes: tuple[tuple[str, ...], ...] = ()
    grants: tuple[str, ...] = ()
    summary: str = ""
    source_path: str = ""


#: Anything that can gate, grant and play. Storylets and anchors share enough
#: shape that most tooling treats them alike; naming the union keeps that
#: honest instead of widening to ``object`` at every call site.
ContentSource = StoryletDef | AnchorDef


@dataclass(frozen=True, slots=True)
class ContentLibrary:
    """Everything authored, loaded once and then treated as read-only."""

    characters: dict[str, CharacterDef] = field(default_factory=dict)
    locations: dict[str, LocationDef] = field(default_factory=dict)
    knowledge: dict[str, KnowledgeDef] = field(default_factory=dict)
    items: dict[str, ItemDef] = field(default_factory=dict)
    storylets: dict[str, StoryletDef] = field(default_factory=dict)
    anchors: dict[str, AnchorDef] = field(default_factory=dict)

    def storylet_ids(self) -> list[str]:
        """Return storylet ids in a stable, deterministic order."""
        return sorted(self.storylets)


# ---------------------------------------------------------------------------
# Runtime state (plain builtins, rollback-safe)
# ---------------------------------------------------------------------------


class BeliefState(TypedDict):
    """What one agent believes about one fact."""

    stance: KnowledgeStance
    confidence: float
    source: str
    learned_day: int


class CharacterState(TypedDict):
    """Per-character mutable state for the current run."""

    present: bool
    availability: int
    mood: str
    location: str
    goal: str
    flags: dict[str, bool]


class CommitmentState(TypedDict):
    """A promise the player made, and what became of it."""

    id: str
    kind: str
    participants: list[str]
    made_day: int
    due_day: int
    due_time: str
    importance: int
    status: CommitmentStatus
    resolved_day: int


class WorldState(TypedDict):
    """Where and when we are, plus loose world-level counters."""

    day: int
    calendar_day: int
    month: str
    time_slot: TimeSlot
    weather: Weather
    phase: Phase
    location: str
    flags: dict[str, int]
    recent_events: list[str]


class StoryletRecord(TypedDict):
    """One entry in the play history."""

    id: str
    day: int
    time_slot: str


class GameState(TypedDict):
    """The complete per-run state.

    Every value below is a plain builtin so Ren'Py's rollback, save and load
    machinery can handle it without help.
    """

    save_schema_version: int
    game_version: str
    seed: int
    rng_counter: int
    world: WorldState
    characters: dict[str, CharacterState]
    relationships: dict[str, dict[str, int]]
    beliefs: dict[str, dict[str, BeliefState]]
    traits: dict[str, int]
    commitments: list[CommitmentState]
    inventory: list[str]
    history: list[StoryletRecord]
    seen_counts: dict[str, int]
    last_seen_day: dict[str, int]
    anchors_done: list[str]
    #: Archive documents the player has read, in order. Separate from
    #: ``seen_counts`` on purpose: a document is not a scene, and mixing them
    #: would pollute the storylet history and the coverage reports.
    documents_read: list[str]
