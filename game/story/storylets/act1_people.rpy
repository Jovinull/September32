# PROTOTYPE / NON-FINAL — Act 1 draft
#
# One scene per central character whose conflict is NOT the archive, the
# photograph, or September 32. That is a rule rather than a preference: a cast
# who only ever appear in connection with the mystery are not people, they are
# exposition with faces, and the whole premise depends on the player liking the
# routine before it breaks.
#
# Plus Ms. Ellery, who has existed in the data since the bootstrap and has never
# been on screen. She has no sprite and is not getting one by downloading
# another character pack (ADR-0005), so she is played off-sprite: a voice, a
# folder and a biro. That is a real production gap being worked around, not a
# solved problem -- docs/production/ART_GAP_ANALYSIS.md.
#
# docs/narrative-design/ACT_1.md, docs/characters/

label s32_st_mara_the_long_way:
    # Reached on `mara->player.familiarity >= 6`, which she gives out cheaply.
    # Trust and suspicion she does not: pressing her about the town on the road
    # adds four suspicion and costs a point of trust, and this is the scene
    # where that shows. She still takes the long way. She just does not offer
    # anything on it.

    scene bg town_road day with dissolve

    show mara school_summer neutral at s32_centre with dissolve

    $ _mara = stance("mara")

    narrator "Mara turns left at the junction, which is not the way back."

    c_me "That's the long way."

    c_mara "It is."

    narrator "She does not explain and does not slow down, and after about forty seconds it becomes clear that you are going the long way."

    narrator "The long way has a hedge on one side and a field on the other, and a gate in the hedge that has been wired shut for so long the wire has gone into the wood."

    c_mara "That's the Corrigans'. There aren't any Corrigans."

    c_me "Then whose gate is it?"

    c_mara "It's the Corrigans'."

    narrator "There is a dog at the next house that has decided about you, and it makes its position clear from behind a fence with total confidence and no follow-through."

    show mara school_summer talk

    c_mara "That's Bill. He does that to everyone for about a year and then stops."

    c_me "A year?"

    c_mara "About a year. You'll know when it happens. You'll come past and he won't get up, and you'll feel worse about it than you expect to."

    if _mara == "wary":

        narrator "You walk the rest of it. It takes eleven minutes longer than the short way and she names four more things without being asked about any of them, and does not once say anything about herself."

        narrator "It is a good walk. It is also, you notice about halfway, a tour of things rather than a conversation, and you are fairly sure she could keep this up for an hour."

    else:

        narrator "You walk the rest of it. It takes eleven minutes longer than the short way and neither of you says very much, and it is not uncomfortable."

    menu:

        "Thanks for walking back with me.":
            $ trait("gentle")
            $ rel("player->mara", "trust", 6)
            $ rel("mara->player", "trust", 4)

            c_mara "I was going this way."

            c_me "You weren't."

            c_mara "..."

            if _mara == "wary":

                c_mara "I go this way sometimes."

                narrator "Which is not a no, and is as close to one as she is willing to be, and she looks at the hedge for the next thirty seconds."

            else:

                c_mara "No."

                narrator "She says it and keeps walking and does not appear to want anything done with it, and you find you have stopped reading her as cold, which took a fortnight less than you would have guessed."

        "Why does everyone here explain things by not explaining them?":
            $ trait("curious")
            $ rel("player->mara", "respect", 6)
            $ learn("june_arrived_alone", source="mara_mentioned_it")

            c_mara "Because everyone already knows."

            c_mara "You're the first person in two years who's had to be told anything. Before you it was June, and she came on her own in the middle of a term, which is worse."

            c_me "Worse how?"

            c_mara "You arrive in September and there's a queue of you. She arrived in February and there was a queue of one."

            narrator "She says it factually, without sympathy, in a way that makes it clear that she noticed at the time and has kept noticing."

        "Say nothing and keep walking.":
            $ trait("reserved")
            $ rel("player->mara", "respect", 3)
            $ rel("mara->player", "familiarity", 2)

            narrator "You walk. She points at two more things without being asked — a postbox, a bend where a lorry went through a wall in the nineties — and does not require a response to either."

            narrator "At the gates she says right, then, and goes, and the whole thing turns out to have been a tour."

    hide mara with dissolve

    return


label s32_st_theo_the_spreadsheet:

    scene bg common_room evening with dissolve

    show theo school_summer neutral at s32_centre with dissolve

    narrator "Theo has the laptop open and has turned it very slightly toward you, which from Theo is a fanfare."

    c_theo "Column J."

    c_me "Column J."

    c_theo "Column J is {i}seen{/i}. Not {i}logged{/i}. Logged means somebody wrote down that it exists. Seen means I have had the lid off."

    narrator "There are two hundred and six rows. Column J is about a third full."

    c_theo "The accession record has eleven boxes I can't find. Not missing — I can't find them, which is a different claim and I'm being careful about the difference."

    show theo school_summer talk

    c_theo "Six of those are almost certainly a numbering thing from before the reorganisation. Two are probably in the annexe. Three I have no theory about, and I like that I have no theory rather than a bad one."

    menu:

        "What happens when column J is full?":
            $ trait("curious")
            $ rel("theo->player", "trust", 4)
            $ rel("theo->player", "respect", 2)

            c_theo "Then the spreadsheet is finished and I'll have to think of something else."

            narrator "He says it as a joke and it does not entirely arrive as one."

            c_theo "It won't be full. There's always another box. That's not a complaint."

            narrator "He turns the laptop back and does something to a cell, and you notice he has a colour for {i}checked twice{/i} and that it is a nicer colour than the one for {i}checked{/i}."

        "Nobody asked you to do this.":
            $ trait("gentle")
            $ rel("theo->player", "trust", 3)
            $ rel("theo->player", "familiarity", 3)

            c_theo "No."

            c_me "That wasn't a criticism."

            c_theo "I know. People usually say it as one."

            narrator "He goes back to it. Twenty seconds later, without looking up:"

            c_theo "It's not that I think something's wrong with the archive. It's that if it were, this is the shape the wrongness would be, and it costs me four hours a week to be able to say that."

            narrator "It is the longest sentence you have heard him produce, and he says it to a laptop."

        "You could get that down to a weekend with a script.":
            $ trait("direct")
            $ rel("theo->player", "respect", 4)
            $ rel("theo->player", "resentment", 2)

            c_theo "A script would tell me what the record says."

            c_me "Right."

            c_theo "The record is the thing I'm checking."

            narrator "He is not annoyed, exactly. He is the specific flavour of not-annoyed of a person who has had this conversation before and would rather not have had it again."

            c_theo "You're not wrong about the weekend."

    hide theo with dissolve

    return


label s32_st_june_the_kitchen:

    scene bg common_room evening with dissolve

    show june school_summer neutral at s32_centre with dissolve

    narrator "June has a piece of paper and is not going to explain it until she has your attention, which she gets by waiting."

    c_june "It's Priya's birthday on Thursday and nobody's doing anything about it."

    c_me "Who's Priya?"

    show june school_summer talk

    c_june "Second floor, does chemistry, has the good hairdryer. She's had two birthdays here and both times somebody said {i}oh, was it your birthday{/i} on the Friday."

    narrator "The piece of paper is the kitchen rota. She has turned it over and started using the back."

    c_june "So. Cake is me. Card is you, because you have handwriting. Mara knows the shop that does the ones that aren't horrible. Theo will do the thing where he asks whether anyone has checked it's actually Thursday, and he'll be right, and we'll need him for that."

    c_me "What's Noah doing?"

    c_june "Noah's going to want to make it a piece."

    narrator "She says this without any particular malice and moves on, and the whole plan takes four minutes and is finished."

    narrator "Watching it happen is like watching somebody parallel park a van on the first attempt."

    menu:

        "You're good at this.":
            $ trait("gentle")
            $ rel("player->june", "trust", 6)
            $ rel("june->player", "trust", 4)

            c_june "It's not a skill, it's just noticing."

            c_me "That's a skill."

            c_june "..."

            c_june "The first year I was here nobody did anything for mine and I decided that was going to be the last time it happened to anybody in this building. Which is a stupid thing to build a personality on."

            narrator "She laughs, and the laugh arrives about a beat early, and she has already moved on to the question of candles."

        "How did you know it was Thursday?":
            $ trait("curious")
            $ rel("player->june", "respect", 5)
            $ learn("june_arrived_alone", source="she_said_it_lightly")

            c_june "Because I keep a list."

            c_me "Of birthdays."

            c_june "Of everybody's. It's on the back of my timetable, it takes about a minute a term, and it means nobody here gets the Friday thing."

            narrator "She says it lightly and quickly, in the specific tempo she uses when a subject has an edge on it, and the tempo is the whole tell."

            c_june "I came in February, by the way. There is no queue in February."

            narrator "And then she is talking about candles, and the door is shut, and it was open for about three seconds."

        "I have terrible handwriting.":
            $ trait("reserved")
            $ rel("june->player", "respect", 3)
            $ rel("player->june", "familiarity", 3)

            c_june "You wrote your name on the sign-out book. I've seen it. It's fine."

            c_me "You've inspected the sign-out book."

            c_june "I inspect everything. It's how I know who's out and who's sulking."

            narrator "She hands you the card anyway, and it turns out she has already bought the card, which means the four minutes of planning were a formality performed for your benefit."

    hide june with dissolve

    return


label s32_st_noah_the_sports_report:

    scene bg classroom_2b day with dissolve

    show noah school_summer concerned at s32_centre with dissolve

    narrator "Noah is at a desk with a notebook, a phone, and the specific posture of somebody about to write two hundred words they do not want to write."

    c_noah "Netball. Away. We lost. I wasn't there."

    c_me "How do you write it if you weren't there?"

    c_noah "You write {i}a spirited second half{/i} and you go home."

    narrator "He does not write {i}a spirited second half{/i}. He phones somebody who was there, and asks four questions, and the fourth one is what was the weather like."

    show noah school_summer talk

    c_noah "Right. It rained from about twenty past and they'd already made both their substitutions."

    c_me "Does that matter?"

    c_noah "It's the difference between {i}we lost{/i} and {i}we lost after an hour on a pitch that had turned{/i}. Two hundred words either way."

    menu:

        "Nobody's going to notice.":
            $ trait("skeptical")
            $ rel("noah->player", "resentment", 3)
            $ rel("noah->player", "respect", 2)

            c_noah "Seven people will notice."

            c_me "Seven."

            c_noah "The eleven who played, minus the four who don't read it. They'll notice because they were there, and if I get it wrong they'll know the paper's the kind of thing that gets it wrong."

            narrator "He says it evenly, and then goes quiet for a second, and then writes for six minutes without saying anything at all, which is the longest you have known him to be silent."

        "Who did you phone?":
            $ trait("gentle")
            $ rel("noah->player", "trust", 4)
            $ rel("noah->player", "dependency", 2)

            c_noah "Wing defence. She's the only one who'll tell me we were bad."

            c_noah "Everyone else does the thing where the score was a bit unfair. She said we were slow in the middle third and she said it in about four words."

            c_me "And that goes in?"

            c_noah "That goes in with her name on it, because if I put it in my own voice it's me being clever about people I didn't watch."

            narrator "It is the first thing you have heard him say that sounds like a rule rather than an enthusiasm."

        "Two hundred words is nothing. Do it properly.":
            $ trait("direct")
            $ rel("noah->player", "respect", 4)

            c_noah "That's what I'm doing."

            c_me "I know. I'm agreeing with you."

            c_noah "..."

            c_noah "Oh."

            narrator "He appears to be storing this for later use, and then writes the thing, and reads it out, and it is better than it needs to be by a distance that is slightly sad."

    hide noah with dissolve

    return


label s32_st_iris_the_apology:

    scene bg archive_room day with dissolve

    show iris school_summer neutral at s32_centre with dissolve

    narrator "There is a paperweight on the desk. Glass, with something orange suspended in it, from a box that has otherwise turned out to be entirely certificates."

    narrator "You pick it up, the way you pick up a paperweight."

    narrator "She takes it out of your hands."

    narrator "It is not fast and it is not rough. She takes it the way a nurse takes something, and she is already apologising while she is doing it."

    show iris school_summer concerned

    c_iris "Sorry. Sorry — I do that."

    narrator "She puts it back on the felt at an angle that is apparently the correct angle."

    c_iris "It's not that you'd break it. It's that I haven't photographed it yet."

    menu:

        "Then photograph it.":
            $ trait("gentle")
            $ rel("iris->player", "trust", 5)
            $ rel("iris->player", "attraction", 2)

            narrator "She does. It takes ninety seconds — the felt, the light from the window rather than the overhead, a card with a number on it that she writes while the shutter is still going."

            c_iris "There. Now you can hold it."

            narrator "You hold it. It is a paperweight. The orange thing is a piece of orange plastic and was made in about 1974 and is not a mystery, and she watches you hold it with an attention that is not about the paperweight."

            c_iris "Thank you for waiting."

            c_me "It was ninety seconds."

            c_iris "People don't, though."

        "Why does it have to be photographed first?":
            $ trait("curious")
            $ rel("iris->player", "respect", 3)
            $ learn("iris_keeps_a_second_index", source="she_almost_said_it")

            c_iris "Because after it's catalogued it's a line."

            c_me "It's still a paperweight."

            c_iris "It's a line that says {i}paperweight, glass, orange inclusion{/i}, and in four years that's the only thing anyone will read, and the line is right and it isn't the object."

            narrator "She hears herself, and stops, and does the small recalibration of somebody who has said a true thing in a room where they had intended to say a normal one."

            c_iris "I keep my own record. It's cards, it's not official. Anyway."

        "It's a paperweight.":
            $ trait("direct")
            $ rel("iris->player", "resentment", 3)
            $ rel("iris->player", "respect", 2)

            c_iris "Yes."

            narrator "She does not argue. She puts it on the felt and moves the felt slightly and goes back to the scanner, and the room is exactly as it was except for a temperature you would struggle to measure."

            c_iris "You're right, it's a paperweight. Sorry, that was a lot for a paperweight."

            narrator "It occurs to you, about an hour later, that she apologised twice in a conversation in which she did nothing wrong."

    hide iris with dissolve

    return


label s32_st_ellery_the_sign_off:

    # ART GAP: Ellery has no sprite in the current asset set, and is not going
    # to get one by downloading another character pack (ADR-0005). Rather than
    # stand a labelled placeholder on the stage for a whole scene, she is played
    # off-sprite: she is a voice, a folder and a biro, and the scene is written
    # so that works. This is a real production gap, not a solved one --
    # docs/production/ART_GAP_ANALYSIS.md.

    scene bg archive_room day with dissolve

    narrator "Ms. Ellery supervises the archive project in the sense that she signs a sheet about it on Thursdays."

    narrator "She comes in at ten past four with a folder and does not sit down, because she is not going to be here long enough for sitting down to be worth the trouble."

    c_ellery "Boxes eleven to fourteen."

    c_me "Done. Photographed and logged."

    c_ellery "Logged where?"

    c_me "The spreadsheet."

    c_ellery "Theo's or the real one?"

    narrator "There is no edge on the question. She is establishing which of two records she is being asked to sign against, and a person about to put her name on something is entitled to know."

    c_ellery "Both, then. Good."

    narrator "She countersigns four lines, dates them, and squares the sheet against the edge of the desk before putting it in the folder, and the whole transaction takes ninety seconds."

    menu:

        "Does anyone ever read these?":
            $ trait("direct")
            $ rel("ellery->player", "respect", 4)

            c_ellery "I do."

            c_ellery "And if this school is ever inspected, or sued, or closed, somebody will read them very carefully indeed, and on that day it will matter enormously that they are boring."

            narrator "She says it pleasantly. It is, you realise, the most confident sentence anybody has said to you in this building."

        "Thanks for signing it off.":
            $ trait("gentle")
            $ rel("ellery->player", "trust", 4)

            c_ellery "It's the job."

            narrator "She pauses at the door with the folder under her arm."

            c_ellery "You've done four boxes in a week, which is three more than the last person, and you've written the descriptions out rather than putting {i}misc{/i}."

            c_ellery "I do notice. I don't often say."

        "What's in the annexe?":
            $ trait("curious")
            $ rel("ellery->player", "respect", 2)
            $ learn("annexe_is_locked", source="the_office_has_no_key")

            c_ellery "Overflow. Bound volumes, mostly, and some furniture."

            c_me "Can I get in?"

            c_ellery "Not through me. The office doesn't hold that key — it went with the maintenance contract in whatever year that was, and nobody has needed it since."

            narrator "She says this in exactly the tone she used about the spreadsheets, which is to say without the slightest interest, and she is plainly telling the truth."

            c_ellery "If you want it opened, put it in writing and I'll forward it to somebody who will not answer."

    narrator "She goes. The folder goes with her, and so does the only copy of the sheet, and that is presumably the point of a folder."

    return
