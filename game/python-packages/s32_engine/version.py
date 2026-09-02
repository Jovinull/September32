"""Version constants for the engine and for saved-game compatibility."""

from typing import Final

#: Version of the narrative engine code itself. Informational.
ENGINE_VERSION: Final = "0.1.0"

#: Structure version of the in-run game state (``GameState``). Bump this
#: whenever the shape of the state dict changes in a way old saves cannot be
#: read as-is; add a migration step in ``s32_engine.state.migrate_state``.
#:
#: v2 added ``documents_read``, for the archive viewer's once-only effects.
#: v3 flipped relationship edges the broken ``source="player"`` default had
#: filed backwards.
SAVE_SCHEMA_VERSION: Final = 3

#: Structure version of the cross-run ``persistent`` meta state. Bump and add
#: a migration in ``s32_engine.meta.migrate_meta`` when it changes.
META_SCHEMA_VERSION: Final = 1

#: Structure version of the playtest report written by ``s32_engine.playtest``.
#: Bump when the report's shape changes; ``s32 playtest summarize`` refuses a
#: file it does not recognise rather than half-reading it.
PLAYTEST_REPORT_SCHEMA_VERSION: Final = 1

#: Human-facing build version of the game, surfaced in saves and bug reports.
#:
#: 0.2.0-playtest.1 is the first build meant for somebody outside the project.
#: The suggested 0.0.5-playtest.1 was not used because it sorts *before* the
#: 0.1.0-prototype it succeeds, and a version that goes backwards is a version
#: nobody can reason about. See docs/production/PLAYTEST_BUILD.md.
GAME_VERSION: Final = "0.2.0-playtest.1"
