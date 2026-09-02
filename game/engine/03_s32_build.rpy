# Build identity.
#
# A tester's bug report is worth very little if nobody can tell which build it
# came from, and "the one you sent me" is what testers reasonably say. So the
# build stamps itself: version, build id and commit hash, written by
# `s32 build` into game/build_stamp.json and read back here at init.
#
# The stamp is generated rather than committed. Committing a file that names
# the commit containing it is not a thing that can be true, and a stale hash
# is worse than an honest "development". A checkout that has never been built
# simply reports itself as development, which is exactly what it is.
#
# docs/production/PLAYTEST_BUILD.md.

init offset = -5

init python:

    import json as _s32_json

    def _s32_read_build_stamp():
        """Return the build stamp written by `s32 build`, or a development one.

        `renpy.loadable` is the right question rather than `os.path.exists`:
        in a distribution the file lives inside an archive, where the operating
        system cannot see it and Ren'Py can.
        """
        from s32_engine import playtest as _pt

        if renpy.loadable("build_stamp.json"):
            try:
                raw = _s32_json.loads(renpy.file("build_stamp.json").read().decode("utf-8"))
            except (ValueError, OSError):
                # A corrupted stamp must not stop the game starting. It is
                # metadata about the build, not part of it.
                raw = {}
            return _pt.new_build_stamp(
                build_id=raw.get("build_id", "unreadable"),
                commit=raw.get("commit", "unreadable"),
                version=raw.get("game_version", GAME_VERSION),
            )
        return _pt.new_build_stamp()

    # Not game state: it describes the build, not the run, and it is identical
    # for every player of a given build.
    S32Build = _s32_read_build_stamp()

    def s32_build_line():
        """Return the one-line build identity, for the menu and bug reports."""
        return "{} · build {} · {}".format(
            S32Build["game_version"], S32Build["build_id"], S32Build["commit"][:8]
        )
