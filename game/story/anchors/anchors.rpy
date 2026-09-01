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
            $ rel("mara->player", "familiarity", 4)
            c_mara "Everyone knows. It's been on the noticeboard since June."
            c_mara "Nobody wanted it. Sorry."
            narrator "She does not sound sorry. She sounds like someone being accurate."

        "Thanks. Lead on.":
            $ trait("reserved")
            $ rel("mara->player", "familiarity", 3)
            $ rel("mara->player", "respect", 2)
            c_mara "Right."
            narrator "She walks. You follow. It is a long enough silence to be comfortable, which is not what you expected."

        "Does everyone get met at the gate?":
            $ trait("direct")
            $ rel("mara->player", "familiarity", 2)
            $ rel("mara->player", "suspicion", 3)
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
            $ rel("iris->player", "trust", 4)
            $ rel("iris->player", "familiarity", 3)
            c_iris "Then it goes in the maybe pile and I photograph it anyway."
            c_iris "Most of the maybe pile is somebody's aunt at a sports day in 1974."
            narrator "She says {i}most{/i} the way you would set something down carefully."

        "Seems straightforward.":
            $ trait("reserved")
            $ rel("iris->player", "familiarity", 3)
            c_iris "It is. That's why nobody does it."

        "How long have you been doing this alone?":
            $ trait("empathetic")
            $ rel("iris->player", "trust", 5)
            $ rel("iris->player", "attraction", 2)
            c_iris "..."
            c_iris "Since March."
            narrator "She goes back to the scanner, which is her way of finishing a sentence."

    hide iris with dissolve

    $ s32_finish_anchor("first_shift")

    return


label s32_anchor_the_date:
    # End of Act 1, CONTRADICTION. The second record. It does NOT advance the
    # phase: `unsettling` is the second and third thing and belongs to Act 2, so
    # the week ends inside `odd`, holding two documents and no account that
    # covers both.
    #
    # Nobody reads the number out loud. What it is stays open --
    # docs/canon/SEPTEMBER_32.md is still IDEA about almost everything, and a
    # character saying "thirty-two" here would be the scene deciding canon.
    #
    # Branches on whether the player found box seventeen themselves, since
    # old_photo_glimpse reaches 98% of runs and an anchor cannot depend on that.

    $ go("archive_room")

    scene bg archive_room evening with fade

    if has_item("old_photo"):

        narrator "You have had it for days. It has been face-down on the desk under a box lid, which is not filing, and you know it is not filing."

    else:

        narrator "Box seventeen, loose, at the bottom, under a bundle of sports-day programmes."

        narrator "Forty-odd faces in three rows, the back row standing on a bench. The mount is trimmed along one edge and not squarely, as though somebody did it by hand and in a hurry."

        $ take("old_photo")
        $ learn("old_photo_exists", source="the_box_you_went_back_to")

    narrator "You turn it over for the reverse, because the reverse is where a school writes the year and the form and the names, and this one has none of those."

    narrator "It has a stamp."

    $ s32_browse_document("photograph_card_unlisted")

    narrator "The stamp is a date, and it is the month you are currently standing in, and the number after the month is not a number that month has."

    narrator "You read it twice, which is once more than a date needs."

    narrator "It is not smudged. It is not two numbers overlapping. It is the sort of stamp that gets rolled onto a page by somebody who does it four hundred times a week and it has been rolled cleanly."

    menu:

        "A stamp can be set wrong.":
            $ trait("skeptical")

            narrator "It can. You have seen a franking machine in the office and it has little wheels on it and the wheels turn."

            narrator "Somebody set the wheel one click too far, stamped a photograph, and went to lunch. That is a Tuesday, not a mystery."

            narrator "You are aware, holding it, that this explanation covers the stamp and does not cover the column, and that you now have two things instead of one."

        "Somebody filled a register on a day like this.":
            $ trait("curious")

            narrator "Fourteen names, ruled top and bottom, in the same hand as the columns either side of it. A day that got a register and did not get a number."

            narrator "And a photograph with a number the month does not have."

            narrator "Neither of those is anything on its own. You cannot make them be nothing together, and you try, standing there, for about a minute."

        "Put it back where it was.":
            $ trait("reserved")

            narrator "You put it back under the programmes, face-down, in the position it came out of."

            narrator "It does not help. Knowing where a thing is turns out to be a different problem from knowing what it is, and you have solved the wrong one."

    narrator "The archive at this hour makes the noise a room makes when the heating has gone off and the building is still deciding about it."

    # The knowledge grants are declared in data/anchors/the_date.json and applied
    # by s32_finish_anchor. Duplicating them here would put the change somewhere
    # the reachability tooling cannot see it.
    $ s32_finish_anchor("the_date")

    return


label s32_anchor_the_common_room:
    # Day 3, CONNECTION. Deliberately contains no mystery, no archive and no
    # information the player needs. It is here because a player who has spent
    # three days between the gate and the archive has met four people one at a
    # time and has no idea what they are like with each other, and the rest of
    # Act 1 assumes they do. docs/narrative-design/ACT_1.md
    #
    # Outcomes are declared in data/anchors/the_common_room.json.

    $ go("common_room")

    scene bg common_room evening with dissolve

    narrator "The common room has two sofas, one of which everybody sits on."

    show june school_summer talk at s32_quad_b with dissolve
    show noah school_summer neutral at s32_quad_c with dissolve

    narrator "June is halfway through a story you have arrived too late for and is not going to recap."

    c_june "— and he still had the tray. That's the part. He had walked the entire length of the corridor and he still had the tray."

    c_noah "Was it his tray?"

    c_june "It was nobody's tray, Noah. That's why it's funny."

    show theo school_summer neutral at s32_quad_d with dissolve

    narrator "Theo is at the table by the window doing something to a spreadsheet on a laptop that makes a noise when it thinks."

    c_theo "It's a bit funny."

    c_june "Thank you, Theo."

    c_theo "I said a bit."

    narrator "Somewhere behind you a kettle finishes and nobody claims it."

    show mara school_summer neutral at s32_quad_a with dissolve

    c_mara "That's mine."

    narrator "Mara collects it, makes three cups without asking anyone anything, and hands two of them out correctly."

    c_noah "How do you know how everyone takes it."

    c_mara "I've been here since I was eleven."

    c_june "That is not an answer, that is a length of time."

    narrator "You realise, sitting on the arm of the sofa nobody sits on, that this has been happening every evening since before you arrived, and will happen on the evenings you are not here."

    menu:

        "Say something into the gap.":
            $ trait("gentle")
            $ rel("june->player", "familiarity", 3)
            $ rel("noah->player", "familiarity", 3)

            narrator "You say the obvious thing about the tray and it lands about as well as the obvious thing usually does, which is to say adequately."

            c_june "See, he gets it."

            c_noah "He does not get it. He's being polite."

            c_june "Being polite is getting it. That's the whole of manners."

            narrator "The conversation moves on without needing you again, and it turns out that is fine. Being included is mostly a question of being present when a thing is happening."

        "Ask Theo what the spreadsheet is.":
            $ trait("curious")
            $ rel("theo->player", "respect", 3)
            $ rel("june->player", "familiarity", 2)

            c_theo "Box inventory."

            c_me "For the archive?"

            c_theo "For me. The archive has one. Mine has a column for whether I've actually seen the box or whether I'm taking somebody's word for it."

            c_june "He's been doing that for a year."

            c_theo "Fourteen months."

            c_june "He's been doing that for fourteen months."

            narrator "It is said with the specific fondness of somebody explaining a friend to a newcomer while the friend is in the room. Theo does not appear to mind, and may not have noticed."

        "Stay where you are.":
            $ trait("reserved")
            $ rel("mara->player", "respect", 3)
            $ rel("theo->player", "familiarity", 2)

            narrator "You drink the tea you did not ask for and say nothing for twenty minutes."

            narrator "June tells two more stories. Noah tries out a sentence about the paper and does not get to finish it. The laptop makes its noise."

            c_mara "You're not much of a talker."

            c_me "I'm new."

            c_mara "That wears off."

            narrator "She takes the cups back without being asked. It is the second time this evening she has done something nobody thanked her for, and you notice, and you do not say so."

    hide june with dissolve
    hide noah with dissolve
    hide theo with dissolve
    hide mara with dissolve

    $ s32_finish_anchor("the_common_room")

    return


label s32_anchor_the_undated_column:
    # Day 4, INCONSISTENCY. The phase turns here, and this is the smallest thing
    # it could turn on: a column with entries and no date written above it. The
    # ordinary explanation is offered inside the scene, by a character, and it is
    # probably correct. Nothing here may imply otherwise.
    #
    # Branches on whether Theo already showed the player the page, because
    # theo_ledger_question reaches about five runs in six and an anchor cannot
    # depend on that. docs/narrative-design/CONTINUITY_REVIEW.md

    $ go("archive_room")

    scene bg archive_room afternoon with dissolve

    if knows("attendance_sheet_anomaly"):

        narrator "You go back to it on your own, which is different from being shown it."

        narrator "Theo had the page flat on the desk with a ruler across it and you had looked where he was pointing, and looking where somebody is pointing is not the same as looking."

    else:

        narrator "Box eleven is attendance ledgers, which is the least promising sentence in the building."

        narrator "You are doing them because they are the only boxes with a spine, and a spine means an order, and an order means you can stop and start."

        narrator "Ledger III, page forty. You are three columns in before you notice."

    narrator "Every column on the page has a date above it in the same hand: a number, the month abbreviated, ruled underneath."

    narrator "One does not."

    # Granted inline because the document is gated on it and the director does
    # not apply an anchor's declared effects until the label returns. Same class
    # of problem as the Milestone 1 archive bug; the declared effect in
    # data/anchors/the_undated_column.json still runs afterwards, so the
    # tooling's view of where the change happens is unchanged.
    $ learn("attendance_sheet_anomaly", source="the_column_itself")

    $ s32_browse_document("ledger_iii_page_forty")

    narrator "The column itself is complete. Fourteen entries, all present marks, ruled top and bottom the way the others are ruled. Somebody filled it in properly and did not write what day it was."

    show iris school_summer neutral at s32_centre with dissolve

    c_iris "You've found the one with no header."

    c_me "You know about it."

    c_iris "Everyone who's done box eleven knows about it. It's been like that since before any of us."

    narrator "She says it the way you would describe a stuck window."

    menu:

        "So what happened?":
            $ trait("curious")
            $ rel("iris->player", "trust", 3)

            c_iris "Somebody was writing a register, got interrupted, and came back to it after the moment when you write the date."

            c_iris "It's the most boring answer and it's almost certainly the right one. That's usually how the boring answer works."

            c_me "Almost certainly."

            c_iris "..."

            c_iris "Almost."

            narrator "She goes back to the scanner and does not add anything, and the not-adding sits there a second longer than it needs to."

        "Has anyone worked out which day it was?":
            $ trait("skeptical")
            $ rel("iris->player", "respect", 3)
            $ npc_learns("iris", "attendance_sheet_anomaly", "known")

            c_iris "You'd do it from the columns either side. The one before is the fifteenth, the one after is the seventeenth."

            c_me "Then it's the sixteenth."

            c_iris "Then it's the sixteenth, and somebody wrote a register on it, and it doesn't have a number."

            narrator "She says this with no weight at all, in the tone of a person completing an arithmetic problem, and goes back to what she was doing."

        "Put it back.":
            $ trait("reserved")
            $ rel("iris->player", "familiarity", 3)

            narrator "You square the ledger, close it, and put it in the box in the position it came out of. Iris notices and does not comment."

            c_iris "Most people leave them open."

            c_me "It's a book."

            c_iris "It's a book."

            narrator "That is apparently the correct answer, and you get the impression it is the first correct answer anyone has given her about a book this term."

    hide iris with dissolve

    $ s32_finish_anchor("the_undated_column")

    return
