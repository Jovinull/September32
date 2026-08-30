# PROTOTYPE / NON-FINAL
#
# Anchor scenes. These are the beats that must happen, in order; the storylets
# fill the space between them. Metadata lives in data/anchors/*.json — this file
# holds only the writing.
#
# Anchors apply their own effects at the end rather than leaving it to the
# director, because an anchor is called directly and its post-conditions are
# part of what it means for the beat to have happened.

label s32_anchor_arrival:

    $ go("school_gate")

    scene bg school_gate day with dissolve

    narrator "The letter called it a residential academy. The gate calls it Northfield, in iron, with the F missing."

    show mara school_summer neutral at s32_centre with dissolve

    c_mara "You're the archive one."

    c_me "Am I?"

    c_mara "You're the only person arriving on a Sunday. Everyone else got here Friday."

    narrator "She says it without any particular judgement, the way you would read a timetable."

    c_mara "I'm Mara. I'll walk you up, the front door sticks."

    menu:
        "How do you know about the archive job?":
            $ trait("curious")
            $ rel("mara", "familiarity", 4)
            c_mara "Everyone knows. It's been on the noticeboard since June."
            c_mara "Nobody wanted it. Sorry."
            narrator "She does not sound sorry. She sounds like someone being accurate."

        "Thanks. Lead on.":
            $ trait("reserved")
            $ rel("mara", "familiarity", 3)
            $ rel("mara", "respect", 2)
            c_mara "Right."
            narrator "She walks. You follow. It is a long enough silence to be comfortable, which is not what you expected."

        "Does everyone get met at the gate?":
            $ trait("direct")
            $ rel("mara", "familiarity", 2)
            $ rel("mara", "suspicion", 3)
            c_mara "No."
            narrator "She holds the pause exactly long enough for you to notice it."
            c_mara "My family's been here a while. You get used to being the one who's around."

    hide mara with dissolve

    $ s32_finish_anchor("arrival")

    return


label s32_anchor_first_shift:

    $ go("archive_room")
    $ advance(1)

    scene bg archive_room day with fade

    narrator "The archive room was a club room until recently. There is still a kettle."

    show iris school_summer neutral at s32_centre with dissolve

    c_iris "You're late, which is fine, because I'm early, which is not a virtue."

    c_iris "Iris. I do the photographs."

    narrator "Boxes to the ceiling on two walls. On the third, a flatbed scanner that predates everyone in the room."

    c_iris "The job is: open a box, photograph what's in it, write down what it is, put it back."

    c_iris "The writing-down is the part people skip. Don't skip it."

    menu:
        "What happens if something isn't labelled?":
            $ trait("curious")
            $ rel("iris", "trust", 4)
            $ rel("iris", "familiarity", 3)
            c_iris "Then it goes in the maybe pile and I photograph it anyway."
            c_iris "Most of the maybe pile is somebody's aunt at a sports day in 1974."
            narrator "She says {i}most{/i} the way you would set something down carefully."

        "Seems straightforward.":
            $ trait("reserved")
            $ rel("iris", "familiarity", 3)
            c_iris "It is. That's why nobody does it."

        "How long have you been doing this alone?":
            $ trait("empathetic")
            $ rel("iris", "trust", 5)
            $ rel("iris", "attraction", 2)
            c_iris "..."
            c_iris "Since March."
            narrator "She goes back to the scanner, which is her way of finishing a sentence."

    hide iris with dissolve

    $ s32_finish_anchor("first_shift")

    return


label s32_anchor_the_date:
    # PROVISIONAL. Not reachable in the current slice — the phase advance here
    # is the first genuinely wrong thing, and the prototype stops before it.
    # Present so that the anchor chain is complete and the reachability tools
    # have something to check against.

    scene bg archive_room evening with fade

    narrator "You read the stamp twice, which is once more than a date needs."

    # The knowledge grant is declared in data/anchors/the_date.json and applied
    # by s32_finish_anchor. Duplicating it here would put the change somewhere
    # the reachability tooling cannot see it.
    $ s32_finish_anchor("the_date")

    return
