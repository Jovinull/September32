# The Calendar.
#
# September 32's second signature interface, and the sibling of the Archive
# Document Viewer. It shares that screen's paper, its typography and its
# restraint on purpose: both of them are pieces of institutional stationery, and
# they should read as coming out of the same building.
#
# Design constraints, from docs/style/VISUAL_DESIGN_SYSTEM.md:
#
#   Institutional, analogue, archival, slightly nostalgic, clean, restrained.
#   NOT: glitch, corruption, red error text, horror UI.
#
# It is a completely normal school calendar. That is the entire brief for this
# phase. Any unease here now would be spent before it is worth anything, and it
# would spend the *interface* rather than a scene, which is the one thing this
# screen will eventually be uniquely able to do.
#
# What it is NOT:
#
#   * Not a second source of truth. Everything comes from s32_engine.calendar,
#     which derives every value from WorldState, commitments and history at the
#     moment it is asked. There is no calendar state and there is no calendar in
#     the save file.
#   * Not a planner. The player cannot move a commitment; a promise is a thing
#     you made to a person, not a row you drag.
#   * Not omniscient. It shows what the protagonist knows -- where they have
#     been, and what they have promised. A scene scheduled for Thursday cannot
#     appear on Tuesday's square, because the future is not in scope for the
#     module that builds the view.
#
# Dates are labels. Nothing here parses one. See s32_engine/calendar.py.

init offset = -1


screen s32_calendar():
    ## The month, and one day at a time.
    ##
    ## `selected` is screen-local. Which square the player is looking at is not
    ## part of the story and has no business in a save.

    tag menu

    default selected = s32_calendar_today()

    $ _entries = s32_calendar_month()
    $ _month = s32_calendar_month_name()
    $ _entry = s32_calendar_entry(_entries, selected)

    add "#141210"

    ## Keyboard first. Arrows walk the grid a day and a week at a time, escape
    ## closes. Everything reachable with the mouse is reachable without it.
    key "game_menu" action Return()
    key "K_ESCAPE" action Return()
    key "K_LEFT" action SetScreenVariable("selected", s32_calendar_step(selected, -1))
    key "K_RIGHT" action SetScreenVariable("selected", s32_calendar_step(selected, 1))
    key "K_UP" action SetScreenVariable("selected", s32_calendar_step(selected, -7))
    key "K_DOWN" action SetScreenVariable("selected", s32_calendar_step(selected, 7))
    key "K_HOME" action SetScreenVariable("selected", s32_calendar_today())

    frame:
        style "s32_cal_sheet"
        background Fixed(
            Tile("doc_paper"),
            Frame("doc_edge", 40, 40),
            xysize=(1400, 900),
        )

        vbox:
            spacing 6
            xsize 1300

            hbox:
                xfill True
                text "[_month]" style "s32_cal_title"
                text _("Northfield School") style "s32_doc_reference"

            add Solid("#2a27234a") xysize (1300, 1) ypos 8

            null height 12

            hbox:
                spacing 28

                ## The grid.
                vbox:
                    spacing 6

                    ## Weekday headers. Localised, never baked into an image.
                    hbox:
                        spacing 6
                        for _name in s32_calendar_weekday_labels():
                            text "[_name]" style "s32_cal_weekday" xsize 116

                    for _row in s32_calendar_rows(_entries):
                        hbox:
                            spacing 6
                            for _cell in _row:
                                if _cell is None:
                                    null width 116 height 96
                                else:
                                    use s32_calendar_square(_cell, selected)

                ## The day panel. Sits beside the grid rather than over it, so
                ## the month never disappears while you are reading a day.
                vbox:
                    xsize 400
                    spacing 8

                    use s32_calendar_day_panel(_entry)

    hbox:
        xalign 0.5
        yalign 0.955
        spacing 24

        textbutton _("Today") action SetScreenVariable("selected", s32_calendar_today()) style "s32_doc_button"
        textbutton _("Close") action Return() style "s32_doc_button"

    ## Not decoration: the grid distinguishes days by tint and by a mark, and a
    ## mark is not enough on its own. This is the same information as a sentence.
    $ _read_out = s32_calendar_summary(_entry)
    text "[_read_out]" style "s32_doc_meta" xalign 0.5 yalign 0.995


screen s32_calendar_square(cell, selected):
    ## One day.
    ##
    ## Three states, and each is carried by a word or a mark as well as by a
    ## tint, because a player who cannot separate the tints must still be able
    ## to separate the days.

    python:
        _day = cell["calendar_day"]
        _is_selected = _day == selected
        _state = cell["state"]
        _promised = len(cell["commitments"])
        _recorded = len(cell["events"])
        _label = s32_calendar_summary(cell)

    button:
        xysize (116, 96)
        action SetScreenVariable("selected", _day)
        alternate NullAction()
        tooltip _label
        background (
            "#2a272326" if _is_selected
            else ("#00000014" if _state == "past" else None)
        )

        vbox:
            spacing 2
            xoffset 10
            yoffset 8

            hbox:
                spacing 6
                text "[_day]" style ("s32_cal_day_today" if _state == "today" else "s32_cal_day")
                if _state == "today":
                    ## The word, not only the ring around it.
                    text _("today") style "s32_cal_mark" yoffset 8

            if _promised:
                text _("promised") style "s32_cal_mark"
            if _recorded:
                $ _n = _recorded
                text _("· [_n]") style "s32_cal_mark"


screen s32_calendar_day_panel(entry):
    ## What the protagonist knows about one day. Nothing else goes here.

    python:
        _weekday = entry["weekday"]
        _daynum = entry["calendar_day"]
        _state = entry["state"]

    vbox:
        spacing 6

        text "[_weekday] [_daynum]" style "s32_cal_panel_heading"

        if _state == "future":
            text _("Not yet.") style "s32_doc_meta"
        elif _state == "today":
            text _("Today.") style "s32_doc_meta"

        null height 8

        if entry["commitments"]:
            text _("You said you would") style "s32_cal_panel_label"
            for _cid in entry["commitments"]:
                $ _line = s32_calendar_commitment_line(_cid)
                text "[_line]" style "s32_doc_body"
            null height 10

        if entry["events"]:
            text _("What you did") style "s32_cal_panel_label"
            for _title in entry["events"]:
                text "[_title]" style "s32_doc_body"
        elif _state == "past":
            text _("Nothing you wrote down.") style "s32_doc_meta"
        elif _state == "future" and not entry["commitments"]:
            text _("Nothing arranged.") style "s32_doc_meta"


init python:

    def s32_calendar_today():
        """Return the calendar day the run is on."""
        return S32State["world"]["calendar_day"]

    def s32_calendar_month_name():
        """Return the month, as authored. Never computed from a date."""
        return S32State["world"]["month"]

    def s32_calendar_weekday_labels():
        """Return the weekday headers, localised.

        Translated here rather than in the engine: `s32_engine` is imported by
        the headless tooling, which has no `_()` and no business having one.
        """
        return [__(name) for name in s32_calendar_module.WEEKDAYS]

    def s32_calendar_month():
        """Return one entry per day of the month.

        Storylet titles are passed in rather than looked up inside the engine
        module, which is what keeps the calendar unable to see content the
        player has not reached.
        """
        titles = {sid: s.title for sid, s in s32_library.storylets.items()}
        return s32_calendar_module.month_view(S32State, titles)

    def s32_calendar_entry(entries, calendar_day):
        """Return one entry by day number."""
        for entry in entries:
            if entry["calendar_day"] == calendar_day:
                return entry
        return entries[0]

    def s32_calendar_rows(entries):
        """Lay the month out in weeks, padded so the first day lands correctly.

        Padding is `None`, and the screen renders `None` as empty space rather
        than as a day. A blank square is not day zero.
        """
        cells = [None] * s32_calendar_module.WEEKDAY_OFFSET + list(entries)
        while len(cells) % 7:
            cells.append(None)
        return [cells[i:i + 7] for i in range(0, len(cells), 7)]

    def s32_calendar_step(calendar_day, delta):
        """Move the selection, clamped to the month.

        Clamped rather than wrapping: a player holding the right arrow should
        stop at the end of the month, not reappear at the start of it.
        """
        return max(1, min(s32_calendar_module.MONTH_LENGTH, calendar_day + delta))

    def s32_calendar_summary(entry):
        """Return the one-line reading of a day, localised."""
        weekday = __(entry["weekday"])
        parts = ["{} {}".format(weekday, entry["calendar_day"])]
        if entry["state"] == "today":
            parts.append(__("today"))
        elif entry["state"] == "future":
            parts.append(__("not yet"))
        if entry["commitments"]:
            parts.append(__("something promised"))
        if entry["events"]:
            parts.append(__("something recorded"))
        return ", ".join(parts)

    def s32_calendar_commitment_line(commitment_id):
        """Render one open promise the way the protagonist would remember it.

        The participants come from the commitment record rather than from the
        content library, for the same reason the whole screen does: the record
        is what the protagonist agreed to, and the library is what the game
        intends.
        """
        for record in S32State["commitments"]:
            if record["id"] == commitment_id:
                who = ", ".join(
                    s32_library.characters[p].display_name
                    for p in record["participants"]
                    if p in s32_library.characters
                )
                return "{}{}".format(
                    commitment_id.replace("_", " "),
                    " — {}".format(who) if who else "",
                )
        return commitment_id.replace("_", " ")


style s32_cal_sheet is empty:
    xalign 0.5
    yalign 0.46
    xsize 1400
    ysize 900
    padding (50, 44)

style s32_cal_title is text:
    size 30
    color "#2a2723"
    font S32_SERIF_SEMIBOLD

style s32_cal_weekday is text:
    size 16
    color "#6b6459"
    font S32_SANS
    text_align 0.0

style s32_cal_day is text:
    size 24
    color "#332f2a"
    font S32_SERIF

style s32_cal_day_today is text:
    size 24
    color "#2a2723"
    font S32_SERIF_SEMIBOLD

style s32_cal_mark is text:
    size 14
    color "#6b6459"
    font S32_SANS

style s32_cal_panel_heading is text:
    size 26
    color "#2a2723"
    font S32_SERIF_SEMIBOLD

style s32_cal_panel_label is text:
    size 16
    color "#6b6459"
    font S32_SANS
