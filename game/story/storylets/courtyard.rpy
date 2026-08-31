# PROTOTYPE / NON-FINAL
#
# The courtyard. Scene cards: docs/narrative-design/scene-cards/MILESTONE_2.md
#
# The busiest cell in the simulation. Before Milestone 2 it was served by one
# ambient scene which accounted for 42% of everything played in the game, so
# these three exist to give the courtyard a second, third and fourth thing that
# can happen in it.
#
# `courtyard_lunch_table` is one of the milestone's three group scenes. Both
# NPCs have an opinion about each other and the player is not required to hold
# one, which is why the third branch has to be as substantial as the first two.
#
# Effects are declared in data/storylets/courtyard_*.json and iris_outside.json.

label s32_st_courtyard_morning_queue:

    scene bg courtyard day with dissolve

    $ _v = s32_rng().randint(1, 2)

    if _v == 1:

        narrator "The hatch by the science block sells tea, a flapjack, and a second thing that changes weekly and is currently a cheese roll."

        narrator "There are eleven people in the queue and the hatch opens at half past, and everybody knows this, and everybody is here at twenty past."

        narrator "By the time you get there the flapjacks have gone. This appears to be a structural feature rather than an accident."

    else:

        narrator "You are not allowed to walk across the middle of the courtyard. You are allowed to walk around all four sides of it."

        narrator "Nobody can tell you why. The prevailing theory involves a headmaster who left in the nineties and a lawn that was, at the time, new."

        narrator "The lawn is not new. Everybody still walks around."

    return


label s32_st_courtyard_lunch_table:

    scene bg courtyard day with dissolve

    narrator "June has one of the two tables that get shade, and she has it in the way you have something you arrived early for."

    show june school_summer neutral at s32_left with dissolve

    c_june "Sit down, I'm defending this against a year nine."

    narrator "You are eleven minutes into a conversation about nothing when Noah arrives with a folder of printouts held together by an arrangement he clearly regrets."

    show noah school_summer neutral at s32_right with dissolve

    c_noah "The laptop's booked till two. I'm doing the layout on paper like it's nineteen ninety."

    c_june "You could have booked the laptop."

    c_noah "I did book the laptop. Somebody else also booked the laptop."

    show june school_summer talk

    c_june "So you're doing it here."

    c_noah "I'm doing it here."

    narrator "There is a pause with something in it. They know each other well enough not to be polite and not well enough to say the actual thing."

    c_june "It's just — every lunchtime, Noah. It's a school paper. Nobody reads it."

    show noah school_summer concerned

    c_noah "Four hundred people live here and about six of them write anything down. I'd rather be one of the six."

    c_june "That's a very nice sentence. Did you have it ready?"

    c_noah "Yes."

    narrator "He says it flatly and June laughs before she has decided whether to, which is the closest either of them gets to conceding anything."

    menu:

        "She's got a point. It is every lunchtime.":
            $ trait("gentle")
            $ rel("june->player", "trust", 3)
            $ rel("noah->june", "resentment", 2)
            $ rel("june->noah", "respect", 1)

            c_noah "Right."

            narrator "He does not argue. He squares the printouts against the table, twice, and starts working, and the conversation goes somewhere else without him in it."

            c_june "He'll be fine. He does this."

            narrator "She says it to you rather than to him, at a volume he can hear, and you are fairly sure that was the point."

        "Six people is not nothing.":
            $ trait("curious")
            $ rel("noah->player", "respect", 3)
            $ rel("june->noah", "resentment", 2)
            $ rel("noah->june", "suspicion", 1)

            c_noah "Thank you."

            c_june "Oh, brilliant."

            narrator "June says it lightly, and then does not say anything else for a while, which from June is the whole of the message."

            c_noah "The third column's short. It's always the third column."

            narrator "He works. She eats. Nobody says anything else about it for the rest of lunch."

        "I'm not refereeing this.":
            $ trait("reserved")
            $ rel("june->player", "respect", 2)
            $ rel("noah->player", "respect", 2)
            $ rel("june->noah", "familiarity", 2)

            c_june "Wise."

            c_noah "Wise."

            narrator "They say it at the same time and both look mildly annoyed about that."

            narrator "For the next twenty minutes they talk to each other instead of at you, about a teacher and about whether the annexe has a working socket, and you are not needed for any of it."

            narrator "That is a better lunchtime than the one that was heading your way."

    hide june with dissolve
    hide noah with dissolve

    return


label s32_st_iris_outside:

    scene bg courtyard day with dissolve

    narrator "Iris is in the courtyard, which is wrong the way a chair on a lawn is wrong. Nothing is the matter with it. It simply is not where the thing goes."

    show iris school_summer neutral at s32_centre with dissolve

    narrator "She is eating lunch at ten past eleven, on the low wall, with the box balanced on her knees."

    c_iris "It's quiet in there between eleven and twelve. If I eat now I don't have to eat later, and later is when people come in."

    c_me "So you eat lunch at eleven so you can be alone at one."

    c_iris "Yes."

    narrator "She says it as though you have correctly read out a timetable."

    menu:

        "Sit down.":
            $ trait("gentle")
            $ rel("iris->player", "trust", 3)
            $ rel("iris->player", "attraction", 3)

            narrator "You sit on the wall. The wall is cold in the way stone is cold in September, which is not unpleasant for about four minutes."

            narrator "She does not fill the silence and neither do you, and it turns out to be fine."

            c_iris "You can sit here again, if you want. I'm here most days at this time."

            narrator "She looks at the box rather than at you while she says it, and then closes it, and that is the end of that."

        "Doesn't that get lonely?":
            $ trait("curious")
            $ rel("iris->player", "respect", 3)

            c_iris "That's the wrong question by about one step."

            c_iris "It's the same amount of alone either way. This way I choose when."

            narrator "There is no self-pity in it at all."

            c_iris "Ask me in November. In November the wall's no good and I have to eat in the room and then it is a bit much."

        "Leave her to her eleven o'clock.":
            $ trait("reserved")

            narrator "You lift a hand and keep walking, and she lifts hers, and the whole exchange takes under two seconds and costs nobody anything."

            narrator "It occurs to you afterwards that she chose a wall in the middle of the courtyard rather than anywhere actually private, and that people who want to be entirely alone do not generally do that."

    hide iris with dissolve

    return
