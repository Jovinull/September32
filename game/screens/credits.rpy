# The in-game credits screen.
#
# Presentation lives here; content comes from game/credits_data.rpy, which is
# generated from assets/catalog/assets.toml. That split is deliberate: a
# designer can rework this screen freely without any risk of dropping an
# attribution, and adding an asset can never mean forgetting to update a screen.

screen s32_credits():

    tag menu

    add "#141210"

    frame:
        style "s32_credits_frame"

        vbox:
            spacing 24

            label _("Credits") style "s32_credits_heading"

            side "c r":
                area (0, 0, 1180, 720)

                viewport id "s32_credits_vp":
                    mousewheel True
                    draggable True

                    vbox:
                        spacing 30

                        for section, entries in s32_credits_sections:

                            vbox:
                                spacing 8
                                text section style "s32_credits_section"

                                for line, sub in entries:
                                    vbox:
                                        spacing 2
                                        text line style "s32_credits_line"
                                        text sub style "s32_credits_sub"

                        null height 12

                        text s32_credits_footer style "s32_credits_sub"

                vbar style "vscrollbar"

    textbutton _("Return"):
        style "return_button"
        action Return()


style s32_credits_frame is empty:
    xalign 0.5
    yalign 0.5
    xsize 1280
    ysize 880
    padding (48, 40)
    background "#1c1a1690"


style s32_credits_heading is text:
    size 54
    color "#e8e2d4"
    font S32_SERIF_SEMIBOLD


style s32_credits_section is text:
    size 28
    color "#d8b978"
    font S32_SANS_SEMIBOLD


style s32_credits_line is text:
    size 22
    color "#ddd6c6"
    font S32_SANS


style s32_credits_sub is text:
    size 18
    color "#8f887a"
    font S32_SANS
