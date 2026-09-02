# Playtest surfaces: the consent question, and the end of Act 1.
#
# Three screens and one label, and every one of them has the same constraint on
# it: a tester must be able to play this build without being told anything that
# would change what they notice. So none of these mentions a hypothesis, a
# system, a character to watch, or a number.
#
# In particular the completion screen shows no progress figures at all. A
# "scenes seen: 41 of 58" would turn a first playthrough into a checklist and
# would make the second one -- which is the one we do not want yet -- feel
# owed. docs/playtest/WAVE_1_PLAN.md.

init offset = -1


label s32_playtest_consent:
    # Asked once per installation, before the first line of the game, and
    # answered by the tester rather than by a default. `None` means not yet
    # asked, which is why it is a third state.

    if persistent.s32_playtest_consent is None:
        call screen s32_consent

    return


screen s32_consent():

    modal True
    zorder 100

    add "#0d0c0a"

    frame:
        style "s32_playtest_frame"

        vbox:
            spacing 26

            text _("Before you start") style "s32_playtest_heading"

            text _("This private test can save an anonymous gameplay report on your computer: which scenes you saw, which options you took, and roughly how long you played.") style "s32_playtest_body"

            text _("Nothing is uploaded, and nothing is sent anywhere. The file stays on your machine unless you decide to send it. It contains no name, no email address and nothing about your computer, and you can read it yourself before you send it.") style "s32_playtest_body"

            text _("Either answer is fine. The game is exactly the same.") style "s32_playtest_body"

            null height 10

            hbox:
                spacing 24

                textbutton _("Keep a report") action [Function(s32_set_consent, True), Return()] style "s32_playtest_button"

                textbutton _("Don't keep a report") action [Function(s32_set_consent, False), Return()] style "s32_playtest_button"


screen s32_act1_complete():

    modal True
    zorder 100

    add "#0d0c0a"

    frame:
        style "s32_playtest_frame"

        vbox:
            spacing 22

            text _("End of Act 1") style "s32_playtest_heading"

            text _("September 32 — Act 1 private playtest") style "s32_playtest_sub"

            text _("Thank you. This is where the story stops for now.") style "s32_playtest_body"

            text _("Please answer the questionnaire before you play again. What you thought the first time through is the part that cannot be recovered later.") style "s32_playtest_body"

            null height 6

            vbox:
                spacing 12

                if s32_recording():
                    textbutton _("Generate playtest report") action Function(s32_write_report_now) style "s32_playtest_button"

                textbutton _("Feedback instructions") action Show("s32_feedback_instructions") style "s32_playtest_button"

                textbutton _("Save") action ShowMenu("save") style "s32_playtest_button"

                textbutton _("Return to the main menu") action MainMenu(confirm=False) style "s32_playtest_button"

            if s32_report_message:
                null height 6
                text "[s32_report_message]" style "s32_playtest_note"


screen s32_feedback_instructions():

    modal True
    zorder 150

    add "#000000d0"

    frame:
        style "s32_playtest_frame"

        vbox:
            spacing 20

            text _("Sending feedback") style "s32_playtest_heading"

            text _("Your session code is:") style "s32_playtest_body"

            $ _s32_code = s32_session_code()
            text "[_s32_code]" style "s32_playtest_code"

            text _("Write that at the top of the questionnaire. It is how a report and a questionnaire get matched up, and it says nothing about you.") style "s32_playtest_body"

            if s32_recording():
                text _("If you generated a report, it is saved as playtest-report.json and playtest-summary.md in your save folder. Open the summary if you would like to see what it says before sending it.") style "s32_playtest_body"
            else:
                text _("You chose not to keep a report, which is fine. The questionnaire on its own is the more important half.") style "s32_playtest_body"

            text _("FEEDBACK_INSTRUCTIONS.md, next to the game, has the questionnaire and where to send it.") style "s32_playtest_body"

            null height 8

            textbutton _("Close") action Hide("s32_feedback_instructions") style "s32_playtest_button"


init python:

    # The last thing the report writer said, shown under the buttons. Not
    # game state: it describes a file operation, not the story.
    s32_report_message = ""

    def s32_write_report_now():
        """Write the report and put the result on screen."""
        global s32_report_message
        s32_report_message = s32_export_report()


style s32_playtest_frame is frame:
    xalign 0.5
    yalign 0.5
    xsize 1180
    padding (60, 48)
    background "#16130fe8"

style s32_playtest_heading is text:
    size 44
    color "#e8e2d4"
    font S32_SERIF

style s32_playtest_sub is text:
    size 24
    color "#a89d88"
    font S32_SANS

style s32_playtest_body is text:
    size 26
    color "#cfc8b8"
    line_spacing 6
    font S32_SANS

style s32_playtest_note is text:
    size 22
    color "#9fc48a"
    font S32_SANS

style s32_playtest_code is text:
    size 48
    color "#e8c98a"
    font S32_SANS_SEMIBOLD

style s32_playtest_button is button

style s32_playtest_button_text is text:
    size 26
    color "#cfc8b8"
    hover_color "#e8c98a"
    font S32_SANS
