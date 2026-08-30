# PROTOTYPE / NON-FINAL
#
# The vertical slice. Five to fifteen minutes, and its purpose is to exercise
# every system end to end rather than to tell the story:
#
#   dialogue, sprite, background, music, a choice, a relationship change,
#   a knowledge grant, a storylet selection, a commitment, persistent meta,
#   and the debug inspector.
#
# What it deliberately does NOT do is explain September 32. The player leaves
# this slice with one small thing that does not fit, and no framework for it.
# See docs/narrative-design/PACING.md: before you break the routine, the player
# has to like the routine.

label start:

    $ s32_new_run()

    scene bg school_gate day with fade
    $ s32_music("hope", fadein=2.0)

    narrator "The bus leaves before you have finished getting your bag off it."

    narrator "Then it is quiet, in the specific way of a place that was loud ten minutes ago."

    narrator "The gate is open. Someone has wedged it with a brick, which suggests it does not stay open on its own."

    call s32_anchor_arrival from _call_anchor_arrival

    call s32_anchor_first_shift from _call_anchor_first_shift

    # From here the director decides. The prototype runs a handful of slots so
    # the recombination is visible, then stops on a deliberate note rather than
    # trailing off.
    call s32_prototype_loop from _call_prototype_loop

    jump s32_prototype_end


label s32_prototype_loop:
    # Six time slots of storylet-driven play. Real chapters will not look like
    # this — anchors will punctuate it — but this is the shape the engine has.

    python:
        _s32_slots = 0

    while _s32_slots < 6:

        $ _s32_storylet = s32_select()

        if _s32_storylet is None:
            # Nothing fits here. That is a normal outcome, not an error: the
            # player moves on and time passes. The simulator reports it as a
            # dead end only if it happens repeatedly.
            $ s32_devlog.log("narrative", "nothing eligible at {}".format(S32State["world"]["location"]))
            call s32_wander from _call_wander
        else:
            $ renpy.call(_s32_storylet.label)
            $ s32_play_effects(_s32_storylet)
            $ advance(1)

        $ _s32_slots += 1

    return


label s32_wander:
    # Move somewhere else and let the afternoon go by. Written as a scene rather
    # than a silent state change because a jump cut with no acknowledgement
    # reads as a bug.

    # Go where something is happening, rather than at random. A player in a
    # small school can see where people are, and a wander that ignores that
    # produces the experience of an empty corridor.
    python:
        _s32_options = s32_places_with_content() or ["courtyard", "hallway_east", "dorm_room"]
        _s32_where = s32_rng().choice(_s32_options)

    $ go(_s32_where)
    $ advance(1)

    scene expression "bg " + _s32_where with dissolve

    narrator "You walk for a while without deciding to."

    return


label s32_prototype_end:

    scene bg dorm_room evening with fade
    stop music fadeout 2.0

    narrator "The room came furnished. Someone else's dent in the mattress, someone else's mark on the desk where a lamp used to be."

    if knows("old_photo_exists"):
        narrator "You put the photograph on the desk, face down, and then turn it face up again, and then leave it."
        $ s32_record_discovery("found_the_photograph")

        if s32_check("rel iris.trust >= 15"):
            narrator "Iris said the unlabelled ones are the interesting ones. She said it the way people say things they have said before."

    else:
        narrator "Two boxes catalogued. Four hundred to go, at a guess nobody has asked you to make."

    narrator "Tomorrow there will be more boxes."

    # A prototype should end by saying so, not by pretending to be a demo.
    narrator "{i}— end of the prototype slice —{/i}"

    narrator "{size=-6}This build exists to test the storylet engine. The scenes above are not final, and September 32 has not happened yet.{/size}"

    return
