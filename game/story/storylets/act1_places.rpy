# PROTOTYPE / NON-FINAL — Act 1 draft
#
# The five world scenes. Every one of them exists because the simulator counted
# thousands of visits to a place at an hour with nothing authored in it:
# the dorm before the bell, the corridor after the last lesson, the gate on the
# way out, and the common room, which did not exist until this milestone.
#
# Nothing here advances anything. That is the job.
# docs/narrative-design/ACT_1.md, docs/narrative-design/CELL_MAP.md

label s32_st_dorm_early_start:

    scene bg dorm_room day with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "The radiator comes on at twenty to seven and makes a sound like somebody moving furniture two floors down."

        narrator "You are awake before it and you lie there anyway, because being awake and being up are separated by an amount of willpower nobody has at that hour."

        narrator "The window is cold. Outside, one person is already crossing the courtyard, at a pace that says they have somewhere to be and have had somewhere to be for years."

    elif _v == 2:

        narrator "You have four shirts and two of them are in a bag you have been meaning to take to the launderette in town."

        narrator "This is the morning you find out which two."

        narrator "The third one is fine. It is not the one you wanted, and it is fine, and you put it on."

    else:

        narrator "Somebody's alarm has been going in a room down the corridor for eleven minutes."

        narrator "It is not your alarm. There is a protocol for this and nobody has told you what it is, so you lie there participating in a collective decision not to do anything."

        narrator "At minute twelve it stops. Nobody ever mentions it. This will happen again on Thursday."

    return


label s32_st_hallway_afternoon_drift:

    scene bg hallway_east day with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "The last lesson lets out and the corridor becomes, for about four minutes, the most populated place in the county."

        narrator "Then it empties from both ends at once and you are standing in it, which is a thing that happens if you do not have a plan."

        narrator "There is a radiator here that works, unlike the one in the archive, and standing near it is a legitimate use of an afternoon."

    elif _v == 2:

        narrator "A window is open at the far end because it is always open at the far end, and there is a note taped under it that says {i}please leave open{/i} with no signature."

        narrator "Underneath, in a different hand: {i}why{/i}"

        narrator "Underneath that, in the first hand again: {i}damp{/i}"

    else:

        narrator "Two people ahead of you are having an argument about a film, conducted entirely in the form of asking each other what they thought the ending meant."

        narrator "Neither of them will say what they thought it meant. This continues for the whole length of the corridor and is unresolved at the stairs."

    return


label s32_st_common_room_evening:

    scene bg common_room evening with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "The common room at nine has three people in it and a lamp that only works if the switch is held at an angle."

        narrator "Somebody has left a mug. The mug has been there long enough to have become a topic and then stopped being one."

        narrator "You do the reading you were going to do in your room, here, badly, and it is better than doing it well upstairs."

    elif _v == 2:

        narrator "The television gets four channels and the aerial is a coat hanger, which everybody knows and nobody has fixed because fixing it would end the joke."

        narrator "Tonight it is a programme about canals. Nobody chose it. Four people are watching it."

        narrator "By the second lock you are watching it too."

    else:

        narrator "Empty, which happens on the nights something is on somewhere else."

        narrator "The kettle is warm, so somebody was here recently and has gone. The cushions on the good sofa are arranged the way they get arranged when a person has been lying on them and has straightened up afterwards out of guilt."

        narrator "You sit on the other one. It is worse. That is presumably the whole reason the good one is the good one."

    return


label s32_st_common_room_kettle:

    scene bg common_room day with dissolve

    $ _v = s32_rng().randint(1, 2)

    if _v == 1:

        narrator "There is a laminated sign above the kettle that says {i}THIS IS NOT A KITCHEN{/i} in a font that suggests real feeling."

        narrator "Under it there is a kettle, four mugs, a jar of coffee, a jar of something that used to be coffee, and a toaster somebody has brought from home and which is therefore the toaster of a specific person nobody can name."

        narrator "The sign is correct and has lost."

    else:

        narrator "Daylight makes it a different room. In the evening it is somewhere to be; at half eleven on a free morning it is furniture in a rectangle."

        narrator "You can hear a lesson through the wall. Not the words — the shape: a question, a pause, three or four people answering at once, a longer pause."

        narrator "It is the most restful sound in the building and you will not tell anybody that."

    return


label s32_st_gate_going_out:

    scene bg school_gate evening with dissolve

    narrator "There is a sign-out book on a shelf inside the gate, in a plastic sleeve, with a biro on a string."

    narrator "Name, time out, destination, time back. Nobody checks it. Everybody fills it in."

    narrator "The destinations column is the interesting one. Four people this week have written {i}town{/i}. Two have written {i}out{/i}. One has written {i}the shop, then back{/i}, which is either very honest or a small joke depending on the person."

    menu:

        "Fill it in properly.":
            $ trait("direct")

            narrator "Name, time, {i}town{/i}, and you leave the return column blank the way you are supposed to."

            narrator "It takes eleven seconds and it means that if you fall in a ditch somebody knows roughly which ditch. The system is not sophisticated and it is not nothing."

        "Copy whatever the person above wrote.":
            $ trait("sarcastic")

            narrator "The person above wrote {i}out{/i}. You write {i}out{/i}."

            narrator "The column now reads {i}out{/i} eleven times in the same afternoon, which will look, to anyone reading it in forty years, like something happened."

        "Don't sign out.":
            $ trait("reserved")

            narrator "You walk through the gate and nobody stops you, because nobody was ever going to."

            narrator "Halfway down the road it occurs to you that the book is not a rule, it is a courtesy, and that you have just been discourteous to a shelf."

    return


label s32_st_dorm_bathroom_queue:

    scene bg dorm_room day with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "There are four showers for eleven people and an unwritten agreement that the one on the end is broken."

        narrator "It is not broken. It runs cold for ninety seconds and then it is the best of the four, and about three people know this, and none of them has said."

        narrator "You are now one of the three."

    elif _v == 2:

        narrator "Somebody has been in there for nineteen minutes and there is a queue of two, and the queue is being conducted entirely by standing in the corridor looking at phones."

        narrator "Nobody knocks. Knocking would make it a thing. The nineteen minutes are being endured as a group and will be discussed later by everyone except the person responsible."

    else:

        narrator "You are first, which happens perhaps twice a term, and the whole floor is yours and the water is hot from the start."

        narrator "It is a fifteen-minute head start on the day and you spend eleven of the minutes standing still doing nothing, which is what the fifteen minutes were for."

    return
