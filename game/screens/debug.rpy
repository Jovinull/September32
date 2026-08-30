# Developer inspectors.
#
# Available only when config.developer is on, which means they are absent from
# a release build entirely — not hidden, absent. A debug overlay that ships is
# both a spoiler and a support burden.
#
# These matter more than they look. Once there are several hundred storylets,
# "why didn't that scene fire?" is the question a writer asks every day, and an
# engine that cannot answer it in one keypress is an engine nobody trusts.
#
#   Shift+D  Ren'Py's own developer menu
#   Shift+S  Storylet inspector
#   Shift+C  Character, relationship and knowledge inspector
#   Shift+W  World state

screen s32_debug_frame(title):
    ## Shared chrome for every inspector: a scrollable panel that does not
    ## fight the game underneath it.
    zorder 200
    modal True

    add "#000000c0"

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1500
        ysize 900
        padding (30, 24)
        background "#12100ee8"

        vbox:
            spacing 12

            hbox:
                xfill True
                text title style "s32_debug_title"
                textbutton "close" action Hide() text_style "s32_debug_text"

            null height 4

            side "c r":
                area (0, 0, 1420, 780)
                viewport id "s32_debug_vp":
                    mousewheel True
                    draggable True
                    transclude
                vbar style "vscrollbar"


style s32_debug_title is text:
    size 26
    color "#e8e2d4"
    font "gui/vendor/fonts/SourceSans3-Semibold.ttf"

style s32_debug_text is text:
    size 19
    color "#cfc8b8"
    font "gui/vendor/fonts/SourceSans3-Regular.ttf"

style s32_debug_pass is text:
    size 19
    color "#9fc48a"

style s32_debug_fail is text:
    size 19
    color "#d08a7a"

style s32_debug_head is text:
    size 21
    color "#e8c98a"


screen s32_storylet_inspector():
    ## Every storylet, why it is or is not eligible, and a button to force it.
    ##
    ## Forcing a storylet is what makes a mid-scene bug reproducible in ten
    ## seconds instead of ten minutes of replaying to reach it.

    use s32_debug_frame(_("Storylet inspector")):
        vbox:
            spacing 10

            ## Ren'Py's text interpolation evaluates what is inside the
            ## brackets, so a dict subscript would look up a *variable* named
            ## after the key. Values are unpacked into plain locals instead.
            $ _dbg = s32_debug_snapshot()
            $ _dbg_summary = _dbg["summary"]

            text "[_dbg_summary]" style "s32_debug_head"

            null height 6

            for entry in _dbg["storylets"]:

                frame:
                    xfill True
                    padding (14, 10)
                    background ("#1e6b3a30" if entry["eligible"] else "#00000030")

                    vbox:
                        spacing 4

                        hbox:
                            spacing 14
                            xfill True
                            $ _sid = entry["id"]
                            $ _weights = "p{} w{:g}".format(entry["priority"], entry["weight"])
                            text "[_sid]" style "s32_debug_head"
                            text "[_weights]" style "s32_debug_text"
                            textbutton "force" action [Hide("s32_storylet_inspector"), Function(s32_force_storylet, _sid)] text_style "s32_debug_text"

                        for line in entry["trace"]:
                            if line.startswith("PASS"):
                                text "[line]" style "s32_debug_pass"
                            elif line.startswith("FAIL"):
                                text "[line]" style "s32_debug_fail"
                            else:
                                text "[line]" style "s32_debug_text"


screen s32_character_inspector():
    ## Who is present, how they feel, and what they believe.

    use s32_debug_frame(_("Characters, relationships and knowledge")):
        vbox:
            spacing 16

            $ _dbg = s32_debug_characters()

            for entry in _dbg:
                frame:
                    xfill True
                    padding (14, 10)
                    background "#00000030"

                    vbox:
                        spacing 4
                        $ _head = "{}  ({})".format(entry["name"], entry["id"])
                        $ _status = "present={}  mood={}  availability={}".format(entry["present"], entry["mood"], entry["availability"])
                        $ _toward = entry["to_them"]
                        $ _beliefs = entry["beliefs"]
                        text "[_head]" style "s32_debug_head"
                        text "[_status]" style "s32_debug_text"
                        text "player -> them: [_toward]" style "s32_debug_text"
                        text "beliefs: [_beliefs]" style "s32_debug_text"

            frame:
                xfill True
                padding (14, 10)
                background "#00000030"
                vbox:
                    spacing 4
                    $ _traits = s32_traits.profile(S32State)
                    $ _known = s32_debug_player_knowledge()
                    $ _carrying = s32_debug_inventory()
                    $ _promises = s32_debug_commitments()
                    text _("Player") style "s32_debug_head"
                    text "traits: [_traits]" style "s32_debug_text"
                    text "knows: [_known]" style "s32_debug_text"
                    text "carrying: [_carrying]" style "s32_debug_text"
                    text "promises: [_promises]" style "s32_debug_text"


screen s32_world_inspector():
    ## Where and when, plus every flag that has been touched.

    use s32_debug_frame(_("World state")):
        vbox:
            spacing 8

            $ _w = S32State.get("world", {})
            $ _when = "day {}  |  {} {}  |  {}".format(_w.get("day"), _w.get("month"), _w.get("calendar_day"), _w.get("time_slot"))
            $ _where = _w.get("location")
            $ _weather = _w.get("weather")
            $ _phase = _w.get("phase")

            text "[_when]" style "s32_debug_head"
            text "location: [_where]" style "s32_debug_text"
            text "weather:  [_weather]" style "s32_debug_text"
            text "phase:    [_phase]" style "s32_debug_text"

            null height 8
            text _("Flags") style "s32_debug_head"
            for _flag_name, _flag_value in sorted(_w.get("flags", {}).items()):
                $ _flag_line = "  {} = {}".format(_flag_name, _flag_value)
                text "[_flag_line]" style "s32_debug_text"

            null height 8
            text _("Recent events") style "s32_debug_head"
            for _event in reversed(_w.get("recent_events", [])):
                text "  [_event]" style "s32_debug_text"

            null height 8
            text _("Anchors done") style "s32_debug_head"
            for _anchor in S32State.get("anchors_done", []):
                text "  [_anchor]" style "s32_debug_text"

            null height 8
            text _("History") style "s32_debug_head"
            for _record in reversed(S32State.get("history", [])[-20:]):
                $ _history_line = "  d{} {}  {}".format(_record["day"], _record["time_slot"], _record["id"])
                text "[_history_line]" style "s32_debug_text"

            null height 8
            $ _schema = "  save schema v{}  |  build {}".format(S32State.get("save_schema_version"), S32State.get("game_version"))
            $ _rng = "  seed {}  |  rng draws {}".format(S32State.get("seed"), S32State.get("rng_counter"))
            $ _runs = "  runs started: {}".format(s32_debug_runs())

            text _("Save / meta") style "s32_debug_head"
            text "[_schema]" style "s32_debug_text"
            text "[_rng]" style "s32_debug_text"
            text "[_runs]" style "s32_debug_text"


init python:

    def s32_debug_snapshot():
        """Gather everything the storylet inspector shows.

        Built fresh each time the screen is shown rather than cached: a stale
        debug view is worse than none, because it is believed.
        """
        evaluations = s32_director.evaluate_all(S32State, s32_rng())
        world = S32State.get("world", {})

        rows = []
        for evaluation in sorted(evaluations, key=lambda e: (not e.eligible, -e.priority, e.storylet_id)):
            trace = []
            trace.extend("FAIL " + reason for reason in evaluation.rejections)
            trace.extend(r.format() for r in evaluation.requirement_results)
            trace.extend("BLOCK " + r.format() for r in evaluation.blocker_results if r.passed)
            rows.append({
                "id": evaluation.storylet_id,
                "eligible": evaluation.eligible,
                "priority": evaluation.priority,
                "weight": evaluation.weight,
                "trace": trace or ["(no conditions)"],
            })

        eligible_count = sum(1 for e in evaluations if e.eligible)
        return {
            "storylets": rows,
            "summary": "{} of {} eligible  |  day {} {}  |  {}  |  phase {}".format(
                eligible_count,
                len(evaluations),
                world.get("day"),
                world.get("time_slot"),
                world.get("location"),
                world.get("phase"),
            ),
        }

    def s32_debug_characters():
        """Gather the character inspector's rows."""
        rows = []
        for char_id in sorted(s32_library.characters):
            definition = s32_library.characters[char_id]
            state = S32State.get("characters", {}).get(char_id, {})
            beliefs = S32State.get("beliefs", {}).get(char_id, {})
            rows.append({
                "id": char_id,
                "name": definition.display_name,
                "present": state.get("present"),
                "mood": state.get("mood"),
                "availability": state.get("availability"),
                "to_them": s32_relationships.summary(S32State, char_id),
                "beliefs": ", ".join(
                    "{}={}".format(fact, entry["stance"]) for fact, entry in sorted(beliefs.items())
                ) or "—",
            })
        return rows

    def s32_debug_player_knowledge():
        """Return the player's known facts as one line."""
        return ", ".join(s32_knowledge.known_facts(S32State)) or "—"

    def s32_debug_inventory():
        """Return the player's inventory as one line."""
        return ", ".join(S32State.get("inventory", [])) or "—"

    def s32_debug_commitments():
        """Return open and resolved promises as one line."""
        records = S32State.get("commitments", [])
        if not records:
            return "—"
        return ", ".join("{}:{}".format(r["id"], r["status"]) for r in records)

    def s32_debug_runs():
        """Return the cross-run counter."""
        return s32_get_meta()["runs_started"]

    def s32_force_storylet(storylet_id):
        """Jump straight into a storylet, ignoring its requirements.

        Development only. Effects are applied on return exactly as they would
        be in normal play, so a forced scene leaves the state in the shape a
        real playthrough would.
        """
        storylet = s32_library.storylets.get(storylet_id)
        if storylet is None:
            return
        renpy.call_in_new_context(storylet.label)
        s32_play_effects(storylet)


init python:

    ## Bindings. Registered only in developer mode, so the keys do nothing at
    ## all in a release build.
    if config.developer:
        config.keymap.setdefault("s32_storylets", []).append("shift_K_s")
        config.keymap.setdefault("s32_characters", []).append("shift_K_c")
        config.keymap.setdefault("s32_world", []).append("shift_K_w")

        config.underlay.append(
            renpy.Keymap(
                s32_storylets=renpy.curry(renpy.show_screen)("s32_storylet_inspector"),
                s32_characters=renpy.curry(renpy.show_screen)("s32_character_inspector"),
                s32_world=renpy.curry(renpy.show_screen)("s32_world_inspector"),
            )
        )
