"""Exception types raised by the narrative engine."""


class S32Error(Exception):
    """Base class for every error raised by the engine."""


class ContentError(S32Error):
    """Static authored content is malformed or internally inconsistent.

    Raised at load time, never during play: by the time a save exists the
    content has already been validated.
    """


class ConditionError(ContentError):
    """A requirement or blocker expression could not be parsed or evaluated."""


class EffectError(ContentError):
    """An effect expression could not be parsed or applied."""


class StateError(S32Error):
    """The runtime game state is not in a shape the engine can work with."""
