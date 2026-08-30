"""Vendor filename to project filename mapping.

Third-party packs use whatever naming the artist preferred: ``smp2_ar_night1``,
``chinatsu_schsum_normalblush``, ``beach a s2 day.png``. The project uses one
scheme, documented in ``docs/production/ASSET_NAMING.md``::

    char_<character>_<outfit>_<expression>.webp
    bg_<place>_<variant>_<time>.webp
    prop_<name>.webp
    ui_<name>.png

Two rules make the renaming safe:

* **Traceability survives it.** Every rename is recorded in the import log, so a
  project-side name always resolves back to the file the artist shipped.
* **Names carry asset identity, not canon identity.** The file is
  ``char_chinatsu_...``, never ``char_iris_...``. Which sprite plays Iris is a
  casting decision recorded in ``data/characters/iris.json`` and can change
  without touching a single file. See ADR-0005 and the note in
  ``docs/canon/OPEN_QUESTIONS.md``.

Where a source token's meaning is not certain from the filename alone, it is
passed through unchanged rather than guessed at. A wrong expression name is
worse than an ugly one: it will be used by a writer who trusts it.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------

#: Source outfit token -> project outfit name.
OUTFITS: dict[str, str] = {
    "schsum": "school_summer",
    "schwin": "school_winter",
    "schwi": "school_winter",  # one character's files use the truncated form
    "schoolsummer": "school_summer",
    "schoolwinter": "school_winter",
    "school": "school",
    "schoolsweater": "school_sweater",
    "offtop": "casual_offshoulder",
    "shirttop": "casual_shirt",
    "whitetop": "casual_white",
    "casual": "casual",
    "outing": "outing",
    "outdoor": "outdoor",
    "dress": "dress",
    "butler": "butler",
    "sensei": "faculty",
    "sports": "sports",
    "outfit1": "outfit_a",
}

#: Source expression token -> the project's semantic vocabulary.
#:
#: Only confident mappings are listed. ``purp`` is deliberately absent: its
#: meaning cannot be determined from the filename, and inventing one would put a
#: wrong label in front of a writer. It passes through unchanged and is listed
#: as an open item in docs/production/ASSET_NAMING.md.
EXPRESSIONS: dict[str, str] = {
    "normal": "neutral",
    "normalblush": "neutral_blush",
    "talk": "talk",
    "happy": "happy",
    "blush": "blush",
    "pout": "pout",
    "poutangry": "pout_angry",
    "angry": "angry",
    "angrytalk": "angry_talk",
    "upset": "sad",
    "upsettalk": "sad_talk",
    "tears": "crying",
    "huh": "surprised",
    "frown": "concerned",
    "disgusted": "disgusted",
    "evilsmirk": "smirk",
}

#: The semantic expression set scenes may rely on. A character is not required
#: to have all of them; the Ren'Py side falls back to ``neutral`` and the dev
#: build reports the gap rather than crashing.
CANONICAL_EXPRESSIONS: tuple[str, ...] = (
    "neutral",
    "neutral_blush",
    "talk",
    "happy",
    "blush",
    "smirk",
    "surprised",
    "concerned",
    "sad",
    "sad_talk",
    "angry",
    "angry_talk",
    "pout",
    "pout_angry",
    "crying",
    "disgusted",
)

# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

#: Source pack prefix -> project place prefix and a per-pack place table.
BG_PLACES: dict[str, dict[str, str]] = {
    "smp": {
        "classroom1": "school_classroom_a",
        "classroom2": "school_classroom_b",
        "classroom3": "school_classroom_c",
        "classroom4": "school_classroom_entrance",
        "club1": "school_clubroom_a",
        "club2": "school_clubroom_b",
        "club3": "school_clubroom_c",
        "club4": "school_clubroom_d",
        "front": "school_entrance",
        "hallway": "school_hall",
        "noticeboard": "school_noticeboard",
        "roof": "school_rooftop",
        "stairs1": "school_stairs_a",
        "stairs2": "school_stairs_b",
    },
    "smp2": {
        "ar": "school_artroom",
        "mr": "school_musicroom",
        "sp1": "school_pool_a",
        "sp2": "school_pool_b",
        "sp3": "school_pool_c",
        "sp4": "school_pool_d",
    },
    "pra": {"a1": "room_a_view1", "a2": "room_a_view2", "a3": "room_a_view3"},
    "prb": {"a1": "room_b_view1", "a2": "room_b_view2"},
    "prc": {"a1": "room_c_view1"},
}

#: Time-of-day token -> project time name. ``lights`` variants are kept as a
#: separate suffix because they are a different lighting state, not a time.
BG_TIMES: dict[str, str] = {
    "day1": "day",
    "day2": "day_alt",
    "evening1": "evening",
    "evening2": "evening_alt",
    "night1": "night",
    "night2": "night_alt",
    "night3": "night_alt2",
    "day": "day",
    "evening": "evening",
    "night": "night",
    "nightlights": "night_lit",
}

_HALLWAY_RE = re.compile(r"^hallway(\d)(\d)$")


def character_name(stem: str) -> tuple[str, str, str] | None:
    """Split a character sprite stem into ``(character, outfit, expression)``.

    Returns ``None`` for a filename that does not follow the pack convention, so
    the caller can report it rather than silently importing something odd.
    """
    parts = stem.split("_")
    if len(parts) < 3:
        return None
    character, outfit_token = parts[0], parts[1]
    expression_token = "_".join(parts[2:])
    return (
        character,
        OUTFITS.get(outfit_token, outfit_token),
        EXPRESSIONS.get(expression_token, expression_token),
    )


def character_filename(stem: str, suffix: str) -> str | None:
    """Return the project filename for a character sprite."""
    parsed = character_name(stem)
    if parsed is None:
        return None
    character, outfit, expression = parsed
    return f"char_{character}_{outfit}_{expression}{suffix}"


def background_filename(stem: str, suffix: str) -> str | None:
    """Return the project filename for a background image.

    Handles both the ``smp_place_time`` convention of the newer packs and the
    space-separated ``beach a s2 day`` convention of the older starter pack.
    """
    if " " in stem:
        return _starter_pack_filename(stem, suffix)

    parts = stem.split("_")
    if len(parts) < 2:
        return None

    prefix, place_token = parts[0], parts[1]
    table = BG_PLACES.get(prefix)
    if table is None:
        return None

    extras = parts[2:]

    place: str
    if hallway := _HALLWAY_RE.match(place_token):
        place = f"school_hall_{hallway.group(1)}"
        extras = [f"door{hallway.group(2)}", *extras]
    else:
        known = table.get(place_token)
        if known is None:
            return None
        place = known

    time = "day"
    modifiers: list[str] = []
    for token in extras:
        if token in BG_TIMES:
            time = BG_TIMES[token]
        elif token == "lights":
            modifiers.append("lit")
        else:
            modifiers.append(token)

    tail = ("_" + "_".join(modifiers)) if modifiers else ""
    return f"bg_{place}_{time}{tail}{suffix}"


def _starter_pack_filename(stem: str, suffix: str) -> str:
    """Map the older starter pack's space-separated names."""
    tokens = stem.lower().split()
    time = "day"
    place_tokens: list[str] = []
    for token in tokens:
        if token in BG_TIMES:
            time = BG_TIMES[token]
        else:
            place_tokens.append(token)
    place = "_".join(place_tokens)
    return f"bg_{place}_{time}{suffix}"


def prop_filename(stem: str, suffix: str) -> str:
    """Return the project filename for a prop icon."""
    cleaned = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return f"prop_{cleaned}{suffix}"


def ui_filename(stem: str, suffix: str) -> str:
    """Return the project filename for a UI element."""
    cleaned = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return f"ui_{cleaned}{suffix}"


def audio_filename(stem: str, suffix: str) -> str:
    """Return the project filename for a music track."""
    cleaned = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return f"bgm_{cleaned}{suffix}"


def classify(path: Path, asset_id: str) -> str:
    """Return which naming rule applies to a vendor file."""
    if asset_id.startswith("pm_char"):
        return "character"
    # Checked before the "pm_bg" prefix, which it would otherwise match.
    if asset_id.startswith("pm_bgm"):
        return "audio"
    if asset_id.startswith("pm_bg"):
        return "background"
    if asset_id == "kenney_generic_items":
        return "prop"
    if asset_id == "kenney_ui_pack":
        return "ui"
    if asset_id.startswith("source_"):
        return "font"
    return "other"
