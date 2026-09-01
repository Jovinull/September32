# PROTOTYPE / NON-FINAL — Act 1 draft
#
# Milestone 4. Eight scenes, each written for one thing the editorial audit
# found the first week could not do:
#
#   Iris exists somewhere other than the archive
#   Mara is confidently, specifically wrong
#   Theo has an ego and is embarrassed about it
#   June is the one being handled
#   Noah is avoiding something that has nothing to do with any of this
#   Ms. Ellery is a wall made of reasonable things
#   the community predates the protagonist
#   the school has lessons in it
#
# Not one of these was written to fill a cell.
# docs/narrative-design/ACT_1_CHARACTER_ARCS.md


label s32_st_iris_the_wrong_photograph:

    scene bg courtyard day with dissolve

    show iris school_summer neutral at s32_centre with dissolve

    narrator "Iris is crouched by the bike rack with the camera, doing something to the settings with her thumb, and has been for a while."

    c_me "What's in the bike rack?"

    c_iris "Nothing's in the bike rack."

    narrator "She takes the photograph. She looks at the back of the camera. She deletes it and takes it again from about eight inches to the left."

    c_iris "The rust has gone through the paint in a line and it's stopped exactly at the weld."

    c_me "Right."

    c_iris "It's not interesting. I'm aware it's not interesting."

    show iris school_summer talk

    narrator "She takes a third one. This one she keeps."

    menu:

        "Show me the others.":
            $ trait("curious")
            $ rel("iris->player", "trust", 4)
            $ rel("iris->player", "attraction", 3)

            narrator "She scrolls back and does not editorialise, which takes some doing."

            narrator "A drain cover. A section of skirting board with three colours of paint on it. The underside of the hatch counter. Somebody's abandoned trainer, from two angles, on two different days, so you can see it has moved."

            c_iris "That one's a whole thing. It's been there since term started and it keeps going about a foot."

            c_me "You're documenting a shoe."

            c_iris "I'm documenting a shoe."

            narrator "She says it perfectly cheerfully, and puts the camera away, and does not offer to explain any of it, and you find you do not need her to."

        "Is any of this for the archive?":
            $ trait("gentle")
            $ rel("iris->player", "familiarity", 4)

            c_iris "God, no."

            c_iris "The archive gets the good camera and a card and a number. This is — "

            narrator "She stops, and does the thing where she recalibrates a sentence mid-air."

            c_iris "This is the other one."

            c_me "The other what?"

            c_iris "The other camera."

            narrator "That is not what she meant and both of you let it stand, and she photographs the drain by the science block on the way back in."

        "You're going to run out of storage.":
            $ trait("direct")
            $ rel("iris->player", "respect", 3)
            $ rel("iris->player", "resentment", 2)

            c_iris "I have run out of storage. Twice."

            c_me "And?"

            c_iris "And I bought more storage."

            narrator "It is said without any defensiveness at all, which is somehow worse, and she goes back to the bike rack."

            narrator "You have made a joke about the size of a problem and been told the size of the problem. This is a specific way of losing an exchange and you have not encountered it before."

    hide iris with dissolve

    return


label s32_st_mara_is_wrong:

    scene bg hallway_east day with dissolve

    show mara school_summer neutral at s32_centre with dissolve

    narrator "Mara is at the window on the turn of the stairs, which is where she is when she is not going anywhere."

    c_mara "Theo's fallen out with somebody."

    c_me "Has he."

    c_mara "He's eaten in the library twice. He doesn't like the library, he thinks the chairs are stupid."

    narrator "She says it the way she says everything, which is as a completed thought."

    c_mara "It'll be Iris. It's the room, or it's the spreadsheet. He's proud about the spreadsheet."

    narrator "It is a good reading. It is built out of two real observations and a thing she knows about him, and it is the kind of reading she has been right about all week."

    narrator "It is also wrong, and you know it is wrong, because Theo told you on Tuesday that the library is the only room in the building where the radiator works and he has been trying to finish the crate before it gets cold."

    menu:

        "The radiator in the annexe corridor's broken. That's all it is.":
            $ trait("gentle")
            $ rel("mara->player", "trust", 5)
            $ rel("player->mara", "respect", 3)

            c_mara "..."

            c_mara "The radiator."

            c_me "He told me on Tuesday."

            narrator "She takes about four seconds with this, and does not argue, and does not look thrilled."

            c_mara "Right. Yes. That's better than mine."

            c_me "Yours was good."

            c_mara "Mine was good and it was wrong, which is the problem with mine."

            narrator "She says it flatly and it is not self-pity and it is not a joke. It is a person filing a correction, and she has clearly done it before, and it clearly does not get easier."

        "You do this a lot, and you're usually right.":
            $ trait("direct")
            $ rel("mara->player", "respect", 4)
            $ rel("mara->player", "resentment", 4)

            c_mara "Usually."

            c_me "So what happens when you're not?"

            narrator "The pause here is not one of her deliberate ones."

            c_mara "Then somebody's been walking round for a fortnight thinking a thing about somebody that isn't true, and it's my fault, and I don't find out."

            c_mara "That's not a hypothetical, before you ask. I'm not going to tell you which one."

            narrator "She goes down the stairs. It is the first time this week she has ended a conversation rather than let it end."

        "Say nothing.":
            $ trait("reserved")
            $ rel("mara->player", "familiarity", 3)
            $ rel("player->mara", "suspicion", 3)

            narrator "You do not correct her, and she does not find out, and the two of you talk about something else for six or seven minutes."

            narrator "She is good company. She is funny about the chairs in the library, which she has also decided are stupid, and about a teacher, and about the state of the bike rack."

            narrator "You will be listening differently to the next thing she tells you about somebody, and she will have no idea, and that is now a thing you are carrying rather than a thing she is."

    hide mara with dissolve

    return


label s32_st_theo_the_quiz:

    scene bg common_room evening with dissolve

    show theo school_summer neutral at s32_centre with dissolve

    narrator "There is a quiz on the television that nobody in this room is watching except Theo, who is watching it the way a person watches a fixture."

    c_theo "Bismuth."

    narrator "It was bismuth."

    c_theo "Nineteen seventy-four."

    narrator "It was nineteen seventy-two, and he says a word under his breath that you have not previously heard him use."

    show theo school_summer concerned

    c_theo "Seventy-two. It's the album, I always do the album."

    narrator "He is keeping score. On paper. In a notebook that has other people's scores in it, from previous weeks, in a column."

    menu:

        "Who's winning?":
            $ trait("gentle")
            $ rel("theo->player", "trust", 4)
            $ rel("theo->player", "attraction", 2)

            c_theo "Me. Obviously me, nobody else plays."

            c_me "There are four names in that book."

            c_theo "..."

            c_theo "There were four names in that book. Ade did three weeks and got bored. Priya's competitive and doesn't like losing to a spreadsheet, her words."

            narrator "He turns a page back and looks at the column of Thursdays, and does not say the thing, and it is very obvious what the thing is."

            c_theo "You could do next week. If you're about."

            narrator "It is the least casual attempt at casual you have ever witnessed and you have the good manners not to point at it."

        "Round four is always music. You always lose round four.":
            $ trait("direct")
            $ rel("theo->player", "respect", 4)

            c_theo "I do not always lose round four."

            narrator "He checks the notebook. He checks four Thursdays of the notebook."

            c_theo "I always lose round four."

            c_me "It's not a moral failing."

            c_theo "It is a systematic one, which is worse, because it means I could have fixed it and haven't."

            narrator "He writes something at the top of the page. You are reasonably confident it says {i}music{/i}."

        "This is the most invested I've seen you in anything.":
            $ trait("sarcastic")
            $ rel("theo->player", "resentment", 3)
            $ rel("theo->player", "familiarity", 3)

            narrator "The notebook closes."

            c_theo "It's a quiz."

            c_me "I know."

            c_theo "It's on at nine on a Thursday and it's forty minutes."

            narrator "He watches the rest of it. He does not write anything down for the rest of it either, and he gets six of the next eight, and you both know he is not writing them down because you are sitting there."

    hide theo with dissolve

    return


label s32_st_june_is_not_fine:

    scene bg courtyard day with dissolve

    show june school_summer neutral at s32_centre with dissolve

    narrator "June is on the wall with her phone face down beside her, which is not where June's phone lives."

    c_june "Hi. Hello. Good. How was — what have you got this afternoon?"

    narrator "Three openings in one breath, and she picks the third, and it is the one about you."

    c_me "Double history."

    c_june "God. With the — yes. Right."

    narrator "She has run out of the thing she was doing, which was talking, and she reaches for a second one, which is also talking."

    show june school_summer talk

    c_june "So Priya's card worked, by the way, she did the whole face. I'm going to do Ade's in November, he'll pretend to hate it."

    narrator "It is a good story and it is being told at slightly the wrong speed, and the phone stays face down through all of it."

    menu:

        "You don't have to do the story.":
            $ trait("gentle")
            $ rel("june->player", "trust", 6)
            $ rel("player->june", "trust", 4)

            c_june "..."

            c_june "No, I know."

            narrator "She does not tell you what it is. She stops telling you what it isn't, which is a different and larger thing, and the two of you sit on the wall for about six minutes."

            c_june "It's not a big one. It's a phone call I've got to make and I've been not making it since half eleven."

            c_me "Do you want to make it now?"

            c_june "No."

            c_june "I'll make it at four."

            narrator "At four she makes it. You are not there. She tells you the next day that she made it, unprompted, in the middle of something else, which is her way of saying thank you and is not going to be acknowledged as one."

        "Sit down and let her get on with it.":
            $ trait("reserved")
            $ rel("june->player", "respect", 4)
            $ rel("june->player", "familiarity", 2)

            narrator "You let her have the story. She does Priya's card, and Ade in November, and a thing about the hatch, and by the fourth one it is working properly and she has stopped doing it at the wrong speed."

            narrator "The phone stays face down. Whatever it is is still there at the end and she is in better shape to go and meet it, and you did that by sitting on a wall and laughing in the right places."

            c_june "Right. Things to do."

            narrator "She picks the phone up on the way out without looking at it, which is a person who has decided rather than a person who has forgotten."

        "What's on the phone?":
            $ trait("direct")
            $ rel("june->player", "resentment", 4)
            $ rel("player->june", "respect", 3)

            narrator "There is a very short pause and then she is entirely fine."

            c_june "Oh — nothing. Sorry, was I being weird? I've got a call to make and I'm putting it off, that's the whole of it."

            c_june "Anyway, the card. Priya did the whole face."

            narrator "And she does the story again, from the start, at the correct speed this time, and it is genuinely funny, and you get nothing else for the rest of the afternoon."

            narrator "You have watched somebody close a door so smoothly that it took you until the evening to notice which door it was."

    hide june with dissolve

    return


label s32_st_noah_takes_a_call:

    scene bg school_gate evening with dissolve

    show noah school_summer talk at s32_centre with dissolve

    narrator "Noah is mid-sentence about the paper — the third column again, the perennial third column — when his phone goes and he looks at it and stops being mid-sentence."

    c_noah "Two minutes. Sorry. Two minutes."

    narrator "He goes about fifteen metres down the road, which is further than the signal requires."

    narrator "You cannot hear any of it. You can see that he says very little, and that most of what he does say is short, and that at one point he stands entirely still for about twenty seconds."

    show noah school_summer neutral

    narrator "He comes back putting the phone in the wrong pocket."

    c_noah "Right. Third column."

    menu:

        "Everything all right?":
            $ trait("gentle")
            $ rel("noah->player", "trust", 5)
            $ rel("noah->player", "dependency", 2)

            c_noah "Yeah. My mum."

            c_noah "She's fine. It's a — it's a whole thing at home, and it's not a bad thing, it's just a thing, and she rings on a Tuesday and I don't always want a Tuesday."

            narrator "This is more than he had to say and less than an explanation, and he appears to have surprised himself with the amount."

            c_noah "Anyway. Third column."

            narrator "He does the third column. He is quieter about it than he has ever been about anything, and he does not want that mentioned, and you do not mention it."

        "Third column.":
            $ trait("reserved")
            $ rel("noah->player", "respect", 3)
            $ rel("noah->player", "familiarity", 2)

            c_noah "Third column."

            narrator "And that is it. You do eight centimetres of the paper standing at a gate in the dark, and he talks the entire time, at the usual speed, about a fixture and a teacher and the perennial problem of the third column."

            narrator "Twice he loses the thread and picks up a different one, which he does not normally do."

        "That wasn't two minutes.":
            $ trait("curious")
            $ rel("noah->player", "suspicion", 4)
            $ rel("player->noah", "suspicion", 3)

            c_noah "Wasn't it?"

            c_me "It was about six."

            c_noah "..."

            c_noah "You timed it."

            narrator "He says it lightly and it is not a light sentence, and you are aware that you have just told him something about yourself that you had not planned to."

            c_noah "It was my mum. You can have that for free."

            narrator "He goes back to the paper. The rest of the conversation is entirely normal and you are the one who is now being careful."

    hide noah with dissolve

    return


label s32_st_ellery_and_the_form:

    # Off-sprite, deliberately and consistently with ellery_the_sign_off. This
    # is a production gap being worked around and it is recorded as one:
    # docs/production/ART_PRODUCTION_PLAN.md

    scene bg archive_room day with dissolve

    narrator "You ask Ms. Ellery whether you can take box seventeen out of the room."

    narrator "You have a good reason. The scanner in the archive is the school's second-worst scanner and there is a better one in the office, and doing it there would save about four hours."

    c_ellery "No."

    narrator "There is a pause in which you assemble the reason again, more carefully."

    c_ellery "It's a good reason. The answer is still no, and I'll tell you why, because you'll only think it's arbitrary otherwise."

    c_ellery "If it leaves this room it's off the accession record and onto a movement log, and there isn't a movement log, because nothing has left this room since 2011."

    c_ellery "I'd have to start one. To start one I'd have to know what's in the box. Nobody knows what's in the box. That's the job you're doing."

    menu:

        "So it's circular.":
            $ trait("direct")
            $ rel("ellery->player", "respect", 4)
            $ rel("ellery->player", "resentment", 2)

            c_ellery "It is completely circular and it has been since before you were born."

            c_me "Doesn't that bother you?"

            c_ellery "It bothers me on Thursdays for about ten minutes."

            narrator "She is not being flippant. She means the ten minutes and she means that they are on Thursdays."

            c_ellery "The alternative is that I make an exception for a sensible person with a good reason, and then the next sensible person has a precedent, and in four years the box is in somebody's car."

        "Could I have it in writing? I'd like to show Theo.":
            $ trait("gentle")
            $ rel("ellery->player", "trust", 4)

            c_ellery "Yes."

            narrator "She writes it out there and then, three lines, on a compliment slip, and signs it and dates it."

            c_ellery "He'll want the reference number. There isn't one, so I've put {i}no movement log extant{/i}, which is the truthful version and which he will enjoy."

            narrator "She is right. He does enjoy it. He puts it in the front of the spreadsheet folder and it is still there in November."

        "Who could say yes?":
            $ trait("skeptical")
            $ rel("ellery->player", "respect", 2)
            $ rel("player->ellery", "suspicion", 3)

            c_ellery "In principle, the head. In practice, nobody has asked the head about the archive since the reorganisation, and if you ask her she will ask me, and I will say what I have just said to you."

            c_me "That's a closed loop."

            c_ellery "That is an institution."

            narrator "She says it without any pleasure and without any apology, and goes to sign something else."

            narrator "You are aware, walking back to the boxes, that nothing she said was unreasonable and that you got nothing, and that you cannot name the moment where the second part happened."

    return


label s32_st_courtyard_before_you:

    scene bg courtyard day with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "Somebody shouts {i}not the bench{/i} across the courtyard, and about six people laugh, and one of them puts something down."

        narrator "You do not know what happened to the bench. Nobody is going to tell you, because nobody has registered that you were not here for it."

    elif _v == 2:

        narrator "Two of the year above conduct an entire negotiation about a locker using four words and a gesture, and settle it, and separate."

        narrator "It took eleven seconds. Whatever the four words meant, they have meant it for a long time."

    else:

        narrator "There is a name written on the underside of the hatch counter in biro, where you only see it if you are short or leaning, and the woman in the hatch has clearly never seen it."

        narrator "Three people this week have leant on that counter and looked at it and smiled and said nothing, and you have watched two of them do it."

    return


label s32_st_classroom_the_lesson:

    scene bg classroom_2b day with dissolve

    $ _v = s32_rng().randint(1, 3)

    if _v == 1:

        narrator "Double history, and the radiator is winning."

        narrator "You take four pages of notes, three of which are the lesson and one of which is a diagram of the room with everybody's usual seat on it, which you started for no reason and have been maintaining for a week."

        narrator "Nobody sits anywhere different. Ever. You have checked."

    elif _v == 2:

        narrator "Somebody asks a question that is actually a question and not a bid, and the room goes briefly and genuinely quiet while it gets answered."

        narrator "It happens perhaps twice a term. Both times this term it has been the same person and it has not been you."

    else:

        narrator "The last fifteen minutes are silent reading, which the whole room treats as a gift and nobody has ever said so out loud."

        narrator "Outside, somebody is doing something to the guttering with a ladder, badly, at length, and forty people watch it through the window and pretend to be reading."

    return
