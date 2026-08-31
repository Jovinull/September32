# PROTOTYPE / NON-FINAL
#
# The school gate. Scene cards: docs/narrative-design/scene-cards/MILESTONE_2.md
#
# This location had no content at any hour before Milestone 2, in a game about
# a school. Three scenes here, deliberately overlapping in the morning, because
# the milestone is about the director having something to choose between.
#
# Nothing here foreshadows anything. The gate is a gate.
#
# Effects are declared in data/storylets/gate_*.json.

label s32_st_gate_early_arrival:

    scene bg school_gate day with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "The gate is chained. Not locked in an interesting way — chained, with a padlock the size of a fist, the way you would secure a bicycle you did not like very much."

        narrator "Four people are waiting. Nobody is talking. It is the particular silence of people who are not friends but who recognise each other by now, and who have agreed without discussing it that this is not a conversation."

        narrator "At two minutes past, a small van pulls up and a man gets out with a set of keys on a retractable line, and everybody stops looking at their phones at the same moment."

        $ learn("caretaker_opens_at_seven", source="waiting_at_the_gate")

        narrator "Seven o'clock, apparently. Seven, and not a minute of it earlier, and you get the sense that this has been tested."

    elif _v == 2:

        narrator "You are early enough that the gate is open and nobody is through it yet, which is a different thing from being first."

        narrator "The path has been swept. Somebody swept it, at an hour when nobody was here to see it swept, and will do it again tomorrow."

    else:

        narrator "Somebody has left a bike against the railing without locking it, which either means they trust the town or they have given up on the bike."

        narrator "Two girls from the year below go past at a speed that suggests they are late for something that started yesterday."

    return


label s32_st_gate_noticeboard:

    scene bg school_gate day with dissolve

    narrator "The glass case by the gate is the school's only public surface and it has three things in it."

    narrator "A lost property list, typed, with items described in the flat language of somebody who has never seen them: {i}one scarf, dark{/i}. {i}One key, brass, no fob{/i}."

    narrator "A sign-up sheet for a walking club with two names on it, both from last year."

    narrator "And a laminated notice that has been there long enough for the laminate to have gone yellow along the top edge."

    menu:

        "Read the laminated one properly.":
            $ trait("curious")
            $ learn("bound_volumes_were_moved", source="the_noticeboard")

            narrator "It is a storage notice. The bound volumes of the school paper, the parish magazine and something called the Governors' Minutes were moved into the annexe during the library reorganisation, and enquiries go to the office."

            narrator "There is a date on it. It is not recent, and the notice has plainly outlived whoever was supposed to take it down."

            narrator "So that is where they went. Somebody wrote it on a card and put the card in a glass case and considered the matter closed, which is roughly how most things get decided here."

        "Take the lost property notice down. It is three weeks old.":
            $ trait("gentle")

            narrator "The case is not locked. You take the sheet out, fold it, and put it in your bag to bin properly later."

            narrator "Underneath it there is an older one, and underneath that, one older still. Nobody has ever taken one down. You put the two old ones in your bag as well."

        "Walk on.":
            $ trait("direct")

            narrator "It is a noticeboard. You have read one."

    return


label s32_st_gate_waiting:

    scene bg school_gate day with dissolve

    narrator "Theo is at the gate, not going through it."

    show theo school_summer neutral at s32_centre with dissolve

    narrator "He has his bag open on the wall and he is going through it in the way you go through a bag you have already been through — slower, and with less hope."

    c_theo "It's fine."

    c_me "I didn't say anything."

    c_theo "You were going to."

    menu:

        "Give me half the bag.":
            $ trait("gentle")
            $ rel("theo", "familiarity", 4)
            $ rel("theo", "trust", 2)

            narrator "He hands you the side pocket without arguing, which is the fastest he has agreed to anything."

            narrator "You find a ruler, a bus ticket from the wrong month, and a sandwich that has been in there long enough to be an artefact. He finds nothing."

            c_theo "It's brass. It's about that long. No fob, which is the whole problem."

            c_me "A key."

            c_theo "A key."

            narrator "He zips the bag and puts it on his shoulder and does not move."

            c_theo "It'll be somewhere. Things are always somewhere."

        "What is it?":
            $ trait("direct")
            $ rel("theo", "respect", 3)

            c_theo "Something I'm supposed to have."

            c_me "That's not an answer."

            c_theo "No."

            narrator "He says it without heat, as an accurate observation about his own reply, and goes back to the bag."

            c_theo "If I say it out loud I have to have lost it. At the minute I've only misplaced it."

            narrator "That is either a joke or it is not, and he does not give you enough to decide."

        "Leave him to it.":
            $ trait("reserved")

            narrator "You say something ordinary and go through the gate."

            narrator "When you look back from the corner he is still there with the bag open, doing it again from the start, in the same order."

    hide theo with dissolve

    return
