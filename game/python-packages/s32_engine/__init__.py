"""September 32 narrative engine.

A pure-Python, dependency-free package shared by two very different hosts:

* **Ren'Py**, which imports it at runtime to drive the game, and
* **the headless dev tooling** (validators, simulator, coverage reports),
  which imports it to reason about the content without launching a game.

Two rules keep that dual life honest and are enforced by tests:

1. **No third-party imports.** Ren'Py ships its own interpreter and cannot
   install wheels, so the engine may only use the standard library.
2. **No engine-owned mutable game state.** Everything that must survive a save,
   a load, or a Ren'Py rollback lives in plain ``dict``/``list``/``set``
   structures owned by the Ren'Py store. The engine is a library of pure
   functions over those structures. See ``docs/decisions/ADR-0007``.
"""

from s32_engine.containers import configure as configure_containers
from s32_engine.version import ENGINE_VERSION, SAVE_SCHEMA_VERSION

__all__ = ["ENGINE_VERSION", "SAVE_SCHEMA_VERSION", "configure_containers"]
