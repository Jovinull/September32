# PROTOTYPE / NON-FINAL — Act 1 draft
#
# The commitment pair, and the two scenes that belong to the `odd` phase.
#
# `june_needs_saturday` and `the_saturday` are the milestone's answer to "A and
# B are both interesting and I can only do one". The promise is deliberately
# about nothing important. What makes it a choice is that it is somewhere else
# at the same time as the annexe.
#
# `june_reads_it_flat` is rule R5 given a scene: the ordinary explanation, made
# by somebody who is good at arguing, written so that agreeing with her is the
# more intelligent-sounding option. A game that punishes scepticism does not get
# to claim its mystery is earned.
#
# docs/canon/PHENOMENON_RULES.md, docs/narrative-design/ACT_1.md

label s32_st_june_needs_saturday:

    scene bg courtyard day with dissolve

    show june school_summer talk at s32_centre with dissolve

    c_june "Saturday. Mara's got the car, we're going into town, there are four of us and one of them is you."

    c_me "Is it?"

    c_june "It is now. You've been here two weeks and you've seen a road and a shop."

    narrator "This is true and is delivered as though it were a diagnosis."

    c_june "Half nine at the gate. It's twenty minutes there, we'll be back by two."

    menu:

        "All right. Half nine.":
            $ trait("gentle")
            $ promise("saturday_with_june", "june", 2, 50)
            $ rel("june->player", "trust", 3)

            c_june "Good. Bring money, the market's cash."

            narrator "She writes it on the back of her hand, which is a filing system Theo would have opinions about, and which has worked for June for two years."

        "Fine, but I'm not carrying anything.":
            $ trait("direct")
            $ promise("saturday_with_june", "june", 2, 50)
            $ rel("june->player", "respect", 3)

            c_june "You'll carry one thing."

            c_me "One thing."

            c_june "One thing, and it won't be heavy, and you'll offer before we get to the car park because you'll feel bad."

            narrator "She is entirely correct about this and you both know it before the sentence has finished."

        "I've got the archive on Saturday.":
            $ trait("reserved")
            $ rel("june->player", "resentment", 3)

            c_june "The archive is on Saturday because you put it on Saturday."

            c_me "It's four hours."

            c_june "It's four hours you chose. That's fine. That's a real answer."

            narrator "It is, from June, both genuinely fine and slightly cooler than the temperature the conversation started at, and she is talking to somebody else within about forty seconds."

    hide june with dissolve

    return


label s32_st_the_saturday:

    scene bg school_gate day with dissolve

    narrator "Half past nine on a Saturday. The gate is open, the car is there with the engine off, and June is on the wall with a bag."

    narrator "The annexe is also open on a Saturday. It is open because maintenance are in, and maintenance are in until twelve, and this is the only day in the next fortnight that is true."

    narrator "You found that out on Thursday and have been carrying it around ever since like a stone in a shoe."

    show june school_summer talk at s32_centre with dissolve

    c_june "You're early. That's suspicious."

    menu:

        "Get in the car.":
            $ trait("gentle")
            $ kept("saturday_with_june")
            $ rel("june->player", "trust", 6)
            $ rel("player->june", "trust", 4)

            narrator "You get in the car."

            narrator "The town has a market on Saturdays that is four stalls and a van. You buy nothing. Mara knows the man on the van and does not introduce anybody, and the man on the van gives all four of you a sample of something without being asked."

            narrator "You are back at two, exactly as advertised."

            c_june "See. Worth it."

            c_me "It was four stalls."

            c_june "It was four stalls and you laughed twice, and I counted, because I always count."

            narrator "The annexe closed at twelve. You know this and it is, on the whole, a smaller fact than it was on Thursday."

        "Say you'll catch them up.":
            $ trait("curious")
            $ broke("saturday_with_june")
            $ rel("june->player", "resentment", 6)
            $ rel("june->player", "trust", -3)
            $ learn("annexe_is_locked", source="you_went_and_looked")

            c_june "Catch us up. Into town. On foot."

            c_me "There's a bus."

            c_june "There is famously a bus."

            narrator "She does not argue past that. She gets in the car and it goes, and nobody in it looks back, which is worse than somebody looking back."

            narrator "The annexe is at the end of the east corridor behind a door with a brass plate and a lock that has not been oiled since the plate was fitted."

            narrator "Maintenance are two floors up doing something to a cistern. The door is locked. The door is locked in the specific way of a door nobody has opened in years — the paint has gone over the join."

            narrator "You stand there for a while. At twelve the maintenance van leaves and the corridor is exactly as quiet as it was, and you have learned one thing, which is that the door is real."

            narrator "You are back in your room at ten past twelve with four hours of Saturday left and nothing at all to do with them."

        "Take the bag off her.":
            $ trait("direct")
            $ kept("saturday_with_june")
            $ rel("june->player", "familiarity", 5)
            $ rel("june->player", "respect", 3)

            c_june "It's not heavy."

            c_me "You said I'd offer before the car park."

            c_june "I did say that."

            c_me "I'm ahead of schedule."

            narrator "She gives you the bag. The bag is heavy. She knew the bag was heavy and has been carrying it from the residence to the gate on principle."

            narrator "In the car she talks for the entire twenty minutes and Mara drives and says four words, and one of them is {i}left{/i}."

    hide june with dissolve

    return


label s32_st_june_reads_it_flat:

    scene bg common_room evening with dissolve

    show june school_summer neutral at s32_centre with dissolve

    narrator "You tell her about the column, because it is the sort of thing you tell somebody, and because you have been carrying it for two days."

    show june school_summer talk

    c_june "Right. So a register with no date on it."

    c_me "Ruled and filled the same as the ones either side."

    c_june "By the same person."

    c_me "By the same person."

    c_june "Then it's the same person's Tuesday."

    narrator "She does not say it dismissively. She says it the way you would identify a bird."

    c_june "Look — my mother did payroll for nineteen years. There is nothing, {i}nothing{/i}, in a set of records that is stranger than a person doing them at four in the afternoon."

    c_june "Columns get missed. Pages get done out of order and put back in order. Somebody rules a page in advance because ruling is boring and you may as well do six, and then they fill four of them and the fifth one is Thursday and they were off on Thursday."

    c_me "The column's full, though. Fourteen names."

    c_june "Then they came back and did it from the class list and didn't put the date on, because they already knew what day it was. Nobody writes the date for themselves. You write it for the person in forty years."

    narrator "This is a genuinely good argument and it takes about eleven seconds and she has not raised her voice once."

    menu:

        "That's almost certainly it.":
            $ trait("skeptical")
            $ rel("june->player", "trust", 5)
            $ rel("player->june", "respect", 5)
            $ npc_learns("june", "attendance_sheet_anomaly", "disproven")

            c_june "It is."

            c_june "And the thing about a place like this is that the alternative is always more fun, so everyone reaches for it, and then there's a story about the school that ninety people believe and nobody's checked."

            narrator "You agree with her, out loud, and it is a relief, and the relief is the part you notice — that you would like her to be right, and that wanting it is not evidence."

            c_june "Anyway. Cake on Thursday."

        "Then why is it the only one in ninety-one pages?":
            $ trait("curious")
            $ rel("june->player", "familiarity", 3)
            $ rel("june->player", "suspicion", 3)

            c_june "Because it happened once."

            c_me "In ninety-one pages."

            c_june "Things happen once. That's what once means."

            narrator "She says it lightly and it is the first sentence of the conversation that has not been an argument, and she moves on to something else about four seconds sooner than she moved on to things earlier in the evening."

            narrator "It does not prove anything. It is not nothing either, and you file it under the wrong heading twice before giving up and leaving it where it is."

        "Say nothing and let her be right.":
            $ trait("gentle")
            $ rel("june->player", "trust", 3)
            $ rel("player->june", "trust", 3)

            narrator "You let it go, and she visibly relaxes by an amount that is only detectable in retrospect."

            c_june "Sorry. I get — people here love a thing being strange. It's a village, there's nothing on, and then somebody's found a ledger."

            c_me "You're allowed to find it boring."

            c_june "I don't find it boring."

            narrator "She says this and then does not develop it, and puts the television on, and whatever is on it is about canals."

    hide june with dissolve

    return


label s32_st_annexe_door:

    scene bg hallway_east day with dissolve

    narrator "The east corridor ends in a door that is not a fire door and does not go outside."

    narrator "Brass plate, no sign, painted over at the join in the same cream as the wall — twice, by the look of it, which means the painters came round and nobody opened it either time."

    narrator "The notice in the case by the gate said the bound volumes went into the annexe. This is the annexe. It has been about four metres from the corridor you walk down every day."

    narrator "There is a keyhole. It is the sort of keyhole a brass key goes into."

    menu:

        "Try the handle.":
            $ trait("curious")
            $ trait("direct")

            narrator "It turns about a centimetre and stops, in the way of a lock that is doing its job and has been doing it for a very long time."

            narrator "The door does not move in the frame at all. Paint at the join, four hinges, and a draught excluder somebody screwed on at some point and painted over as well."

            narrator "Whatever is behind it is dry, at least. That is the entire contents of what you have learned."

        "Check whether anyone's been in recently.":
            $ trait("skeptical")
            $ npc_learns("theo", "annexe_is_locked", "known")

            narrator "The paint at the join is unbroken. Along the bottom, where a door that opens leaves a scuff, there is no scuff — there is skirting, and the skirting has the same dust on it as the skirting either side."

            narrator "Nobody has opened this door in years. Not recently, not carefully, not at all."

            narrator "You mention it to Theo the same evening. He listens, asks two questions about the paint, and writes something down, and does not say the thing you can see him deciding not to say."

        "Leave it.":
            $ trait("reserved")

            narrator "It is a locked cupboard with paper in it. You have a locked cupboard with paper in it at the other end of the building, and you have keys to that one, and you have got through about a fortieth of it."

            narrator "You go back down the corridor."

            narrator "You do, on the way, count the doors between the annexe and the stairs, which is not the behaviour of somebody who has left it."

    return
