"""Container factories, so the engine's state can be made rollback-aware.

This is the seam that makes one codebase work in two hosts.

Ren'Py implements rollback by substituting its own ``RevertableDict`` and
``RevertableList`` for the builtins *inside Ren'Py's own Python blocks*. Code in
an ordinary imported package does not get that substitution: a ``{}`` written in
``state.py`` is a plain ``dict``. It saves and loads correctly, and it does not
roll back — the failure is invisible until a player scrolls up, at which point
the text rewinds and the world does not.

So the engine never writes a container literal into game state. It calls
:func:`new_dict` and :func:`new_list`, which default to the builtins for headless
tooling and tests, and which the Ren'Py bridge repoints at the revertable types
during init.

Anything reachable from ``GameState`` must be created this way. A single plain
``dict`` nested three levels down is enough to reintroduce the bug, which is why
``tests/test_containers.py`` walks the whole state tree and asserts that every
container came from these factories.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

#: Overridden by the Ren'Py bridge at init. Left as the builtins everywhere
#: else, so the headless simulator and pytest see ordinary dicts and lists.
_dict_factory: Callable[..., Any] = dict
_list_factory: Callable[..., Any] = list


def configure(dict_factory: Callable[..., Any], list_factory: Callable[..., Any]) -> None:
    """Point the factories at host-provided container types.

    Called once, from ``game/engine/00_s32_engine.rpy``, with Ren'Py's
    revertable types. Calling it again is legal but pointless: state already
    built with the previous factories keeps the types it was built with.
    """
    global _dict_factory, _list_factory  # noqa: PLW0603 - one process-wide seam, by design
    _dict_factory = dict_factory
    _list_factory = list_factory


def reset() -> None:
    """Restore the builtin factories. For tests that need a clean baseline."""
    configure(dict, list)


def new_dict(source: Mapping[str, Any] | None = None) -> Any:
    """Create a dict that the host can roll back."""
    return _dict_factory(source) if source is not None else _dict_factory()


def new_list(source: Iterable[Any] | None = None) -> Any:
    """Create a list that the host can roll back."""
    return _list_factory(source) if source is not None else _list_factory()


def adopt(value: Any) -> Any:
    """Recursively rebuild a structure using the configured factories.

    Used when state arrives from somewhere that did not use the factories: a
    save loaded from disk, or a fixture built in a test. Scalars pass through
    untouched; tuples become lists, because a tuple in game state is a trap
    (it cannot be mutated, so a scene that tries fails at the worst moment).
    """
    if isinstance(value, Mapping):
        return new_dict({key: adopt(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return new_list([adopt(item) for item in value])
    return value


def factories() -> tuple[Callable[..., Any], Callable[..., Any]]:
    """Return the current factories, for assertions and diagnostics."""
    return _dict_factory, _list_factory
