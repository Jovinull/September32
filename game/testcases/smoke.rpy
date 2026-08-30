# Automated smoke tests, run with `s32 renpy test` (which invokes
# `renpy . test <name>`).
#
# These are not a substitute for playing the game. What they defend against is
# the specific class of breakage that is invisible until launch: an init-order
# change that stops the engine loading, a renamed label, a screen that throws
# the moment it is opened. Those cost an afternoon to find by hand and a couple
# of seconds to find here.
#
# Note the syntax: Ren'Py's test language takes conditions as `eval <expr>`, and
# `simple_expression` stops at a comparison operator, so a comparison has to be
# parenthesised. `assert eval (x >= 1)`, never `assert x >= 1`.
#
# The suite is excluded from every build (see options.rpy).

testsuite global:
    teardown:
        exit


testcase smoke_main_menu:
    # The menu exists and its entries are reachable. Deliberately the smallest
    # possible test: if this fails, nothing else is worth running.
    $ _test.transition_timeout = 0.05

    click "Credits"
    pause 0.5
    click "Return"
    pause 0.3

    click "About"
    pause 0.4
    click "Return"
    pause 0.3

    exit


testcase smoke_start_and_choose:
    # Start a run, reach the first anchor, make a choice, and confirm the choice
    # actually moved the state. The assertions are the point: a test that only
    # clicks through proves the game does not crash, not that it works.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    # Anchor: arrival.
    advance until screen "choice"
    click "How do you know about the archive job?"

    # Anchor: first shift.
    advance until screen "choice"

    assert eval (S32State["traits"]["curious"] >= 1)
    assert eval (S32State["relationships"]["player->mara"]["familiarity"] > 0)
    assert eval ("arrival" in S32State["anchors_done"])

    click "What happens if something isn't labelled?"

    advance until eval ("first_shift" in S32State["anchors_done"]) timeout 20.0

    assert eval (S32State["relationships"]["player->iris"]["trust"] >= 4)

    exit


testcase smoke_director_runs:
    # The director selects storylets, and the storylets it selects are the ones
    # its priority rule says they should be.
    #
    # This test follows the *priority order*, not a guess at the RNG. After the
    # first shift the player is in the archive at midday, where `archive_intro`
    # (priority 70) is the only eligible scene; playing it unlocks
    # `old_photo_glimpse` (priority 75), which then outranks everything else in
    # the room. That chain is a property of the content, so the test can rely on
    # it — and if someone changes a priority, this fails and says so.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."

    advance until screen "choice"
    click "Seems straightforward."

    # archive_intro opens the accession record before it ends.
    advance until screen "s32_document" timeout 30.0
    click "Close"
    pause 0.4

    advance until eval (len(S32State.get("history", [])) >= 1) timeout 30.0
    assert eval (S32State["history"][0]["id"] == "archive_intro")

    # Second: the photograph, gated on having seen the first. It produces the
    # catalogue card, which also has to be closed.
    advance until screen "choice" timeout 30.0
    click "Put it in the maybe pile."

    advance until screen "s32_document" timeout 30.0
    click "Close"
    pause 0.4

    advance until eval (len(S32State.get("history", [])) >= 2) timeout 30.0

    assert eval (S32State["history"][1]["id"] == "old_photo_glimpse")
    assert eval ("old_photo_exists" in S32State["beliefs"]["player"])
    assert eval ("old_photo" in S32State["inventory"])
    assert eval (S32State["rng_counter"] > 0)

    exit


testcase smoke_rollback:
    # Rollback is the thing a visual novel cannot get wrong, and the reason the
    # run state is stored as plain dicts (ADR-0007). This checks the state
    # really does unwind, not just the text.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Does everyone get met at the gate?"
    pause 0.4

    # The chosen option raises Mara's suspicion by 3. The expected value is
    # written literally rather than captured into a store variable: a variable
    # set here would itself be rolled back, and the test would end up comparing
    # a rolled-back value against a rolled-back value and always pass.
    assert eval (S32State["relationships"]["player->mara"]["suspicion"] >= 3)

    # Rollback is driven through the same action the UI uses, rather than a
    # keysym, so the test exercises the path a player actually takes.
    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.5

    assert eval (S32State["relationships"]["player->mara"]["suspicion"] < 3)

    exit


testcase smoke_debug_screens:
    # The developer inspectors open and render without throwing. They read a lot
    # of engine state, which makes them an unusually good canary for a
    # state-shape change that nothing else notices.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    run Show("s32_storylet_inspector")
    pause 0.6
    run Hide("s32_storylet_inspector")
    pause 0.3

    run Show("s32_character_inspector")
    pause 0.6
    run Hide("s32_character_inspector")
    pause 0.3

    run Show("s32_world_inspector")
    pause 0.6
    run Hide("s32_world_inspector")
    pause 0.3

    exit


# Ren'Py runs `testcase default` when `renpy . test` is given no name.
testcase default:
    $ _test.transition_timeout = 0.05
    click "Start"
    pause 1.0
    advance until screen "choice"
    click "Thanks. Lead on."
    exit
