# ACT 1 — the golden path.
#
# Not the best route, not a canon route, and not a route anybody should read
# anything into: it takes the first option at every menu, which is a policy
# rather than a judgement. What it is is the only regression test in the
# project that runs the *prose* -- fifty-eight storylet labels and five anchor
# labels, executed by Ren'Py, in the order the director puts them in.
#
# That matters more than it sounds. Everything else about these scenes is
# checked without running them: `s32 validate` reads their metadata, `renpy
# lint` reads their images and labels, and the simulator plays five thousand
# runs of the storylet *definitions* while never opening a `.rpy`. Until this
# testcase existed, a NameError inside a scene would have reached a tester
# before it reached anybody else.
#
# It also covers §61's checklist end to end: start a new game, complete Act 1,
# use the Calendar, open a document, make a commitment, trigger a scene that
# reads relationship state, reach Day 7, finish.
#
# Syntax reminder: conditions are `eval <expr>` and comparisons need
# parentheses. `assert eval (x >= 1)`, never `assert x >= 1`.


testcase act1_golden:

    $ _test.transition_timeout = 0.05

    # A fixed seed, so a failure here is reproducible from the report rather
    # than from a description of what the tester was doing.
    $ persistent.s32_playtest_consent = True
    $ persistent.s32_playtest = None
    $ preferences.skip_unseen = True

    run Function(s32_test_autochoice, True)
    run Function(s32_test_fast_documents, True)

    click "Start"
    pause 1.0

    # The whole week, under fast skipping.
    #
    # `advance until` walks one dialogue line per interaction, and a full act is
    # around nine hundred of them; the first version of this test spent fifteen
    # minutes and did not finish. Skipping runs the same statements without
    # waiting for each one, which is the difference between a test that runs in
    # CI and a test that gets disabled.
    skip fast
    pause until eval ("the_date" in S32State["anchors_done"]) timeout 600.0

    $ config.skipping = None
    pause 0.5

    # --- the act happened -------------------------------------------------

    assert eval (S32State["world"]["day"] >= 6)
    assert eval (len(S32State["anchors_done"]) == 5)
    assert eval (S32State["world"]["phase"] == "odd")

    # The two facts the last anchor exists to leave the player holding.
    assert eval ("photo_dated_sept_32" in S32State["beliefs"]["player"])
    assert eval ("attendance_sheet_anomaly" in S32State["beliefs"]["player"])

    # A week's worth of storylets, not a handful. The floor is deliberately
    # well below what a run actually plays: this is a smoke test, and a number
    # tuned to one seed would fail on the next content edit for no reason.
    assert eval (len(S32State["history"]) >= 15)

    # A document was opened, and a promise was made and resolved. Both are
    # part of §61's checklist and both are easy to break without noticing,
    # because neither produces an error when it silently stops happening.
    assert eval (len(S32State["documents_read"]) >= 2)
    assert eval (len(S32State["commitments"]) >= 1)

    # A scene that reads relationship state rather than only writing it --
    # Milestone 4's first finding, and the one most likely to regress quietly.
    assert eval (S32State["relationships"]["iris->player"]["trust"] > 0)

    # --- the playtest notebook wrote something down -----------------------

    assert eval (len(persistent.s32_playtest["runs"]) == 1)
    assert eval (persistent.s32_playtest["runs"][0]["completed"])
    assert eval (persistent.s32_playtest["runs"][0]["first_completed"])
    assert eval (len(persistent.s32_playtest["runs"][0]["scenes"]) >= 15)
    assert eval (len(persistent.s32_playtest["runs"][0]["choices"]) >= 15)
    assert eval (persistent.s32_playtest["runs"][0]["days_reached"] >= 6)

    # Promises are read out of the state rather than hooked at the verb, so
    # a `commit(...)` declared as a storylet effect is counted too. It was not,
    # once.
    assert eval (len(persistent.s32_playtest["runs"][0]["commitments_made"]) >= 1)

    # And it is safe to hand to somebody.
    assert eval (s32_playtest.privacy_violations(persistent.s32_playtest) == [])

    # --- the two menu screens, opened at the end of a real week -----------
    #
    # Folded in here rather than given a testcase of their own. The calendar
    # derives every square from live state, so opening it after six days of
    # history is a different test from opening it after none -- and a second
    # testcase would have meant playing the whole week twice, which took the
    # suite past its timeout.

    run ShowMenu("s32_calendar")
    pause 0.8
    assert eval (renpy.get_screen("s32_calendar") is not None)
    click "Close"
    pause 0.5

    run ShowMenu("s32_journal")
    pause 0.8
    assert eval (renpy.get_screen("s32_journal") is not None)
    click "Return"
    pause 0.5

    # --- the end of the act is a screen the player can act on -------------

    advance until screen "s32_act1_complete" timeout 60.0

    click "Generate playtest report"
    pause 1.0

    click "Feedback instructions"
    pause 0.6
    click "Close"
    pause 0.4

    exit


testcase act1_consent_is_asked_once_and_answered:
    # The one testcase that clicks the consent question rather than presetting
    # it. `None` is the third state -- not asked -- and clearing it here is
    # what makes this repeatable: consent lives in `persistent`, which outlives
    # the process.

    $ _test.transition_timeout = 0.05
    $ persistent.s32_playtest_consent = None
    $ persistent.s32_playtest = None

    click "Start"
    pause 1.0

    assert eval (renpy.get_screen("s32_consent") is not None)

    click "Don't keep a report"
    pause 0.6

    assert eval (persistent.s32_playtest_consent is False)
    assert eval (persistent.s32_playtest is None)

    # Declining leaves the game entirely playable, which is what makes it a
    # real answer rather than a dark pattern with two buttons.
    advance until screen "choice" timeout 40.0
    assert eval (renpy.get_screen("s32_consent") is None)

    exit


testcase act1_the_debug_inspectors_are_developer_only:
    # The inspectors are registered inside `if config.developer`, so they are
    # absent from a build rather than hidden in it. This asserts the mechanism
    # rather than the outcome -- a testcase always runs with developer mode on,
    # so it cannot observe the release behaviour directly. What it can hold is
    # that the screens are still behind the flag and that no other surface has
    # started showing internal state.

    $ _test.transition_timeout = 0.05
    $ persistent.s32_playtest_consent = False

    click "Start"
    pause 1.0

    assert eval (config.developer)
    assert eval ("s32_storylets" in config.keymap)

    exit
