# The private playtest recorder.
#
# What this is: a local notebook. It writes down which scenes a tester saw,
# which options they took, and how long they played, so that a questionnaire
# answered from memory can be read beside what actually happened.
#
# What this is not, and what several tests exist to keep it from becoming:
#
#   * Telemetry. Nothing here opens a socket. There is no server, no account,
#     no upload, and no code path that could acquire one without the network
#     guard in tests/test_playtest_privacy.py going red.
#   * A profile. The report holds storylet ids, choice ids and counts. No
#     name, no path, no machine identifier, no clock reading.
#   * On by default. The tester is asked once, in plain words, and "no" is a
#     real answer that leaves the game fully playable.
#
# The recording lives in `persistent`, not in the run state, for two reasons.
# It has to survive quitting, which the run state does not. And it must not be
# rolled back: what a tester did includes the bits they took back, and a
# notebook that unwrites itself when somebody scrolls up is not a record of
# anything.
#
# docs/legal/PRIVACY.md, docs/playtest/PLAYTEST_DATA.md.

init offset = -5

init python:

    from s32_engine import playtest as s32_playtest


# ---------------------------------------------------------------------------
# Installation identity
# ---------------------------------------------------------------------------

default persistent.s32_install_id = None
default persistent.s32_playtest = None

# None means "not asked yet", which is a third state and has to be one: it is
# what makes the consent question appear exactly once.
default persistent.s32_playtest_consent = None


init python:

    def s32_install_id():
        """Return this installation's number, generating it once.

        A number with no relationship to the machine. It exists so that a
        tester has a short code to quote on the questionnaire, and so that two
        installations do not collide -- not so that anybody can be recognised.

        `renpy.random` rather than `s32_engine.rng.Rng` is deliberate and is
        the one place in the project where that is true. Rng exists so that
        rolling back and replaying gives the same answer, which is a property
        of the *run*. This value is generated once, before any run, is never
        rolled back, and must differ between two people who install the same
        build -- the opposite requirement.
        """
        if persistent.s32_install_id is None:
            persistent.s32_install_id = renpy.random.randint(1, 2 ** 31 - 1)
            renpy.save_persistent()
        return persistent.s32_install_id

    def s32_session_code():
        """Return the code the tester writes at the top of the questionnaire."""
        return s32_playtest.session_code(s32_install_id())


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

init python:

    def s32_get_report():
        """Return the stored report, creating one the first time it is asked for."""
        stored = persistent.s32_playtest
        if not stored or stored.get(
            "playtest_report_schema_version"
        ) != s32_playtest.PLAYTEST_REPORT_SCHEMA_VERSION:
            # A report from an older schema is not migrated. It belongs to a
            # build that is no longer the one being tested, and merging the
            # two would produce a file that describes neither.
            stored = s32_playtest.new_report(
                S32Build, s32_session_code(), consent=bool(persistent.s32_playtest_consent)
            )
            persistent.s32_playtest = stored
        return stored

    def s32_recording():
        """Return whether the tester agreed to a report being kept."""
        return persistent.s32_playtest_consent is True

    def s32_set_consent(agreed):
        """Record the tester's answer, and start or discard the report."""
        persistent.s32_playtest_consent = bool(agreed)
        if agreed:
            report = s32_get_report()
            report["consent"] = True
        else:
            # Not merely stopped: removed. Somebody who declines should not
            # have a file about them sitting in their save folder.
            persistent.s32_playtest = None
        renpy.save_persistent()

    def s32_pt_run():
        """Return the record for the run in progress, or None.

        Every recorder below goes through here, so consent is checked in one
        place rather than in fifteen.
        """
        if not s32_recording():
            return None
        return s32_playtest.current_run(s32_get_report())

    def s32_pt_start_run(seed):
        """Open a record for a playthrough that has just begun."""
        if not s32_recording():
            return
        s32_playtest.new_run(s32_get_report(), seed)
        renpy.save_persistent()

    def s32_pt_scene(scene_id, is_anchor=False):
        """Record a scene as played."""
        run = s32_pt_run()
        if run is None:
            return
        run["scenes"].append(scene_id)
        if is_anchor:
            run["anchors"].append(scene_id)
        run["days_reached"] = max(run["days_reached"], S32State["world"]["day"])
        run["active_seconds"] = int(renpy.get_game_runtime())
        s32_pt_commitments()
        renpy.save_persistent()

    def s32_pt_choice(items, chosen):
        """Record which option of a menu was taken.

        `chosen` is the index Ren'Py assigns to the option inside its own menu
        statement, which is why the identifier is stable across a typo fix in
        the caption. See s32_engine.playtest.choice_id.
        """
        run = s32_pt_run()
        if run is None:
            return
        caption = ""
        for label, value in items:
            inner = getattr(value, "value", value)
            if inner == chosen:
                caption = label
                break
        run["choices"].append(
            s32_playtest.choice_id(S32CurrentScene or "unattributed", chosen, caption)
        )

    def s32_pt_travel(location_id):
        """Record where the player chose to go.

        Movement is a choice like any other and it goes in the same list, so
        that a report reads as one sequence of decisions rather than as a
        dialogue track with the navigation missing.
        """
        run = s32_pt_run()
        if run is None:
            return
        run["choices"].append("travel." + location_id)

    def s32_pt_document(document_id):
        """Record a document being opened, and whether it had been read before."""
        run = s32_pt_run()
        if run is None:
            return
        if document_id in run["documents"]:
            run["archive_reopens"] += 1
        run["documents"].append(document_id)

    def s32_pt_screen(name):
        """Record the tester opening the calendar or the journal.

        H17 asks whether anybody opens the calendar without being told to, and
        that is not a question a tester can answer accurately about themselves.
        """
        run = s32_pt_run()
        if run is None:
            return
        if name == "calendar":
            run["calendar_opens"] += 1
        elif name == "journal":
            run["journal_opens"] += 1

    def s32_pt_commitments():
        """Bring the run's promise lists up to date from the state.

        Read from the state rather than recorded where a promise is made,
        because there are two ways to make one and only one of them is the
        `promise()` verb: a storylet's declared `commit(...)` effect goes
        through the effects engine instead. The first version of this hooked
        the verb, and the golden path duly reported a run with a commitment in
        its state and none in its report.
        """
        run = s32_pt_run()
        if run is None:
            return
        for record in S32State.get("commitments", []):
            cid, status = record["id"], record["status"]
            if cid not in run["commitments_made"]:
                run["commitments_made"].append(cid)
            if status == "kept" and cid not in run["commitments_kept"]:
                run["commitments_kept"].append(cid)
            elif status == "broken" and cid not in run["commitments_broken"]:
                run["commitments_broken"].append(cid)

    def s32_pt_load():
        """Record a save being reloaded."""
        run = s32_pt_run()
        if run is None:
            return
        run["loads"] += 1

    def s32_pt_complete():
        """Record the run reaching the end of Act 1."""
        run = s32_pt_run()
        if run is None:
            return
        run["active_seconds"] = int(renpy.get_game_runtime())
        s32_pt_commitments()
        s32_playtest.complete_run(s32_get_report(), run)
        renpy.save_persistent()


# ---------------------------------------------------------------------------
# Choice interception
# ---------------------------------------------------------------------------

# Which scene is on screen. Set by the Act 1 loop before it calls a label, so a
# menu can name the storylet it belongs to without every storylet having to say
# so itself. `default` rather than `define`: it changes during a run, so it
# belongs in the save and in rollback like any other run variable.
default S32CurrentScene = ""


init python:

    def s32_menu(items, *args, **kwargs):
        """Ren'Py's menu, with the answer written down on the way past.

        Overriding `store.menu` is how nvl mode does the same thing, and it is
        the only approach that does not require editing all forty-odd menus in
        the game. Editing them would have meant touching every scene in a
        milestone whose whole instruction was to leave the writing alone.
        """
        rv = renpy.display_menu(items, *args, **kwargs)
        try:
            s32_pt_choice(items, rv)
        except Exception:
            # A recorder must never be the reason a choice fails to register.
            # The tester is mid-scene; the notebook is not the priority.
            pass
        return rv

    menu = s32_menu

    def s32_ask_where(items):
        """Show the travel menu and return the chosen location.

        A seam rather than a direct `renpy.display_menu` call, for one reason:
        the golden path answers menus by replacing the store's `menu`, and the
        travel menu does not go through it. Without this the harness stalled at
        the first junction of the first day, which is exactly the sort of thing
        a test that never finishes does not tell you.
        """
        return renpy.display_menu(items)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

init python:

    def s32_report_dir():
        """Return the directory the report is written to.

        The save directory, because it is per-user, already exists, is already
        writable, and is somewhere a tester can be talked to over a message.
        """
        return config.savedir

    def s32_export_report():
        """Write the report beside the saves. Returns a message for the screen.

        Both forms are written: the JSON is what `s32 playtest summarize`
        reads, and the Markdown is so that a tester can see exactly what they
        would be sending before they send it. Being able to read your own
        report is most of what makes the consent meaningful.
        """
        if not s32_recording():
            return __("No report was kept for this session.")

        report = s32_get_report()
        run = s32_playtest.current_run(report)
        if run is not None:
            run["active_seconds"] = int(renpy.get_game_runtime())

        problems = s32_playtest.privacy_violations(report)
        if problems:
            # Refuses rather than warns. This is the check that decides whether
            # a file is safe to send, and a check that can be clicked past is
            # not one.
            return __("The report was not written: {}").format("; ".join(problems))

        try:
            with open(os.path.join(s32_report_dir(), "playtest-report.json"), "w") as handle:
                handle.write(s32_playtest.to_json(report))
            with open(os.path.join(s32_report_dir(), "playtest-summary.md"), "w") as handle:
                handle.write(s32_playtest.summary_markdown(report))
        except OSError as exc:
            return __("Could not write the report: {}").format(exc)

        renpy.save_persistent()
        return __("Saved to {}").format(s32_report_dir())
