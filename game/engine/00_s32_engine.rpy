# September 32 — the bridge between Ren'Py and the narrative engine.
#
# `init offset = -5` puts this before everything except gui.rpy, because every
# other file in the project assumes `s32` and `S32State` already exist.
#
# The division of labour, which the rest of the project depends on:
#
#   s32_engine (pure Python, game/python-packages/)
#       Content loading, eligibility, effects, selection. Knows nothing about
#       Ren'Py. Testable headless. Holds NO mutable state.
#
#   this file
#       Owns the state, as plain dicts in the Ren'Py store so that rollback,
#       save and load work without help. Exposes a small verb vocabulary that
#       reads well inside a scene.
#
# Why the state is dicts and not objects: Ren'Py's rollback only reverts changes
# to containers it controls. A class instance defined in a pure-Python package
# would save and load correctly and then silently fail to roll back — the worst
# possible bug in a visual novel, because it only appears when the player
# scrolls up. See docs/decisions/ADR-0007-save-and-persistent-state.md.

init offset = -5

init python:

    import s32_engine as s32
    from s32_engine import (
        calendar as s32_calendar_module,
        commitments as s32_commitments,
        conditions as s32_conditions,
        definitions as s32_definitions,
        devlog as s32_devlog,
        effects as s32_effects,
        knowledge as s32_knowledge,
        meta as s32_meta,
        relationships as s32_relationships,
        documents as s32_documents,
        state as s32_state,
        traits as s32_traits,
        world as s32_world,
    )
    from s32_engine.director import NarrativeDirector
    from s32_engine.rng import Rng
    from s32_engine.version import GAME_VERSION, META_SCHEMA_VERSION, SAVE_SCHEMA_VERSION

    s32_devlog.configure(active=config.developer)

    # Point the engine's container factories at Ren'Py's revertable types.
    #
    # This is the single most important line in the bridge. Without it the run
    # state is built from ordinary dicts and lists, which Ren'Py will happily
    # save and load and will NOT roll back — the text rewinds, the world does
    # not, and nothing reports an error. The smoke test `smoke_rollback` exists
    # to catch a regression here.
    from renpy.revertable import RevertableDict, RevertableList

    s32.configure_containers(RevertableDict, RevertableList)


# `init 1` (i.e. -4 after the file offset) so this runs AFTER the imports above.
# A negative literal here would run *earlier* than the unadorned block, which is
# the kind of ordering bug that only shows up as a NameError at launch.
init 1 python:

    def _s32_data_dir():
        """Return the directory holding authored content JSON, or None.

        In development the repository's `data/` sits beside `game/` and the
        engine can read it straight off the disk.
        """
        candidates = [
            os.path.join(config.gamedir, "data"),
            os.path.join(config.basedir, "data"),
        ]
        for path in candidates:
            if os.path.isdir(path):
                return path
        return None

    def _s32_content_files():
        """Return every content file as text, read through Ren'Py.

        A built game keeps `data/` inside `archive.rpa`, where the operating
        system cannot see it: `os.path.isdir` is False and the loader raises.
        That is how the first playtest build reached a fresh install and failed
        on its own content, with a stack trace, before the main menu.

        Ren'Py can read those files perfectly well -- it simply cannot hand
        over a directory -- so the content is read here and passed to the
        engine as text. The engine stays dependency-free, which is the property
        that lets the same loader run in the headless simulator.
        """
        files = {}
        for name in renpy.list_files():
            parts = name.split("/")
            if len(parts) == 3 and parts[0] == "data" and name.endswith(".json"):
                with renpy.file(name) as handle:
                    files["{}/{}".format(parts[1], parts[2])] = handle.read().decode("utf-8")
        return files

    # The content library is static for the life of the process and is NOT part
    # of the save. Rebuilding it every launch is what lets content be edited
    # without invalidating existing saves.
    #
    # Documents load alongside the storylets and are static in the same way.
    # What the player has READ is run state; what exists is not.
    _s32_data = _s32_data_dir()
    if _s32_data is not None:
        s32_library = s32_definitions.load_library(_s32_data)
        s32_library_documents = s32_documents.load_documents(_s32_data)
    else:
        _s32_files = _s32_content_files()
        s32_library = s32_definitions.load_library_from(_s32_files)
        s32_library_documents = s32_documents.load_documents_from(_s32_files)

    # A library with nothing in it is the silent failure this whole path exists
    # to prevent: the director selects nothing, the week is empty, no exception
    # is raised anywhere, and the first person to notice is a tester. Loud is
    # the only acceptable behaviour.
    if not s32_library.storylets:
        raise Exception(
            "no content was loaded. In development, data/ should sit beside "
            "game/. In a built game it is mirrored into game/data/ by "
            "`s32 build` -- see docs/production/PLAYTEST_BUILD.md."
        )

    s32_director = NarrativeDirector(s32_library)

    s32_devlog.log(
        "content",
        "loaded {} storylets, {} anchors, {} characters, {} facts".format(
            len(s32_library.storylets),
            len(s32_library.anchors),
            len(s32_library.characters),
            len(s32_library.knowledge),
        ),
    )
    s32_devlog.log("content", "loaded {} archive documents".format(len(s32_library_documents.documents)))


# ---------------------------------------------------------------------------
# Run state
# ---------------------------------------------------------------------------

# `default` rather than `define`: this is per-run state, it belongs in the save,
# and it must be re-created for a new game.
default S32State = {}

# The last director decision, kept for the debug inspector. Not gameplay state,
# but it lives in the store anyway so rollback shows the trace that matched the
# scene the player is looking at.
default S32LastSelection = None


init python:

    def s32_new_run(seed=None):
        """Start a fresh run.

        Args:
            seed: Deterministic seed. Defaults to one derived from the number of
                runs played, so successive playthroughs differ but any single
                one is reproducible from its save.
        """
        global S32State

        if seed is None:
            # S32_SEED pins the run for automated tests and for reproducing a
            # reported bug: the whole engine is deterministic given a seed, so
            # "it happened on seed 4211" is a complete repro.
            override = os.environ.get("S32_SEED")
            if override:
                seed = int(override)
            else:
                seed = (persistent.s32_meta or {}).get("runs_started", 0) * 7919 + 17

        S32State = s32_state.new_state(s32_library, seed=seed)

        # Everyone starts present. Storylets gate on *location* and time, which
        # is what actually decides who the player runs into; `present` is
        # reserved for a character being genuinely away — ill, suspended, gone.
        # A per-character timetable would be a simulation of a system this game
        # does not have, and the headless simulator makes the same assumption so
        # that its reachability numbers mean something.
        for _char in S32State["characters"].values():
            _char["present"] = True

        meta = s32_get_meta()
        s32_meta.start_run(meta)
        s32_set_meta(meta)

        s32_pt_start_run(seed)

        s32_devlog.log("run", "new run, seed={}".format(seed))
        return S32State

    def s32_after_load():
        """Bring a loaded save up to the current build.

        Called from the `after_load` label. Two jobs, in order: migrate the
        state's shape, then reconcile it with content authored since the save
        was written. Neither is allowed to throw for anything short of a save
        from a *newer* build, which genuinely cannot be read.
        """
        global S32State

        s32_pt_load()

        S32State = s32_state.migrate_state(S32State)
        added = s32_state.sync_with_library(S32State, s32_library)
        if added:
            s32_devlog.log("save", "added state for new characters: {}".format(", ".join(added)))

    def s32_rng():
        """Return a rollback-safe RNG bound to the current state.

        Cheap to construct and holds nothing, so callers make one per use rather
        than caching a reference across an interaction.
        """
        return Rng(S32State)


# ---------------------------------------------------------------------------
# Cross-run meta state
# ---------------------------------------------------------------------------

default persistent.s32_meta = None
default persistent.s32_meta_schema_version = META_SCHEMA_VERSION


init python:

    def s32_get_meta():
        """Return the persistent meta-state, migrated to the current schema."""
        return s32_meta.migrate_meta(persistent.s32_meta)

    def s32_set_meta(meta):
        """Store the meta-state back into `persistent`."""
        persistent.s32_meta = meta
        persistent.s32_meta_schema_version = meta["schema_version"]

    def s32_remember(clue_id):
        """Return whether the PLAYER has earned a cross-run clue.

        Deliberately not "does the protagonist remember". They do not. See
        docs/narrative-design/META.md — this gates the rare `[You remember.]`
        option and nothing else.
        """
        return s32_meta.remembers(s32_get_meta(), clue_id)

    def s32_unlock_meta(clue_id):
        """Record that the player has earned a cross-run clue."""
        meta = s32_get_meta()
        changed = s32_meta.unlock_meta_clue(meta, clue_id)
        s32_set_meta(meta)
        return changed

    def s32_record_discovery(discovery_id):
        """Record something seen at least once, across all runs."""
        meta = s32_get_meta()
        novel = s32_meta.record_discovery(meta, discovery_id)
        s32_set_meta(meta)
        return novel


# ---------------------------------------------------------------------------
# The verb vocabulary used inside scenes
#
# These exist so a scene reads as prose with a few annotations, rather than as
# state manipulation with prose in between. Each one is a thin wrapper; the
# logic lives in the engine where it is tested.
# ---------------------------------------------------------------------------

init python:

    def rel(pair, axis, delta):
        """Adjust one relationship axis. ``pair`` is written ``source->target``.

        The direction is not optional and there is no default, because there
        used to be one and it was wrong in every scene that used it: `rel("iris",
        "trust", 3)` stored the *player's* trust toward Iris, while every scene
        that wrote it meant Iris trusting the player.

            $ rel("iris->player", "trust", 3)     # Iris warms to you
            $ rel("player->iris", "suspicion", 2) # you start doubting her
            $ rel("mara->june", "resentment", 2)  # nothing to do with you

        See docs/narrative-design/RELATIONSHIP_DIRECTION.md.
        """
        source, target = s32_relationships.parse_pair(pair)
        return s32_relationships.change(S32State, source, target, axis, delta)

    def rel_get(pair, axis):
        """Read one relationship axis. ``pair`` is written ``source->target``."""
        source, target = s32_relationships.parse_pair(pair)
        return s32_relationships.get(S32State, source, target, axis)

    def stance(who):
        """Return how ``who`` currently reads the player, as a word.

        Scenes need to ask a human question -- "is she comfortable with me?" --
        and until Milestone 4 no scene asked one at all. Fifty-one storylets
        wrote to eight axes and nothing ever read them back, which is the
        difference between building a relationship and accumulating a variable.

        Deliberately coarse. A scene that needs the exact number can call
        `rel_get`; what most scenes need is which of a few versions of
        themselves to be, and three or four versions is as many as anyone can
        write well.

            distant       barely know you, or actively cooled
            wary          they know you and are holding something back
            comfortable   the ordinary good case
            close         trusted, and it took the whole week

        `wary` is not a milder `distant`. It is the interesting one: somebody
        who knows you well and does not trust you reads completely differently
        from somebody who has not decided yet, and it is the state the eight
        axes exist to make possible.

        See docs/narrative-design/RELATIONSHIP_SEMANTICS.md.
        """
        pair = "{}->player".format(who)
        trust = rel_get(pair, "trust")
        familiarity = rel_get(pair, "familiarity")
        against = max(rel_get(pair, "suspicion"), rel_get(pair, "resentment"))

        if against >= 4 and against * 2 >= trust:
            return "wary"
        if trust >= 18 and familiarity >= 12:
            return "close"
        if familiarity >= 8 or trust >= 8:
            return "comfortable"
        return "distant"

    def regards(who, axis, at_least):
        """Return whether ``who`` holds an axis toward the player at a level.

        The explicit form, for the scenes that want one axis rather than a
        summary: `regards("theo", "respect", 10)`.
        """
        return rel_get("{}->player".format(who), axis) >= at_least

    def player_regards(who, axis, at_least):
        """The other direction, for the rarer case where the player's own view
        of somebody is what a scene turns on."""
        return rel_get("player->{}".format(who), axis) >= at_least

    def learn(fact_id, source=""):
        """The player now knows something.

        Example:
            $ learn("photo_dated_sept_32", source="back_of_the_photo")
        """
        return s32_knowledge.grant(S32State, fact_id, source=source)

    def suspect(fact_id, source=""):
        """The player suspects something without being sure of it."""
        return s32_knowledge.suspect(S32State, fact_id, source=source)

    def knows(fact_id, who="player"):
        """Return whether an agent holds a fact as known."""
        return s32_knowledge.knows(S32State, fact_id, who)

    def npc_learns(who, fact_id, stance="known"):
        """Change what a character believes.

        Characters hold their own stances, and they can be wrong. That is the
        point: an archive that everyone agrees about has no story in it.
        """
        return s32_knowledge.set_stance(S32State, fact_id, stance, agent=who)

    def trait(axis, delta=1):
        """Nudge a player tendency.

        Traits are accumulated by behaving a certain way, never chosen. See
        s32_engine.traits.
        """
        return s32_traits.change(S32State, axis, delta)

    def has_trait(axis, threshold=None):
        """Return whether a tendency is established enough to be noticed."""
        if threshold is None:
            return s32_traits.has(S32State, axis)
        return s32_traits.has(S32State, axis, threshold)

    def trait_label(axis):
        """Return the bracketed label for a trait-gated choice."""
        return s32_traits.label(axis)

    def times_seen(storylet_id):
        """Return how many times a storylet has already played this run.

        Exposed for repeatable scenes whose variants are a progression rather
        than a shuffle: a room stops being unfamiliar in a fixed order, and
        picking that at random is the bug this exists to prevent. See
        docs/narrative-design/CONTINUITY_REVIEW.md.
        """
        return s32_state.times_seen(S32State, storylet_id)

    def promise(commitment_id, who, in_days=1, importance=50, kind="meeting"):
        """Record a promise the player just made."""
        return s32_commitments.make(
            S32State,
            commitment_id,
            kind=kind,
            participants=[who],
            due_day=S32State["world"]["day"] + in_days,
            importance=importance,
        )

    def kept(commitment_id):
        """Mark a promise kept."""
        return s32_commitments.fulfil(S32State, commitment_id)

    def broke(commitment_id):
        """Mark a promise broken by the player's own choice."""
        return s32_commitments.break_(S32State, commitment_id)

    def flag(name, default=0):
        """Read a world flag."""
        return s32_state.flag(S32State, name, default)

    def set_flag(name, value):
        """Set a world flag."""
        s32_state.set_flag(S32State, name, value)

    def bump(name, delta=1):
        """Increment a world flag and return the new value."""
        return s32_state.bump_flag(S32State, name, delta)

    def take(item_id):
        """Put an item in the player's hands."""
        if item_id not in S32State["inventory"]:
            S32State["inventory"].append(item_id)
        return item_id

    def has_item(item_id):
        """Return whether the player is carrying something."""
        return item_id in S32State["inventory"]

    def go(location_id):
        """Move the player."""
        s32_state.set_location(S32State, location_id)

    def advance(slots=1):
        """Let time pass.

        Rolls the weather and expires overdue promises when the day changes.
        Weather is deliberately a daily, not hourly, event: something the player
        can plan around rather than noise.
        """
        before = S32State["world"]["day"]
        s32_state.advance_time(S32State, slots)
        if S32State["world"]["day"] != before:
            s32_world.roll_weather(S32State, s32_rng())

    def s32_places_with_content():
        """Return locations where something is currently eligible.

        Used by the prototype's wander step so the player is not sent to an
        empty corridor. In the finished game this feeds a map screen: the point
        of a storylet system is lost if the player cannot find the storylets.
        """
        return s32_world.locations_with_content(
            S32State, s32_library, s32_director, s32_rng()
        )

    def phase():
        """Return the current escalation phase."""
        return S32State["world"]["phase"]

    def set_phase(new_phase):
        """Advance the escalation phase. Cannot move backwards."""
        s32_effects.apply_effect("phase = {}".format(new_phase), S32State)


# ---------------------------------------------------------------------------
# Director access
# ---------------------------------------------------------------------------

init python:

    def s32_select(category=None, tags=None):
        """Ask the director for the next storylet.

        Returns the `StoryletDef` or None. Selection happens at defined moments
        — a time-slot change, a location change, an explicit request — never on
        a frame timer. See docs/decisions/ADR-0002.
        """
        global S32LastSelection

        selection = s32_director.select(
            S32State, s32_rng(), category=category, tags=tags, keep_trace=config.developer
        )
        S32LastSelection = selection

        if config.developer:
            chosen = selection.storylet.id if selection.storylet else "<none>"
            s32_devlog.log(
                "narrative",
                "selected {} eligible={}/{}".format(
                    chosen, len(selection.eligible), len(selection.evaluations)
                ),
            )
        return selection.storylet

    def s32_play_effects(storylet):
        """Apply a storylet's effects and record it as played.

        Called AFTER the scene's label returns, so that rolling back past the
        scene also rolls back its consequences.
        """
        changes = s32_director.play(storylet, S32State)
        if config.developer and changes:
            s32_devlog.block("narrative", "{} effects".format(storylet.id), changes)
        return changes

    def s32_ready_anchor():
        """Return the id of the anchor that should fire now, or None.

        Anchors are strictly ordered and mandatory, so this is asked before the
        director is asked for anything else: an anchor that is ready outranks
        every storylet in the game by definition rather than by priority.
        """
        pending = s32_director.next_anchor(S32State, s32_rng())
        if pending is None:
            return None
        anchor_id, ready = pending
        return anchor_id if ready else None

    def s32_anchor_label(anchor_id):
        """Return the Ren'Py label for an anchor."""
        return s32_library.anchors[anchor_id].label

    def s32_place_name(location_id):
        """Return a location's display name, for the travel menu."""
        place = s32_library.locations.get(location_id)
        return place.display_name if place else location_id

    def s32_weekday():
        """Return the name of the weekday the run is currently on.

        A label, not a computed date. See s32_engine/calendar.py: nothing in
        this game parses a date, which is what lets a September with
        thirty-two days in it stay representable.
        """
        return s32_calendar_module.weekday_of(S32State["world"]["calendar_day"])

    def s32_explain(storylet_id):
        """Return the full eligibility trace for one storylet, as text.

        The answer to "why didn't that scene fire?", which is the question a
        writer asks every day once there are more than a few dozen scenes.
        """
        storylet = s32_library.storylets.get(storylet_id)
        if storylet is None:
            return "no such storylet: {}".format(storylet_id)
        return s32_director.evaluate(storylet, S32State, s32_rng()).format()

    def s32_check(condition):
        """Evaluate one condition string against the current state.

        Lets a scene reuse the same requirement language its metadata uses,
        instead of restating the logic in Python:

            if s32_check("rel iris.trust >= 30"):
        """
        ctx = s32_conditions.ConditionContext(S32State, s32_rng())
        return s32_conditions.evaluate(condition, ctx).passed


init python:

    def s32_finish_anchor(anchor_id):
        """Close out an anchor scene: apply its effects and record it.

        Anchors are `call`ed directly rather than selected, so nothing else
        applies their post-conditions. Recording the anchor in `persistent` as
        well as in the run is what lets a later playthrough know the player has
        already witnessed a beat, without the protagonist knowing anything.
        """
        anchor = s32_library.anchors.get(anchor_id)
        if anchor is None:
            raise Exception("unknown anchor: {}".format(anchor_id))

        changes = s32_effects.apply_all(anchor.effects, S32State)

        meta = s32_get_meta()
        s32_meta.record_anchor(meta, anchor_id)
        s32_set_meta(meta)

        if config.developer:
            s32_devlog.block("narrative", "anchor {}".format(anchor_id), changes)
        return changes


# ---------------------------------------------------------------------------
# Missing-asset placeholders
#
# Third-party assets are not committed (ADR-0003), so a fresh clone has none of
# them. The game must still run, lint and test in that state — it is how every
# new contributor first sees it, and it is the state CI runs in.
#
# So generated image definitions do not name a file directly. They call these
# helpers, which return the file when it is there and a clearly-labelled
# placeholder when it is not. Naming the file directly would make `renpy lint`
# report several hundred unloadable images on a fresh checkout, which is both
# useless noise and a permanently red CI job.
#
# A release build must NOT ship placeholders. `s32 doctor` reports how many
# would be substituted; this private playtest candidate documents its remaining
# placeholders and is checked against the current art gap list.
# ---------------------------------------------------------------------------

init offset = -5

init python:

    # Populated at init by the helpers below, for the dev log and the debug
    # screens. Not game state: it describes the build, not the run.
    s32_missing_assets = []

    def s32_placeholder(label, width, height):
        """Return a visibly wrong stand-in for an asset that is not installed.

        Deliberately ugly and deliberately legible. A silent fallback — a blank
        or a neutral box — would let a missing asset reach a screenshot.
        """
        return Fixed(
            Solid("#2a1a1a"),
            Text(
                "MISSING ASSET\n{size=-10}" + label + "{/size}",
                color="#d08a7a",
                size=28,
                text_align=0.5,
                xalign=0.5,
                yalign=0.5,
            ),
            xysize=(width, height),
        )

    def s32_asset(path, label, width, height):
        """Return `path` if it is loadable, else a labelled placeholder."""
        if renpy.loadable(path):
            return path
        s32_missing_assets.append(label)
        return s32_placeholder(label, width, height)

    def s32_sprite(path, label):
        """A character sprite, at the source packs' 720x1080 canvas."""
        return s32_asset(path, label, 720, 1080)

    def s32_bg(path, label):
        """A background, at the project's full 1920x1080 design size."""
        return s32_asset(path, label, 1920, 1080)


init 1 python:

    # Reported once, after every image has been defined. Loud in development
    # and absent from a release build, which must have no placeholders at all.
    if config.developer and s32_missing_assets:
        s32_devlog.log(
            "assets",
            "{} image(s) are placeholders — run `s32 assets fetch && s32 assets install`".format(
                len(s32_missing_assets)
            ),
        )


init offset = -5

init python:

    #: Where imported music lands. One constant, so a path change is one edit.
    S32_MUSIC_DIR = "audio/vendor"

    def s32_music_path(name):
        """Return the runtime path for a track name, without the extension."""
        return "{}/bgm_{}.ogg".format(S32_MUSIC_DIR, name)

    def s32_music(name, fadein=1.0, loop=True):
        """Play a track if it is installed; do nothing, loudly, if it is not.

        Audio has no equivalent of a visible placeholder — silence is silence —
        so a missing track is a dev-log line rather than a crash or a lint
        error. Without this, a checkout with no assets fails `renpy lint` on
        every `play music`, which is how a CI job ends up permanently red.
        """
        path = s32_music_path(name)
        if not renpy.loadable(path):
            s32_missing_assets.append("music / " + name)
            s32_devlog.log("assets", "music not installed: {}".format(path))
            return
        renpy.music.play(path, fadein=fadein, loop=loop)


init 1 python:

    # Set here rather than as a `define`, because `define` is evaluated before
    # any import and cannot ask whether the file exists.
    if renpy.loadable(s32_music_path("hope")):
        config.main_menu_music = s32_music_path("hope")


# ---------------------------------------------------------------------------
# Fonts
#
# The project's faces (Source Sans 3, Source Serif 4, both OFL) are fetched
# per-developer like every other asset, so a fresh checkout does not have them
# — and Ren'Py raises on a missing font rather than substituting one. That took
# out three screens and three testcases on a clean clone.
#
# These resolve once at init: the real face when installed, Ren'Py's bundled
# DejaVuSans when not. Screens name the constant, never a path.
# ---------------------------------------------------------------------------

init offset = -5

init python:

    #: Ren'Py bundles this, so it is always loadable.
    S32_FALLBACK_FONT = "DejaVuSans.ttf"

    def s32_font(filename):
        """Return the project font if installed, else the bundled fallback."""
        path = "gui/vendor/fonts/{}".format(filename)
        if renpy.loadable(path):
            return path
        s32_missing_assets.append("font / " + filename)
        return S32_FALLBACK_FONT

    S32_SANS = s32_font("SourceSans3-Regular.ttf")
    S32_SANS_SEMIBOLD = s32_font("SourceSans3-Semibold.ttf")
    S32_SERIF = s32_font("SourceSerif4-Regular.ttf")
    S32_SERIF_SEMIBOLD = s32_font("SourceSerif4-Semibold.ttf")
