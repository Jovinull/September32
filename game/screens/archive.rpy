# The Archive Document Viewer.
#
# One of September 32's signature interfaces, and the reason the archive is a
# place rather than a plot device. A document should feel like an object you
# picked up, not a dialogue box with a border.
#
# Design constraints, from docs/style/VISUAL_DESIGN_SYSTEM.md:
#
#   Institutional, analogue, archival, slightly nostalgic, clean, restrained.
#   NOT: glitch, corruption, red error text, horror UI.
#
# At this phase the interface must be capable of feeling completely normal.
# That is what will make a later change to it worth anything.
#
# Text stays real Ren'Py text — never baked into an image. That keeps documents
# translatable (docs/production/LOCALIZATION.md) and readable at any size.
# The paper underneath is four small deterministic textures generated at build
# time by tools/s32tools/assets/paper.py.

init offset = -1

# Generated, committed, first-party. See tools/s32tools/assets/paper.py.
image doc_paper = "images/documents/doc_paper.png"
image doc_card = "images/documents/doc_card.png"
image doc_rules = "images/documents/doc_rules.png"
image doc_edge = "images/documents/doc_edge.png"


screen s32_document(document_id):
    ## One document, one page at a time.
    ##
    ## `page` is a screen-local variable rather than store state: which page you
    ## are on is not part of the story and has no business in a save file. What
    ## IS saved is whether the document has been read, which the engine owns.

    tag menu
    modal True
    zorder 100

    default page = 0

    $ _doc = s32_library_documents.documents[document_id]
    $ _page = _doc.pages[page]
    # A student notice is not archive paper: it came off a corkboard and should
    # not look like it was accessioned. The card stock is the mount a
    # photograph is fixed to.
    $ _stock = "doc_card" if _doc.type in ("photograph_card", "student_notice") else "doc_paper"

    add "#100e0c"

    ## Keyboard first, mouse second. Escape closes, arrows page. These are
    ## bound on the screen so they work without the mouse ever moving.
    key "game_menu" action Return()
    key "K_ESCAPE" action Return()
    key "K_LEFT" action If(page > 0, SetScreenVariable("page", page - 1))
    key "K_RIGHT" action If(page < _doc.page_count - 1, SetScreenVariable("page", page + 1))
    key "K_PAGEUP" action If(page > 0, SetScreenVariable("page", page - 1))
    key "K_PAGEDOWN" action If(page < _doc.page_count - 1, SetScreenVariable("page", page + 1))

    frame:
        style "s32_doc_sheet"
        background Fixed(
            Tile(_stock),
            Frame("doc_edge", 40, 40),
            xysize=(1100, 860),
        )

        if _doc.type == "ledger_page":
            add Tile("doc_rules") xysize (1100, 860) alpha 0.55

        vbox:
            spacing 4
            xsize 980

            ## The sheet's own header: what this object is, in the archive's
            ## words rather than the game's.
            hbox:
                xfill True
                text _doc.title style "s32_doc_title"
                if _doc.archive_reference:
                    text _doc.archive_reference style "s32_doc_reference"

            null height 10

            side "c r":
                area (0, 0, 980, 640)

                viewport id "s32_doc_body":
                    mousewheel True
                    draggable True
                    arrowkeys False

                    vbox:
                        spacing 10
                        xsize 940

                        for _block in _page.blocks:
                            use s32_document_block(_block)

                vbar style "vscrollbar"

    ## Chrome sits outside the sheet, so the paper is never covered by UI.
    hbox:
        xalign 0.5
        yalign 0.955
        spacing 24

        if _doc.page_count > 1:
            textbutton "‹" action If(page > 0, SetScreenVariable("page", page - 1)) style "s32_doc_button"
            $ _pager = "{} / {}".format(page + 1, _doc.page_count)
            text "[_pager]" style "s32_doc_meta" yalign 0.5
            textbutton "›" action If(page < _doc.page_count - 1, SetScreenVariable("page", page + 1)) style "s32_doc_button"

        textbutton _("Close") action Return() style "s32_doc_button"

    if _doc.fictional_source:
        text _doc.fictional_source style "s32_doc_meta" xalign 0.5 yalign 0.995


screen s32_document_block(block):
    ## One content block. Adding a kind means adding a branch here and a value
    ## to s32_engine.documents.BLOCK_KINDS — deliberately a small, visible cost,
    ## so the block vocabulary grows only when a document actually needs it.

    python:
        _kind = block.kind
        _text = block.text
        _label = block.label

    if _kind == "heading":
        text "[_text]" style "s32_doc_heading"

    elif _kind == "text":
        text "[_text]" style "s32_doc_body"

    elif _kind == "field":
        hbox:
            spacing 16
            text "[_label]" style "s32_doc_field_label" xsize 200
            text "[_text]" style "s32_doc_field_value"

    elif _kind == "date":
        if _text:
            text "[_text]" style "s32_doc_date"
        else:
            ## An empty date block is not a rendering failure. It is the
            ## document — a ruled, numbered column with nothing written above
            ## it. The space is the content, so it is given real height and no
            ## commentary whatsoever.
            null height 30

    elif _kind == "stamp":
        text "[_text]" style "s32_doc_stamp"

    elif _kind == "separator":
        add Solid("#2a27234a") xysize (940, 1) ypos 6

    elif _kind == "note":
        text "[_text]" style "s32_doc_note"

    elif _kind == "image_placeholder":
        ## Art that does not exist yet is visibly absent. Never a substitute,
        ## never a stand-in photograph of real people, never generated.
        ## docs/production/ART_GAP_ANALYSIS.md
        frame:
            xysize (620, 420)
            xalign 0.5
            background Solid("#00000012")
            text "[_text]" style "s32_doc_placeholder" xalign 0.5 yalign 0.5


init python:

    def s32_open_document(document_id):
        """Show a document, and record a first reading exactly once.

        The effects are applied BEFORE the screen is shown, so that rolling back
        past the viewing also rolls back what the player learned from it. They
        are declared in data/documents/<id>.json and applied by the engine, not
        by a screen action — a knowledge grant buried in a button would be
        invisible to the reachability tooling, which is a mistake this project
        has already made twice.
        """
        document = s32_library_documents.documents.get(document_id)
        if document is None:
            raise Exception("no such document: {}".format(document_id))

        if not s32_documents.is_unlocked(S32State, document, s32_rng()):
            s32_devlog.log("archive", "refused locked document: {}".format(document_id))
            return False

        changes = s32_documents.mark_read(S32State, document)
        if changes:
            s32_devlog.block("archive", "first reading of {}".format(document_id), changes)

        s32_pt_document(document_id)
        renpy.call_screen("s32_document", document_id=document_id)
        return True

    def s32_readable_documents():
        """Return the documents the player may currently open."""
        return s32_documents.readable(S32State, s32_library_documents, s32_rng())

    def s32_browse_document(document_id):
        """Open a document from a screen action, rather than from a scene.

        A screen action runs inside an interaction, and `renpy.call_screen`
        starts one — doing it directly raises "Cannot start an interaction in
        the middle of an interaction", which is what the archive index did on
        its first outing. A new context is the supported way in.
        """
        renpy.call_in_new_context("s32_view_document", document_id=document_id)


label s32_view_document(document_id):
    $ s32_open_document(document_id)
    return


screen s32_archive_index():
    ## The way back in. Everything the player has unlocked, reopenable at any
    ## time — an archive you can only consult when a scene offers it is not an
    ## archive.

    tag menu

    add "#141210"

    frame:
        style "s32_journal_frame"

        vbox:
            spacing 20

            label _("The archive") style "s32_journal_heading"

            $ _docs = s32_readable_documents()

            if _docs:
                text _("Items you have been able to look at properly.") style "s32_journal_muted"
                null height 6

                for _entry in _docs:
                    frame:
                        xfill True
                        padding (16, 12)
                        background "#00000030"

                        vbox:
                            spacing 4
                            $ _did = _entry.id
                            $ _dtitle = _entry.title
                            $ _dref = _entry.archive_reference or "not assigned"
                            $ _dread = "read" if s32_documents.has_read(S32State, _did) else "not yet read"

                            textbutton "[_dtitle]":
                                action Function(s32_browse_document, _did)
                                text_style "s32_journal_section"

                            text "[_dref]  ·  [_dread]" style "s32_journal_muted"
            else:
                text _("Nothing yet. Most of it is still in boxes.") style "s32_journal_muted"

    textbutton _("Return"):
        style "return_button"
        action Return()


style s32_doc_sheet is empty:
    xalign 0.5
    yalign 0.46
    xsize 1100
    ysize 860
    padding (60, 52)

style s32_doc_title is text:
    size 26
    color "#2a2723"
    font S32_SERIF_SEMIBOLD

style s32_doc_reference is text:
    size 18
    color "#6b6459"
    font S32_SANS
    xalign 1.0

style s32_doc_heading is text:
    size 30
    color "#2a2723"
    font S32_SERIF_SEMIBOLD

style s32_doc_body is text:
    size 22
    color "#332f2a"
    font S32_SERIF
    line_spacing 4

style s32_doc_field_label is text:
    size 18
    color "#6b6459"
    font S32_SANS

style s32_doc_field_value is text:
    size 21
    color "#2a2723"
    font S32_SERIF

style s32_doc_date is text:
    size 24
    color "#2a2723"
    font S32_SERIF_SEMIBOLD

style s32_doc_stamp is text:
    size 22
    color "#7a5c4a"
    font S32_SANS_SEMIBOLD

style s32_doc_note is text:
    size 20
    color "#4a5c6b"
    font S32_SERIF
    italic True

style s32_doc_placeholder is text:
    size 20
    color "#8f8878"
    font S32_SANS_SEMIBOLD
    text_align 0.5

style s32_doc_meta is text:
    size 18
    color "#8f887a"
    font S32_SANS

style s32_doc_button is button:
    padding (18, 8)

style s32_doc_button_text is text:
    size 22
    color "#cfc8b8"
    hover_color "#e8e2d4"
    font S32_SANS
