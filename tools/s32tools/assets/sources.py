"""The asset acquisition plan: what to fetch, from where, and under what terms.

This module is the *code* half of the asset system; ``assets/catalog/assets.toml``
is the *record* half. Keeping them separate means the manifest stays a
human-readable legal document that survives even if this tooling is rewritten.

Download hygiene, enforced here rather than left to discipline:

* Official sources only -- the creator's own page or the project's own release.
  No mirrors, no aggregators, no reuploads.
* Smallest adequate variant. The project targets 1080p, so 1080p WebP is fetched
  in preference to 4K PNG. That is not only about disk: 4K assets get scaled
  down at runtime for no visible gain.
* Every download is hashed after the fact and the hash is written to the
  manifest, so a later re-fetch that returns different bytes is detectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Method = Literal["itch_free", "direct", "manual"]


@dataclass(frozen=True, slots=True)
class Source:
    """How to obtain one third-party pack."""

    id: str
    method: Method
    page: str
    #: For ``itch_free``: the exact file name shown on the download page.
    #: For ``direct``: the full URL.
    target: str
    #: Rough download size, for the progress line and for judging whether to
    #: fetch at all.
    approx_mb: float = 0.0
    #: Why this particular variant was chosen over the others on the page.
    variant_rationale: str = ""
    #: Instructions to show when automated fetching is not possible.
    manual_steps: list[str] = field(default_factory=list)


#: The character core. One artist, one anatomy, one line weight, one expression
#: vocabulary -- see ADR-0005 for why this is treated as a hard rule rather than
#: a preference.
CHARACTER_SOURCES: tuple[Source, ...] = (
    Source(
        id="pm_char_a01",
        method="itch_free",
        page="https://potat0master.itch.io/free-characters-for-visual-novels-set-a01",
        target="BasicCharacterSetA01_1080p_WEBP_Free.zip",
        approx_mb=7.9,
        variant_rationale=(
            "1080p WebP: the project renders at 1920x1080, so the 2160p variants "
            "would only be downscaled. WebP is 6x smaller than the PNG variant "
            "with no visible difference at target resolution, and Ren'Py 8 "
            "decodes WebP natively."
        ),
    ),
    Source(
        id="pm_char_a02",
        method="itch_free",
        page="https://potat0master.itch.io/characters-set-a02",
        target="BasicCharacterSetA02_1080p_WEBP_Free.zip",
        approx_mb=10.0,
        variant_rationale=(
            "Same characters as A01 with three additional outfits. Identical "
            "anatomy and expression set, which is exactly what a single "
            "character system needs."
        ),
    ),
)

#: Backgrounds, from the same artist, for the same reason.
BACKGROUND_SOURCES: tuple[Source, ...] = (
    Source(
        id="pm_bg_school_1",
        method="itch_free",
        page="https://potat0master.itch.io/free-visual-novel-backgrounds-school-mini-pack-1",
        target="SchoolMiniPack_1080p_WEBP.zip",
        approx_mb=7.3,
        variant_rationale=(
            "1080p WebP is 7 MB against 227 MB for 1080p PNG and over 1 GB for "
            "the 4K PNG parts. Covers classroom, hallway, club room, entrance, "
            "roof and stairs with day/night variants."
        ),
    ),
    Source(
        id="pm_bg_school_2",
        method="itch_free",
        page="https://potat0master.itch.io/free-visual-novel-backgrounds-school-mini-pack-2",
        target="SchoolMiniPack2_1080p_WEBP.zip",
        approx_mb=15.0,
        variant_rationale="Art room, music room and pool. Same rationale as pack 1.",
    ),
    Source(
        id="pm_bg_starter_1",
        method="itch_free",
        page="https://potat0master.itch.io/free-visual-novel-backgrounds-starter-pack",
        target="Visual Novel Backgrounds (Starter Pack).zip",
        approx_mb=40.0,
        variant_rationale=(
            "This older pack offers only one resolution. The page also lists a "
            "Clouds and a Tutorial archive, which are not backgrounds and are "
            "not fetched."
        ),
    ),
    Source(
        id="pm_bg_personal_rooms_1",
        method="itch_free",
        page="https://potat0master.itch.io/free-visual-novel-backgrounds-personal-rooms-pack-1",
        target="PersonalRooms1_1080p_WEBP.zip",
        approx_mb=2.0,
        variant_rationale="Dorm and bedroom interiors, 1080p WebP per the variant policy above.",
    ),
)

#: Props and UI scaffolding. CC0, so the licensing question is genuinely simple
#: here -- which is precisely why they are used for utility art and not for the
#: cast (ADR-0005).
CC0_SOURCES: tuple[Source, ...] = (
    Source(
        id="kenney_generic_items",
        method="direct",
        page="https://kenney.nl/assets/generic-items",
        target="https://kenney.nl/media/pages/assets/generic-items/96b9087204-1677667000/kenney_generic-items.zip",
        approx_mb=2.0,
        variant_rationale=(
            "CC0, 160 items. Used only for inventory icons, clue-journal "
            "placeholders and UI affordances -- never as scene art. Everything "
            "kept gets the same deterministic archival treatment so the set "
            "reads as one visual language rather than as a borrowed pack."
        ),
    ),
    Source(
        id="kenney_ui_pack",
        method="direct",
        page="https://kenney.nl/assets/ui-pack",
        target="https://kenney.nl/media/pages/assets/ui-pack/f651646eab-1718203990/kenney_ui-pack.zip",
        approx_mb=6.0,
        variant_rationale=(
            "CC0 UI scaffolding. Explicitly a bootstrap: the shipped interface "
            "must not read as 'Kenney UI'. See docs/style/VISUAL_DESIGN_SYSTEM.md."
        ),
    ),
)

#: Music. A small, coherent set rather than a library.
AUDIO_SOURCES: tuple[Source, ...] = (
    Source(
        id="pm_bgm_1",
        method="itch_free",
        page="https://potat0master.itch.io/free-background-music-for-visual-novels-bgm-pack-1",
        target="BGM Pack 1 OGG.zip",
        approx_mb=19.0,
        variant_rationale=(
            "OGG Vorbis is Ren'Py's native streaming format and loops without "
            "the leading silence MP3 encoders insert. Taking OGG from the "
            "creator avoids a transcode generation entirely."
        ),
    ),
)

#: Fonts, from the upstream projects rather than a font CDN, so that the exact
#: version and its OFL text are both pinned.
FONT_SOURCES: tuple[Source, ...] = (
    Source(
        id="source_sans_3",
        method="direct",
        page="https://github.com/adobe-fonts/source-sans",
        target="https://github.com/adobe-fonts/source-sans/releases/download/3.052R/TTF-source-sans-3.052R.zip",
        approx_mb=2.4,
        variant_rationale=(
            "SIL Open Font License 1.1, complete Latin coverage including the "
            "diacritics pt-BR needs, and a large x-height that stays legible in "
            "a dialogue box at 1080p. TTF over OTF for the widest engine support."
        ),
    ),
    Source(
        id="source_serif_4",
        method="direct",
        page="https://github.com/adobe-fonts/source-serif",
        target="https://github.com/adobe-fonts/source-serif/releases/download/4.005R/source-serif-4.005_Desktop.zip",
        approx_mb=17.6,
        variant_rationale=(
            "Same family designer and metrics philosophy as Source Sans, so the "
            "two sit together. Used for archive documents and titles, where the "
            "serif reads as institutional paper rather than as decoration."
        ),
    ),
)

#: Packs deliberately NOT fetched, with the reason. Recorded in code so that a
#: future contributor who wonders 'why not this one?' finds the answer before
#: re-adding it.
EXCLUDED: dict[str, str] = {
    "noranekogames_*": (
        "Terms carry a broad restriction against use 'with AI in any way', "
        "including language resembling 'paired with'. This project uses AI "
        "heavily during development, so the ambiguity is not worth entering. "
        "See docs/legal/AI_AND_ASSETS_POLICY.md."
    ),
    "any_ai_generated_pack": (
        "Packs described as Stable Diffusion / Midjourney / AI-generated / "
        "AI-assisted are excluded for the cast and for scene art. Provenance "
        "of the visual corpus is a production requirement."
    ),
    "potat0master_paid_tiers": (
        "The $1-$5 tiers of the packs above are not fetched: payment is a manual "
        "step, and the free tiers cover the prototype. If bought later, add them "
        "as `manual` sources with their own evidence."
    ),
}

#: Secondary character packs, evaluated only after a visual consistency audit.
#: They are listed but not fetched by default -- see
#: docs/production/CHARACTER_ASSET_AUDIT.md.
SECONDARY_CHARACTER_CANDIDATES: dict[str, str] = {
    "pm_char_kioshi_haruo": "https://potat0master.itch.io/free-character-sprite-for-visual-novels-kioshi-haruo",
    "pm_char_sensei": "https://potat0master.itch.io/free-character-sprites-for-visual-novels-sensei-pack",
    "pm_char_hiyori": "https://potat0master.itch.io/free-character-sprite-for-visual-novels-hiyori",
    "pm_char_taishiro": "https://potat0master.itch.io/free-character-sprite-for-visual-novels-taishiro",
    "pm_char_nozomi": "https://potat0master.itch.io/free-character-sprite-for-visua-novel-nozomi",
    "pm_char_ryoko_madoka": "https://potat0master.itch.io/free-character-sprite-for-visual-novels-ryoko-madoka",
    "pm_char_keiko": "https://potat0master.itch.io/free-character-sprite-for-visual-novels",
}

ALL_SOURCES: tuple[Source, ...] = (
    *CHARACTER_SOURCES,
    *BACKGROUND_SOURCES,
    *CC0_SOURCES,
    *AUDIO_SOURCES,
    *FONT_SOURCES,
)

#: Named groups for ``s32 assets fetch --group``.
GROUPS: dict[str, tuple[Source, ...]] = {
    "characters": CHARACTER_SOURCES,
    "backgrounds": BACKGROUND_SOURCES,
    "cc0": CC0_SOURCES,
    "audio": AUDIO_SOURCES,
    "fonts": FONT_SOURCES,
    "all": ALL_SOURCES,
}


def get(source_id: str) -> Source:
    """Return one source by id."""
    for source in ALL_SOURCES:
        if source.id == source_id:
            return source
    raise KeyError(f"unknown asset source {source_id!r}")
