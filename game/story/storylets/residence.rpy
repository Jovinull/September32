# PROTOTYPE / NON-FINAL
#
# The dorm at night, and the road into town. Scene cards:
# docs/narrative-design/scene-cards/MILESTONE_2.md
#
# `dorm_late_night` is the milestone's answer to the Milestone 1 bug where a
# repeatable scene narrated a first-time discovery twice. Its variants are keyed
# to `seen_count`, not to the RNG, so the room stops being new in the order a
# room stops being new. See docs/narrative-design/CONTINUITY_REVIEW.md.
#
# Effects are declared in data/storylets/dorm_*.json and town_road_*.json.

label s32_st_dorm_late_night:

    scene bg dorm_room night with fade

    # Progressive, not random. How many times the player has been here IS the
    # content: the room is unfamiliar, then it is a room, then it is theirs.
    $ _n = times_seen("dorm_late_night")

    if _n == 0:

        narrator "The building has a sound it makes when everybody in it has stopped moving. It is not silence. It is a pipe somewhere and the road and one door on a spring."

        narrator "You know where the light switch is now without looking, which happened at some point in the last week without being decided."

        narrator "The desk is where it was when you arrived, because it is where the socket is."

    elif _n == 1:

        narrator "Late again, and not for any reason. The reading was done at nine."

        narrator "Somebody two doors down is watching something with the volume at the level people use when they believe they are being considerate."

        narrator "You get into bed at a time you would have described, three weeks ago, as unreasonable."

    else:

        narrator "You move the desk."

        narrator "It takes four minutes and it is worse by every practical measure — the socket is now behind the bed and the lamp cable does not reach without going under it."

        narrator "But it faces the window, and you did it, and the room is about eleven per cent yours now instead of nought."

    return


label s32_st_dorm_corridor_noise:

    scene bg dorm_room evening with dissolve

    $ _v = s32_rng().randint(1, 2)

    if _v == 1:

        narrator "Somebody is on the phone in the corridor because the corridor has the signal, and they are having the half of a conversation you can hear."

        narrator "It is about a bank, and then it is about a brother, and then it is about the bank again. They say {i}no, I know{/i} eleven times."

        narrator "When it ends they stand out there for a while before going back in."

    else:

        narrator "There is an argument about the kitchen rota happening at a volume that says both parties know they are being overheard and consider that useful."

        narrator "The rota has been on the door since the first week. Nobody has ever done Thursday."

        narrator "It resolves the way these resolve, which is that somebody makes tea and the subject is changed for four days."

    return


label s32_st_town_road_shops:

    scene bg town_road day with dissolve

    narrator "There are four shops in a row and one of them sells everything."

    narrator "It sells bread, batteries, a small amount of hardware, birthday cards for relationships nobody in the village has, and, on a shelf by itself, four kinds of jam."

    narrator "The other three sell one thing each and have opinions about the fourth that they express by being closed on different days."

    menu:

        "Buy something you do not need.":
            $ trait("gentle")

            narrator "You buy a bar of chocolate and the woman behind the counter asks whether you are up at the school, in the tone of somebody confirming a thing she worked out on your way in."

            narrator "You say yes. She says her nephew was, and that he hated it, and that he is fine now, and none of this is unfriendly."

        "Read the cards in the window.":
            $ trait("curious")
            $ learn("caretaker_opens_at_seven", source="a_card_in_the_window")

            narrator "Handwritten postcards in a grid, some of them years old. A caravan. Piano lessons. Two separate people offering to do gardening."

            narrator "One is a rota for the school in a hand that has given up halfway: gates at seven, hall at seven, boiler Mondays. It is pinned up here because this is where the caretaker actually reads things."

            narrator "It is the least secret document you have ever looked at twice."

        "Keep walking.":
            $ trait("reserved")

            narrator "You have no money and no reason. The road carries on and so do you."

    return


label s32_st_town_road_last_bus:

    scene bg town_road night_lit with fade

    narrator "You are further along the road than you meant to be, at an hour that arrived faster than the distance did."

    narrator "The last bus back up to the school is twenty past. It is eleven minutes past, and the stop is about nine minutes behind you."

    menu:

        "Run.":
            $ trait("direct")

            narrator "You run. It is undignified and it works, with ninety seconds in hand and no breath at all."

            narrator "There are two other people on it and neither of them looks up, and you are grateful for that."

        "Walk it. It is forty minutes.":
            $ trait("reserved")

            narrator "You let the bus go past without especially deciding to, and then it is decided."

            narrator "The road has no pavement for the middle third and no lights for any of it, and it is one of the better forty minutes you have had here."

            narrator "You get in late enough that the corridor is dark and the stairs are the loud ones."

            $ advance(1)

        "Phone June and ask if she is still up.":
            $ trait("gentle")
            $ rel("june->player", "familiarity", 2)

            c_document "yes. why are you outside"

            c_document "there is a bus. there is famously a bus"

            narrator "You make the bus. She is on the stairs when you come up, holding a mug, entirely for the purpose of establishing that she was right."

            c_document "told you about the bus"

    return
