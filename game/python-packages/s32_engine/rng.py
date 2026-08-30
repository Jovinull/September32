"""Deterministic, rollback-safe randomness.

Python's :mod:`random` is the wrong tool inside a visual novel. Its generator
state lives outside the save, so rolling back past a random draw and replaying
it produces a *different* result -- the player scrolls up, scrolls down, and the
world has changed underneath them.

Ren'Py solves this with ``renpy.random``, whose state participates in rollback.
The engine cannot import Ren'Py (it must also run headless), so it takes the
opposite approach: **no generator state at all**. Every draw is a pure hash of
``(seed, counter)``, and the counter lives in the ordinary game state, which
Ren'Py already rolls back, saves and loads for free.

The consequence is worth stating plainly: the same counter always yields the
same number. Rolling back rewinds the counter, so replaying the same beat gives
the same outcome. That is exactly the behaviour a rollback-enabled VN needs, and
it is also what makes ``--seed`` reproducible in the simulator.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import TypeVar

from s32_engine.types import GameState

T = TypeVar("T")

_MODULUS = 2**53


class Rng:
    """A counter-based pseudo-random source bound to a :class:`GameState`.

    The instance holds no randomness of its own; it is a thin view over
    ``state["seed"]`` and ``state["rng_counter"]``. Creating and discarding
    instances freely is fine and cheap.
    """

    __slots__ = ("_state",)

    def __init__(self, state: GameState) -> None:
        self._state = state

    def _next(self) -> int:
        """Advance the counter and return the raw draw as an integer."""
        counter = self._state["rng_counter"]
        self._state["rng_counter"] = counter + 1
        payload = f"{self._state['seed']}:{counter}".encode()
        digest = hashlib.blake2b(payload, digest_size=8).digest()
        return int.from_bytes(digest, "big") % _MODULUS

    def random(self) -> float:
        """Return a float in ``[0.0, 1.0)``."""
        return self._next() / _MODULUS

    def randint(self, low: int, high: int) -> int:
        """Return an integer in ``[low, high]`` inclusive."""
        if high < low:
            raise ValueError(f"empty range: [{low}, {high}]")
        return low + self._next() % (high - low + 1)

    def choice(self, items: Sequence[T]) -> T:
        """Return one element chosen uniformly."""
        if not items:
            raise ValueError("cannot choose from an empty sequence")
        return items[self._next() % len(items)]

    def weighted_choice(self, items: Sequence[T], weights: Sequence[float]) -> T:
        """Return one element chosen in proportion to ``weights``.

        Non-positive weights are treated as zero. If every weight is zero the
        choice degrades to uniform rather than raising, because a content bug
        should not crash a player's session mid-scene.
        """
        if len(items) != len(weights):
            raise ValueError("items and weights must be the same length")
        if not items:
            raise ValueError("cannot choose from an empty sequence")

        positive = [max(0.0, w) for w in weights]
        total = sum(positive)
        if total <= 0.0:
            return self.choice(items)

        target = self.random() * total
        cumulative = 0.0
        for item, weight in zip(items, positive, strict=True):
            cumulative += weight
            if target < cumulative:
                return item
        return items[-1]

    def shuffled(self, items: Sequence[T]) -> list[T]:
        """Return a shuffled copy, using a Fisher-Yates pass over draws."""
        result = list(items)
        for i in range(len(result) - 1, 0, -1):
            j = self._next() % (i + 1)
            result[i], result[j] = result[j], result[i]
        return result
