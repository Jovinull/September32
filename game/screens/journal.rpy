# The clue journal and archive viewer — scaffold.
#
# This is a prototype of the two interfaces that matter most after the dialogue
# box, built far enough to prove the data is there and to be usable in testing.
# It is deliberately NOT finished: the archive viewer is where a commission
# budget produces the most distinctive result in this game, and building a
# polished version now would mean throwing it away.
#
# What is real here: everything it displays comes from live engine state, so it
# doubles as a check that the knowledge model holds what the story needs.
#
# See docs/style/VISUAL_DESIGN_SYSTEM.md for the intended direction, and
# docs/production/ART_GAP_ANALYSIS.md for what is missing.

screen s32_journal():

    tag menu

    add "#141210"

    frame:
        style "s32_journal_frame"

        vbox:
            spacing 20

            label _("What you know") style "s32_journal_heading"

            hbox:
                spacing 40

                ## Facts, grouped by how firmly they are held. The grouping is
                ## the point: "suspected" and "known" are different states and
                ## the player should see the difference.
                vbox:
                    xsize 700
                    spacing 14

                    $ _known = s32_journal_facts("known")
                    $ _suspected = s32_journal_facts("suspected")
                    $ _disproven = s32_journal_facts("disproven")

                    text _("Established") style "s32_journal_section"
                    if _known:
                        for _fact in _known:
                            text "[_fact]" style "s32_journal_entry"
                    else:
                        text _("Nothing yet.") style "s32_journal_muted"

                    null height 10

                    text _("Suspected") style "s32_journal_section"
                    if _suspected:
                        for _fact in _suspected:
                            text "[_fact]" style "s32_journal_entry"
                    else:
                        text _("Nothing yet.") style "s32_journal_muted"

                    if _disproven:
                        null height 10
                        text _("Ruled out") style "s32_journal_section"
                        for _fact in _disproven:
                            text "[_fact]" style "s32_journal_muted"

                ## Objects and open promises.
                vbox:
                    xsize 420
                    spacing 14

                    text _("Carrying") style "s32_journal_section"
                    $ _items = s32_journal_items()
                    if _items:
                        for _item in _items:
                            text "[_item]" style "s32_journal_entry"
                    else:
                        text _("Nothing.") style "s32_journal_muted"

                    null height 10

                    text _("Promised") style "s32_journal_section"
                    $ _promises = s32_journal_promises()
                    if _promises:
                        for _promise in _promises:
                            text "[_promise]" style "s32_journal_entry"
                    else:
                        text _("Nothing outstanding.") style "s32_journal_muted"

                    ## Contradictions the player is actually holding. This is
                    ## the mechanic that makes an unreliable archive legible
                    ## (rule R8), and seeing it listed is meant to be
                    ## uncomfortable.
                    $ _clashes = s32_journal_contradictions()
                    if _clashes:
                        null height 10
                        text _("These cannot both be true") style "s32_journal_warning"
                        for _clash in _clashes:
                            text "[_clash]" style "s32_journal_entry"

    textbutton _("Return"):
        style "return_button"
        action Return()


init python:

    def s32_journal_facts(stance):
        """Return the player's facts at one stance, as readable summaries."""
        beliefs = S32State.get("beliefs", {}).get("player", {})
        summaries = []
        for fact_id, entry in sorted(beliefs.items()):
            if entry["stance"] != stance:
                continue
            definition = s32_library.knowledge.get(fact_id)
            summaries.append(definition.summary if definition else fact_id)
        return summaries

    def s32_journal_items():
        """Return the display names of everything the player is carrying."""
        names = []
        for item_id in S32State.get("inventory", []):
            definition = s32_library.items.get(item_id)
            names.append(definition.display_name if definition else item_id)
        return names

    def s32_journal_promises():
        """Return open promises as readable lines."""
        lines = []
        for record in s32_commitments.open_commitments(S32State):
            who = ", ".join(
                s32_library.characters[c].display_name
                for c in record["participants"]
                if c in s32_library.characters
            )
            due = record["due_day"] - S32State["world"]["day"]
            when = "today" if due <= 0 else ("tomorrow" if due == 1 else "in {} days".format(due))
            lines.append("{} — {}".format(who or record["kind"], when))
        return lines

    def s32_journal_contradictions():
        """Return pairs of held facts that cannot both be true."""
        lines = []
        for left, right in s32_knowledge.contradictions(S32State, s32_library):
            left_def = s32_library.knowledge.get(left)
            right_def = s32_library.knowledge.get(right)
            lines.append(
                "{}  /  {}".format(
                    left_def.summary if left_def else left,
                    right_def.summary if right_def else right,
                )
            )
        return lines


style s32_journal_frame is empty:
    xalign 0.5
    yalign 0.5
    xsize 1280
    ysize 880
    padding (48, 40)
    background "#1c1a1690"

style s32_journal_heading is text:
    size 48
    color "#e8e2d4"
    font "gui/vendor/fonts/SourceSerif4-Semibold.ttf"

style s32_journal_section is text:
    size 24
    color "#d8b978"
    font "gui/vendor/fonts/SourceSans3-Semibold.ttf"

style s32_journal_entry is text:
    size 20
    color "#ddd6c6"
    font "gui/vendor/fonts/SourceSerif4-Regular.ttf"

style s32_journal_muted is text:
    size 19
    color "#8f887a"
    font "gui/vendor/fonts/SourceSans3-Regular.ttf"

style s32_journal_warning is text:
    size 24
    color "#d08a7a"
    font "gui/vendor/fonts/SourceSans3-Semibold.ttf"
