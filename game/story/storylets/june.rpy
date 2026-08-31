# PROTOTYPE / NON-FINAL
#
# June. Scene cards: docs/narrative-design/scene-cards/MILESTONE_1.md
# Voice: docs/characters/VOICES.md and docs/characters/june.md
#
# Fast, fluent, complete sentences. Answers the easy half of a question and asks
# you something. Jokes first, and the joke that arrives too fast is the tell.
#
# Effects are declared in data/storylets/june_*.json. Nothing that changes state
# lives only in this file.

label s32_st_june_the_favour:

    scene bg courtyard day with dissolve

    narrator "There is a bench in the courtyard that gets the sun until about two, and June has been in the middle of it since before you sat down at the other end."

    show june school_summer neutral at s32_centre with dissolve

    c_june "Okay, this is going to sound like I planned it, and I did, but only about forty seconds ago."

    c_me "Go on."

    c_june "Are you doing anything Thursday after fourth?"

    narrator "She asks it lightly. She has clearly already worked out what she will say if you are."

    c_june "There's a thing. It's not a big thing. Somebody has to put chairs out for the parents' evening and take the names at the door, and I have done it every single time since I got here, and I would rather —"

    show june school_summer talk

    c_june "— I would just rather not be the person who does that."

    narrator "This is the longest sentence she has produced and it arrived slightly out of order, which for June is close to a confession."

    menu:
        "Sure. I'll do it.":
            $ trait("gentle")
            $ rel("june->player", "familiarity", 4)
            $ promise("june_favour", "june", in_days=1, importance=45)

            c_june "Oh — great. Thanks."

            narrator "Two beats."

            c_june "That was easier than I'd budgeted for. I had a whole second half."

            c_me "I'd like to hear the second half."

            c_june "You would not. It involved flattery."

        "What is it, exactly?":
            $ trait("skeptical")
            $ rel("june->player", "respect", 3)
            $ promise("june_favour", "june", in_days=1, importance=45)

            c_june "Sixty chairs, a table, a clipboard, and roughly ninety minutes of saying good evening to people who are looking past you for their child."

            c_me "You've done this a lot."

            c_june "I've done this a lot."

            narrator "She hands you the clipboard as though the conversation had already concluded, which it apparently had."

        "Ask someone else. I'm not the one who says yes to things.":
            $ trait("direct")
            $ rel("june->player", "respect", 4)
            $ rel("june->player", "familiarity", 1)

            narrator "She looks at you properly for the first time."

            c_june "Fair. That's a fair answer, that's — yeah."

            c_june "I'm going to remember you said that, by the way. Not in a threatening way. In a useful way."

            narrator "She goes back to her sandwich. It does not appear to have cost either of you anything."

    hide june with dissolve

    return


label s32_st_june_welcome_pack:

    scene bg classroom_2b day with dissolve

    narrator "Fourth period ran short and nobody has told the corridor, so 2-B is eleven people waiting for a bell."

    show june school_summer neutral at s32_left with dissolve

    c_june "You got the booklet, right? When you started. Grey thing, staple in the corner, photograph of the gate on the front."

    c_me "It's in a drawer."

    c_june "That's where it goes."

    narrator "She is peeling the label off a bottle, in one piece, with the concentration of someone doing it as a project."

    c_june "There's a bit at the back. A History of Northfield, five pages, one paragraph per year since about the twenties. Very thrilling. New gymnasium. Roof repaired."

    c_june "And then it just — doesn't do one."

    show june school_summer talk

    c_june "One year it goes straight from one paragraph to the next one and the middle one isn't there."

    menu:
        "Which year?":
            $ trait("curious")
            $ learn("school_history_skips_a_year", source="junes_welcome_pack")
            $ npc_learns("june", "school_history_skips_a_year", "known")
            $ rel("june->player", "familiarity", 3)

            c_june "No idea."

            c_me "You noticed a missing paragraph and not which one?"

            c_june "I noticed it on a Sunday, in a corridor, waiting for someone to find me a key. I was fifteen. It's a booklet."

            narrator "The label comes off in one piece. She looks quite pleased about it."

        "Sounds like a misprint.":
            $ trait("skeptical")
            $ learn("school_history_skips_a_year", source="junes_welcome_pack")
            $ npc_learns("june", "school_history_skips_a_year", "known")
            $ rel("june->player", "respect", 2)

            c_june "That's what I thought. That's exactly what I thought."

            narrator "There is something in how quickly she agrees, and it is not concealment. It is relief at being agreed with."

            c_june "They print about forty of those a year on a machine older than the roof. Things fall off pages."

        "You were fifteen and you read the history section?":
            $ trait("gentle")
            $ rel("june->player", "familiarity", 4)
            $ rel("june->player", "attraction", 2)

            c_june "I read all of it. Twice. On the bus."

            narrator "She says this flatly, as a fact about a stranger."

            c_june "You do that, when you're the new one. You learn the place off the paperwork because there's nobody to ask yet."

            c_june "Anyway. It's a terrible booklet."

            narrator "The bell goes. She is already standing."

    hide june with dissolve

    return
