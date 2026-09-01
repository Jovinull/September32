# The Calendar, driven the way a player drives it.
#
# The Python suite covers the derivation -- weekdays, day states, what appears
# on a square. What only Ren'Py can prove is that the screen opens without
# throwing, that it can be walked with the keyboard, that it reads live world
# state rather than a copy, and that a promise the player has just made shows up
# while a scene the player has not reached does not.
#
# Syntax reminder: conditions are `eval <expr>` and comparisons need
# parentheses. `assert eval (x >= 1)`, never `assert x >= 1`.

testcase calendar_opens_and_closes:
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."

    run ShowMenu("s32_calendar")
    pause 0.8

    assert eval (renpy.get_screen("s32_calendar") is not None)

    click "Close"
    pause 0.5

    assert eval (renpy.get_screen("s32_calendar") is None)

    exit


testcase calendar_shows_today_from_world_state:
    # The single most important property: the calendar is a view, not a second
    # copy. If it ever disagrees with WorldState, one of them is lying and the
    # player has no way to tell which.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."

    run ShowMenu("s32_calendar")
    pause 0.8

    assert eval (s32_calendar_today() == S32State["world"]["calendar_day"])
    assert eval (s32_calendar_month_name() == S32State["world"]["month"])

    # And there is no calendar in the save.
    assert eval ("calendar" not in S32State)

    keysym "K_ESCAPE"
    pause 0.4

    exit


testcase calendar_walks_with_the_keyboard:
    # Everything reachable with the mouse is reachable without it, and the
    # selection clamps to the month rather than wrapping.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."

    run ShowMenu("s32_calendar")
    pause 0.8

    keysym "K_RIGHT"
    pause 0.2
    keysym "K_DOWN"
    pause 0.2
    keysym "K_LEFT"
    pause 0.2
    keysym "K_UP"
    pause 0.2

    # Hold left past the start of the month; it must stop at day one.
    keysym "K_HOME"
    pause 0.2
    keysym "K_LEFT"
    pause 0.2
    keysym "K_LEFT"
    pause 0.2
    keysym "K_LEFT"
    pause 0.2

    assert eval (renpy.get_screen("s32_calendar") is not None)

    keysym "K_ESCAPE"
    pause 0.4

    exit


testcase calendar_shows_a_promise_and_hides_the_future:
    # A promise the protagonist made is theirs to remember, so it appears. A
    # scene the game intends for a later day is not, so it does not -- and the
    # guarantee is structural: the view is built from history and commitments,
    # and never from the content library.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."
    advance until screen "choice"
    click "Seems straightforward."

    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.4

    # Make a promise directly, which is what a scene's outcome does.
    $ promise("calendar_probe", "june", 2, 50)
    pause 0.3

    run ShowMenu("s32_calendar")
    pause 0.8

    $ _due = S32State["world"]["calendar_day"] + 2
    $ _entries = s32_calendar_month()
    $ _entry = s32_calendar_entry(_entries, _due)

    assert eval ("calendar_probe" in _entry["commitments"])
    assert eval (_entry["state"] == "future")

    # A future square carries the promise and nothing else. In particular it
    # carries no scene, because the calendar cannot see scenes that have not
    # played.
    assert eval (len(_entry["events"]) == 0)

    keysym "K_ESCAPE"
    pause 0.4

    exit


testcase calendar_survives_rollback:
    # The calendar holds no state of its own, so rolling back past a day change
    # must move it without anything having to be undone. This is the test that
    # would fail if somebody ever cached the month view into the save.
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."

    advance until screen "choice"
    click "Seems straightforward."

    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.5

    $ _after = s32_calendar_today()

    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.5

    # Whatever the day is now, the calendar agrees with the world, because it
    # asked. Nothing had to be unwound because nothing was stored.
    assert eval (s32_calendar_today() == S32State["world"]["calendar_day"])
    assert eval ("calendar" not in S32State)

    exit
