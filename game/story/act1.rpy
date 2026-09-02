# ACT 1 — the playable week.
#
# This is the loop the game actually runs, and until Milestone 5 it did not
# exist. The prototype slice played six time slots on the first day and then
# stopped with a line saying it was a prototype, which meant that three of the
# five anchors -- the common room, the undated column, and the date itself --
# had never once fired outside the headless simulator. Fifty-eight storylets
# and a seven-day structure were reachable on paper and unreachable in the
# game.
#
# What it does is what the simulator has always modelled, with the two
# decisions the simulator makes for the player handed back:
#
#   anchors first          mandatory and strictly ordered, so an anchor that is
#                          ready outranks every storylet by definition
#   then the director      eligibility, priority tier, weighted draw
#   the player moves       three times a day, and whenever the place they are
#                          in has nothing left in it
#
# The loop ends when `the_date` has fired. That is the end of Act 1 and it is
# the only ending this build has; a run cannot run out of week first, because
# the anchors are day-gated and the guard below is a fault detector rather than
# a stopping rule.
#
# docs/narrative-design/ACT_1.md, docs/production/PLAYTEST_BUILD.md.


label start:

    $ s32_new_run()

    call s32_playtest_consent from _call_playtest_consent

    scene bg school_gate day with fade
    $ s32_music("hope", fadein=2.0)

    narrator "The bus leaves before you have finished getting your bag off it."

    narrator "Then it is quiet, in the specific way of a place that was loud ten minutes ago."

    narrator "The gate is open. Someone has wedged it with a brick, which suggests it does not stay open on its own."

    $ S32CurrentScene = "arrival"
    call s32_anchor_arrival from _call_anchor_arrival
    $ s32_pt_scene("arrival", is_anchor=True)

    $ S32CurrentScene = "first_shift"
    call s32_anchor_first_shift from _call_anchor_first_shift
    $ s32_pt_scene("first_shift", is_anchor=True)

    call s32_act1_week from _call_act1_week

    jump s32_act1_end


label s32_act1_week:

    python:
        # A fault detector, not a stopping rule. Seven in-fiction days is
        # about fifty slots; a run that has taken two hundred and still not
        # reached the last anchor has a content bug, and stopping is a better
        # failure than looping in front of a tester.
        _s32_steps = 0

    while "the_date" not in S32State["anchors_done"] and _s32_steps < 200:

        $ _s32_steps += 1

        # 1. An anchor, if one is ready. Anchors close themselves out: each
        #    label ends with s32_finish_anchor, which is what applies the
        #    effects and records it as done.
        $ _s32_anchor = s32_ready_anchor()

        if _s32_anchor is not None:

            $ S32CurrentScene = _s32_anchor
            $ renpy.call(s32_anchor_label(_s32_anchor))
            $ s32_pt_scene(_s32_anchor, is_anchor=True)

            if "the_date" in S32State["anchors_done"]:
                # The last one. Do not advance the clock past the scene the
                # act ends on.
                return

            call s32_pass_time from _call_pass_time_anchor

        else:

            # 2. Otherwise the director decides, exactly as it has since
            #    Milestone 1. Nothing here influences the selection.
            $ _s32_storylet = s32_select()

            if _s32_storylet is not None:

                $ S32CurrentScene = _s32_storylet.id
                $ renpy.call(_s32_storylet.label)
                $ s32_play_effects(_s32_storylet)
                $ s32_pt_scene(_s32_storylet.id)

                call s32_pass_time from _call_pass_time_storylet

            else:

                # 3. Nothing fits here. That is a normal outcome and not an
                #    error; the player goes somewhere else, and the walk takes
                #    the rest of the hour.
                call s32_elsewhere from _call_elsewhere

    return


label s32_pass_time:
    # One slot forward, and the two moments where the player gets to decide
    # where they are: a new day, and the turn of the afternoon or the evening.
    #
    # Offering the choice after every scene would put a map in front of a
    # reader forty times an hour. Offering it only when the room empties would
    # mean the player never chose anything, only ever accepted a redirection.

    python:
        _s32_day_before = S32State["world"]["day"]
        _s32_slot_before = S32State["world"]["time_slot"]

    $ advance(1)

    if S32State["world"]["day"] != _s32_day_before:
        call s32_day_break from _call_day_break

    elif S32State["world"]["time_slot"] in ("afternoon", "evening"):
        if S32State["world"]["time_slot"] != _s32_slot_before:
            call s32_where_next from _call_where_next

    return


label s32_day_break:
    # A card, a weekday and a date. Deliberately the plainest thing in the
    # game: the calendar is a completely normal school calendar in Act 1, and
    # any unease here would be spent before it is worth anything.

    stop music fadeout 1.5

    scene black with Dissolve(0.8)

    python:
        _s32_weekday = s32_weekday()
        _s32_date = S32State["world"]["calendar_day"]

    centered "{size=+8}[_s32_weekday]{/size}\n{size=-4}September [_s32_date]{/size}"

    call s32_where_next from _call_where_next_morning

    return


label s32_where_next:
    # Where the player goes. The candidate list is the one the engine reports
    # as having something in it, which is the same list the simulator's model
    # of a player uses -- a student in a small school can see where people are,
    # and a menu that offers nine empty corridors is a menu that teaches the
    # player not to read it.

    python:
        _s32_options = s32_places_with_content()
        _s32_here = S32State["world"]["location"]
        _s32_options = [p for p in _s32_options if p != _s32_here]

    if not _s32_options:
        return

    python:
        _s32_where = s32_ask_where(
            [(s32_place_name(p), p) for p in _s32_options]
            + [(__("Stay where you are."), _s32_here)]
        )

    $ s32_pt_travel(_s32_where)

    if _s32_where != _s32_here:
        $ go(_s32_where)
        scene expression "bg " + _s32_where with dissolve

    return


label s32_elsewhere:
    # The room has nothing left in it. Move, and let the walk take the hour.

    python:
        _s32_options = s32_places_with_content()
        _s32_day_was = S32State["world"]["day"]

    if _s32_options:

        python:
            _s32_where = s32_ask_where([(s32_place_name(p), p) for p in _s32_options])

        $ s32_pt_travel(_s32_where)
        $ go(_s32_where)
        $ advance(1)

        scene expression "bg " + _s32_where with dissolve

        narrator "You walk for a while without deciding to."

    else:

        # Three in the morning, or an afternoon with nobody in the building.
        # Nothing to choose between, so nothing is offered: a menu with one
        # option in it teaches a player that the menus do not matter.
        $ advance(1)

        narrator "The hour goes by without asking anything of you."

    # The walk can cross midnight like any other slot, and the day card has to
    # appear when it does. Missing it here was the first bug this loop had.
    if S32State["world"]["day"] != _s32_day_was:
        call s32_day_break from _call_day_break_elsewhere

    return


label s32_act1_end:
    # The end of the act, and the end of this build. It stops on the note the
    # week has been building to rather than on a summary: nothing here tells
    # the player what they have seen, how much of it there was, or what any of
    # it meant. That is the questionnaire's job, and the player's.

    scene bg dorm_room night with fade
    stop music fadeout 3.0

    narrator "The room came furnished. Someone else's dent in the mattress, someone else's mark on the desk where a lamp used to be."

    narrator "A column with no date in it. A date that is not a date. An ordinary account of each, and neither of them survives being put next to the other."

    narrator "Tomorrow there will be more boxes."

    $ s32_record_discovery("reached_the_date")
    $ s32_pt_complete()

    scene black with Dissolve(1.2)

    centered "{size=+6}End of Act 1{/size}"

    call screen s32_act1_complete

    return
