# PROTOTYPE / NON-FINAL — Act 1 draft
#
# The three group scenes, and the two relationship callbacks.
#
# A group scene is worth writing only if the player's choice costs something on
# an edge they are not standing on. All three of these move an NPC-to-NPC axis,
# and in `annexe_two_of_them` the two axes move in opposite directions depending
# which side the player takes, which is the whole reason that scene exists.
#
# docs/narrative-design/ACT_1.md, docs/narrative-design/RELATIONSHIP_DIRECTION.md

label s32_st_common_room_three_way:

    scene bg common_room evening with dissolve

    show june school_summer talk at s32_quad_b with dissolve
    show mara school_summer neutral at s32_quad_c with dissolve
    show theo school_summer neutral at s32_quad_d with dissolve

    narrator "The kitchen rota is on the table and has been annotated by three people in three colours."

    c_june "It isn't a rota if nobody does Thursday. It's a work of fiction."

    c_mara "I do Thursday."

    c_june "You do Thursday because nobody does Thursday. That's not the rota working, that's —"

    show mara school_summer neutral_blush

    c_mara "It gets done."

    c_june "— that's you working."

    narrator "They arrive at the ends of their sentences about a second apart and neither of them acknowledges the collision."

    c_theo "It gets done by one person out of seven, which is a failure of the rota that presents as a success of the kitchen."

    narrator "He says this to the rota rather than to anybody, in the manner of somebody logging a defect."

    c_june "Thank you, Theo."

    c_theo "I'm agreeing with you."

    c_june "I know. It's unsettling."

    narrator "This has happened before, in some form, more than once. What is new is that Mara has stopped saying anything, and June has not noticed, and Theo has — and Theo, having noticed, has gone back to the laptop, because noticing is where his repertoire ends."

    show june school_summer neutral

    c_june "Fine. New rota. Names in a hat."

    c_mara "It'll be the same by November."

    c_june "Then we'll do it again in November."

    narrator "Mara does not answer that. She reads the annotations, all three colours, top to bottom, which takes about as long as an answer would have."

    menu:

        "June's right. It's not a rota if it doesn't work.":
            $ trait("direct")
            $ rel("june->player", "trust", 3)
            $ rel("mara->june", "resentment", 3)
            $ rel("theo->june", "respect", 2)

            c_june "See."

            narrator "Mara does not disagree. She also does not stay, and the leaving is done well enough that only two of you register it as leaving."

            c_theo "That went badly."

            c_june "That went fine."

            c_theo "..."

            narrator "He does not say it again. He does, you notice, write something on the rota, in a fourth colour, and what he writes is {i}Thurs — M{/i}, in the column for the week after next."

        "She's been doing Thursday for four years. Say thank you.":
            $ trait("gentle")
            $ rel("mara->player", "trust", 4)
            $ rel("june->mara", "familiarity", 2)
            $ rel("theo->mara", "respect", 3)

            narrator "There is a pause of the kind that only happens when everyone in a room realises the same thing at the same time and would each rather somebody else had said it."

            c_june "God. Yes. Sorry, Mara."

            c_mara "It's a kitchen."

            c_june "It's four years of a kitchen."

            c_mara "It's a kitchen."

            narrator "She says it the second time in a completely different tone and takes the rota with her when she goes, which is either the end of the argument or the end of the rota."

        "Stay out of it.":
            $ trait("reserved")
            $ rel("theo->player", "respect", 3)
            $ rel("june->player", "respect", 2)
            $ rel("mara->player", "respect", 2)

            narrator "You do not adjudicate the rota. Names go in a hat. The hat is a mug."

            narrator "Mara draws Thursday. Nobody comments on the odds of that and everybody has now thought about them."

            c_theo "I'll swap with you."

            c_mara "You've got Tuesday."

            c_theo "I'll do both."

            narrator "It is not generosity in any register Theo would recognise. It is a correction to a system that produced a wrong result, and Mara takes it as generosity anyway, and both of them are right."

    hide june with dissolve
    hide mara with dissolve
    hide theo with dissolve

    return


label s32_st_annexe_two_of_them:

    scene bg hallway_east day with dissolve

    show iris school_summer concerned at s32_left with dissolve
    show noah school_summer talk at s32_right with dissolve

    narrator "You come round the corner into the middle of it, which is the only way anybody ever arrives at this conversation."

    c_noah "It's four hundred words. It's not an exposé, it's a piece about a school having an archive."

    c_iris "It's a piece about a school having an archive, with a photograph of the archive, and a list of what's in it."

    c_noah "That's what an archive is."

    c_iris "That's what a catalogue is. Nobody has read the catalogue in eleven years and I would like to keep it that way for about another six months."

    narrator "Noah does the thing where he gets more reasonable as he gets more sure. It is genuinely persuasive."

    c_noah "Why six months?"

    c_iris "..."

    c_iris "Because it isn't finished."

    show noah school_summer neutral

    c_noah "Iris, nobody's going to check your cataloguing."

    c_iris "Then why print it."

    narrator "That lands, and he does not have an answer to it that he wants to say out loud in a corridor."

    menu:

        "She's asked you not to. That should be enough.":
            $ trait("gentle")
            $ rel("iris->player", "trust", 5)
            $ rel("noah->player", "resentment", 4)
            $ rel("noah->iris", "resentment", 3)

            c_noah "Right."

            narrator "He says it in the tone of somebody filing a thing rather than dropping it."

            c_noah "It's the school's archive, though. Not hers."

            c_iris "It's the school's archive and I'm the only one in it."

            narrator "Noah leaves first. He does not usually leave first. Iris stands there for a second afterwards looking like somebody who has won something they did not want."

        "It's a school. Things get written about.":
            $ trait("direct")
            $ rel("noah->player", "trust", 5)
            $ rel("iris->player", "suspicion", 4)
            $ rel("iris->noah", "suspicion", 3)

            c_noah "Thank you."

            c_iris "..."

            narrator "Iris does not argue with you. That is worse than being argued with and takes a moment to identify."

            c_iris "You're right. It's not mine."

            c_iris "I'll get the catalogue printed off for you, Noah. It'll take an afternoon."

            narrator "She goes back toward the archive at a normal walking pace, and something you did not know you had has been withdrawn, quietly, without any announcement at all."

        "You're both talking about different things.":
            $ trait("reserved")
            $ rel("iris->player", "respect", 3)
            $ rel("noah->player", "respect", 3)
            $ rel("iris->noah", "familiarity", 2)

            c_me "You want to write about a school with an archive. She's worried about a list of objects being findable."

            c_noah "..."

            c_noah "I don't need the list."

            c_iris "You don't need the list?"

            c_noah "I need a photograph of a room with boxes in it and somebody saying it's four hundred boxes. The list is just the bit I had."

            narrator "They negotiate for about ninety seconds, competently, and arrive at something neither of them is thrilled with, and Iris says {i}fine{/i} in the voice of a person who has been listened to."

            narrator "You have not made either of them like you more. They are both, marginally, easier with each other."

    hide iris with dissolve
    hide noah with dissolve

    return


label s32_st_courtyard_the_bench:

    scene bg courtyard day with dissolve

    show mara school_summer neutral at s32_left with dissolve
    show noah school_summer talk at s32_right with dissolve

    narrator "The low wall gets the sun until about two. Mara is on it. Noah has arrived at it with a notebook, which is Noah arriving."

    c_noah "I'm doing a thing on the town. Two hundred years of it, four hundred words."

    c_mara "That's fifty years a hundred words."

    c_noah "That's a good line, can I have it."

    c_mara "No."

    narrator "He writes it down anyway. She watches him write it down and does not stop him, and neither of them will call that permission."

    show noah school_summer neutral

    c_noah "What should be in it?"

    c_mara "Nothing. It's a village with a school in it."

    c_noah "Everywhere's something."

    c_mara "Everywhere's not, though. That's the bit people from outside can't do. They get here and they need it to be interesting, and then they write four hundred words about a war memorial."

    c_noah "There's a war memorial."

    c_mara "There's a war memorial, and it's got eleven names on it, and four of them are the same family, and if you put that in it'll be the whole piece."

    c_noah "Why shouldn't it be the whole piece?"

    c_mara "Because they're still here. There's two of them in the year below."

    narrator "Noah stops writing. It is the first time you have seen him stop writing."

    menu:

        "He's allowed to write about it.":
            $ trait("direct")
            $ rel("noah->player", "respect", 4)
            $ rel("mara->noah", "resentment", 3)

            c_noah "Thank you."

            c_mara "He's allowed. Everyone's allowed."

            narrator "She gets off the wall."

            c_mara "That's why nobody here tells anyone anything. Not because it's secret. Because being allowed is all anybody needs and they've all got it."

            narrator "It is the most she has said at once, and it is said to you rather than to Noah, and you get the distinct sense that this is not the first time she has run this argument and it may be the first time she has lost it."

        "Ask them first.":
            $ trait("gentle")
            $ rel("mara->player", "trust", 4)
            $ rel("noah->mara", "respect", 3)

            c_noah "Ask the — the family?"

            c_mara "Yes."

            c_noah "That's — yes. Obviously. Why is that obvious now and it wasn't four minutes ago."

            c_mara "Because four minutes ago they were a memorial."

            narrator "He writes that one down too, and this time asks first, and she says yes, and something in the arrangement between the two of them has changed for the better by an amount neither will mention."

        "What would you put in it?":
            $ trait("curious")
            $ rel("mara->player", "respect", 3)
            $ rel("noah->player", "familiarity", 3)
            $ learn("school_history_skips_a_year", source="noah_had_heard_it_too")

            c_mara "The bus."

            c_noah "The bus?"

            c_mara "Two hundred years and the thing that changed it was the bus. Before the bus you married someone from here."

            narrator "Noah, to his credit, writes this down faster than he wrote down the good line."

            c_noah "Is that the thing about the year that's missing? Somebody told me the school skipped a year and nobody can say which."

            c_mara "That's a story. My aunt tells it to be entertaining."

            c_noah "That's not a no."

            c_mara "It's not a no."

            narrator "She says it in the flat voice, and it is not a warning, and it is not an invitation either. It is a person declining to be interesting on request."

    hide mara with dissolve
    hide noah with dissolve

    return


label s32_st_iris_the_second_box:
    # Multidimensional relationship reading. Reaching this scene at all needs
    # `iris->player.trust >= 14`, so she is not distant -- but trust and
    # suspicion are independent axes and the content can produce both at once:
    # telling Noah about the photograph costs trust and `annexe_two_of_them`
    # adds suspicion, so "she trusts you and is watching you" is a real state
    # rather than a hypothetical one.
    #
    # `wary` here is not a colder version of the scene. It is the same
    # invitation, extended by somebody who has decided to extend it anyway,
    # which is a different and harder thing for her to do.

    scene bg archive_room evening with dissolve

    show iris school_summer neutral at s32_centre with dissolve

    $ _iris = stance("iris")

    if _iris == "wary":

        show iris school_summer concerned

        narrator "There is a second shoebox on the desk with the lid off, and she does not move it toward you, and she does not move it away."

        c_iris "I started it."

        narrator "She has been deciding whether to show you this. You can see the shape of the deciding in how deliberately she is not looking up."

    elif regards("iris", "attraction", 6):

        narrator "There is a second shoebox on the desk with the lid off, and a second chair, which was not there on Tuesday."

        c_iris "I started it."

        narrator "She says it to the box. She has been waiting to say it since about four o'clock, and the chair is the part she will not be mentioning."

    else:

        narrator "There is a second shoebox on the desk with the lid off."

        c_iris "I started it."

    narrator "There are four cards in it. Each one is a box number, a rough description, and a date range with a question mark after it."

    c_iris "It took an hour. There are two hundred and six boxes."

    c_me "That's two hundred hours."

    c_iris "It's two hundred and six hours and I've got about four a week, which is a year, which is fine, because I'll be here."

    narrator "She says the last part slightly too quickly."

    menu:

        "Give me half.":
            $ trait("gentle")
            $ rel("iris->player", "trust", 6)
            $ rel("iris->player", "attraction", 4)
            $ rel("player->iris", "trust", 4)

            c_iris "You don't have to."

            c_me "I know."

            c_iris "..."

            narrator "She does not say yes. She takes the lid off the first box, and puts a card and a pen next to your hand, and says nothing at all for about four minutes while you both write."

            c_iris "You've put {i}tin{/i}."

            c_me "It's a tin."

            c_iris "It's a tin. Good."

            if _iris == "wary":

                narrator "You do eleven more. She checks two of yours, early on, and does not check any after that, and neither of you says anything about the checking."

            else:

                narrator "You do eleven more. It is the least interesting hour of the week and you would do it again."

        "What goes on the card that isn't in the record?":
            $ trait("curious")
            $ rel("iris->player", "respect", 5)
            $ rel("iris->player", "trust", 2)

            c_iris "What it looks like. What condition it's in. Whether there's handwriting on it and whose it might be."

            c_iris "And whether it's the sort of thing somebody kept, or the sort of thing somebody didn't throw away. Those are different and the record can't hold the difference."

            c_me "How do you tell?"

            c_iris "You can't, reliably. I write down which one I think it is and I put a question mark after it, and in four years somebody can disagree with me, and they'll have something to disagree with."

            narrator "It is, you realise, a system designed to be argued with by a stranger. She has built it that way on purpose and has never said so."

        "You'll be here in a year.":
            $ trait("reserved")
            $ rel("iris->player", "familiarity", 4)

            c_iris "I'll be here."

            narrator "She puts the lid back on and squares it against the edge of the desk."

            c_iris "That wasn't a complaint. I like it here. It's the one job in this building where nobody's waiting for the output."

            narrator "You do not say the obvious thing, and she does not appear to want you to, and the four cards stay in the box, and the box stays on the desk where you can both see it."

    hide iris with dissolve

    return


label s32_st_theo_admits_it:
    # Reached on `theo->player.trust >= 8`. What varies is resentment, which
    # `theo_the_spreadsheet` adds if the player told him a script could do his
    # job in a weekend -- and being told he is overthinking it is the one thing
    # his bible names as landing. He tells you either way. High trust plus
    # resentment is a person confiding in somebody they have not forgiven.

    scene bg common_room night with dissolve

    show theo school_summer neutral at s32_centre with dissolve

    narrator "Theo is not doing anything, which is the most alarming thing he has done all week."

    if regards("theo", "resentment", 4):

        c_theo "I'm telling you this because you'll be unbearable about it if you find out on your own."

        c_me "That's not why."

        c_theo "..."

        c_theo "No."

    c_theo "It's the annexe key."

    c_me "What is?"

    c_theo "The brass one. I've been calling it {i}a key{/i} for eleven days. It's the annexe key, it was signed out to me in March, and I've had it in a bag since March because there was never any reason to give it back."

    show theo school_summer concerned

    c_theo "And now there's no reason to have it and I can't."

    narrator "He has plainly rehearsed this and it has still come out worse than he wanted."

    c_theo "I checked the crate three times. Three. I put it in column J as {i}seen{/i} and I hadn't seen it, I'd looked at where it should be, which is the exact thing I put the column in to stop."

    menu:

        "That's an easy mistake.":
            $ trait("gentle")
            $ rel("theo->player", "trust", 6)
            $ rel("theo->player", "dependency", 3)

            c_theo "It isn't. It's the only mistake."

            c_me "It's the only mistake you've made in fourteen months of a job nobody asked you to do."

            c_theo "..."

            narrator "He takes about ten seconds with that. He does not agree with it. He does, visibly, put it somewhere."

            c_theo "I'm going to tell Ellery on Thursday."

            c_me "Do you have to?"

            c_theo "No."

            narrator "He says it as though that were the answer to a different question, and then goes and puts the kettle on, which he has never once done in your presence."

        "Tell Ellery.":
            $ trait("direct")
            $ rel("theo->player", "respect", 5)
            $ rel("theo->player", "familiarity", 2)

            c_theo "Yes."

            c_me "Tomorrow, not Thursday."

            c_theo "Thursday's when she signs."

            c_me "Tomorrow."

            c_theo "..."

            c_theo "Tomorrow."

            narrator "He appears steadier for having been given an instruction. You do not point this out."

        "You put 'seen' when you hadn't. That's the whole problem with your column.":
            $ trait("sarcastic")
            $ rel("theo->player", "resentment", 5)
            $ rel("theo->player", "trust", -3)

            c_theo "Yes. That's what I said."

            narrator "There is a pause with nothing in it."

            c_theo "I said it first and I said it about myself, and you've said it back to me as though I hadn't."

            c_me "I didn't mean —"

            c_theo "It's fine."

            narrator "He closes the laptop, which takes longer than closing a laptop needs to take, and says goodnight, and it is the politest he has ever been to you."

    hide theo with dissolve

    return
