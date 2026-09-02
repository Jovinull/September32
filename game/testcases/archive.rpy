# The Archive Document Viewer, driven the way a player drives it.
#
# These assert on engine state, not on what the screen looks like. The Python
# suite covers the document model; what only Ren'Py can prove is that the screen
# opens, pages, closes, and that a first reading applies its effects once when it
# goes through the real UI rather than a function call in a test.
#
# Syntax reminder: conditions are `eval <expr>` and comparisons need
# parentheses. `assert eval (x >= 1)`, never `assert x >= 1`.

testcase archive_opens_and_closes:
    # The teaching document. It has no effects, so this tests the interface and
    # nothing else — which is exactly what it is for.
    $ _test.transition_timeout = 0.05

    $ persistent.s32_playtest_consent = False
    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."

    advance until screen "choice"
    click "Seems straightforward."

    # archive_intro opens the accession record partway through.
    advance until screen "s32_document" timeout 40.0

    assert eval (renpy.get_screen("s32_document") is not None)

    click "Close"
    pause 0.5

    assert eval (renpy.get_screen("s32_document") is None)

    exit


testcase archive_pages_with_the_keyboard:
    # The ledger is the two-page document. Paging is keyboard-first: a player
    # should never need the mouse to read something.
    $ _test.transition_timeout = 0.05

    $ persistent.s32_playtest_consent = False
    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."
    advance until screen "choice"
    click "Seems straightforward."

    # Through the accession record.
    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.4

    # ... and on to the photograph.
    # The week loop offers a travel menu at the turn of the afternoon and the
    # evening, and where the clock lands after archive_intro depends on the
    # scene. Staying put keeps this test about the viewer.
    advance until screen "choice" timeout 40.0
    if "Stay where you are.":
        click "Stay where you are."
        advance until screen "choice" timeout 40.0
    click "Put it in the maybe pile."

    advance until screen "s32_document" timeout 40.0

    assert eval (len(S32State["documents_read"]) >= 2)

    keysym "K_RIGHT"
    pause 0.3
    keysym "K_LEFT"
    pause 0.3

    keysym "K_ESCAPE"
    pause 0.5

    assert eval (renpy.get_screen("s32_document") is None)

    exit


testcase archive_effects_apply_once:
    # The requirement that made a document model necessary at all: reading a
    # document twice must not grant its effects twice.
    $ _test.transition_timeout = 0.05

    $ persistent.s32_playtest_consent = False
    click "Start"
    pause 1.0

    advance until screen "choice"
    click "How do you know about the archive job?"
    advance until screen "choice"
    click "What happens if something isn't labelled?"

    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.4

    assert eval ("accession_record_box_17" in S32State["documents_read"])

    # Re-open the same document from the archive index and confirm the read
    # list does not grow.
    run ShowMenu("s32_archive_index")
    pause 0.8

    click "Accession record"
    pause 0.8

    assert eval (S32State["documents_read"].count("accession_record_box_17") == 1)

    keysym "K_ESCAPE"
    pause 0.5
    click "Return"
    pause 0.4

    exit


testcase archive_index_hides_locked_documents:
    # A locked document must not be openable from the index. The photograph card
    # needs the photograph; at the start of a run the player has nothing.
    $ _test.transition_timeout = 0.05

    $ persistent.s32_playtest_consent = False
    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."
    advance until screen "choice"
    click "Seems straightforward."

    run ShowMenu("s32_archive_index")
    pause 0.8

    # The accession record is unlocked by arriving; the other two are not.
    assert eval (len(s32_readable_documents()) == 1)
    assert eval (s32_readable_documents()[0].id == "accession_record_box_17")

    click "Return"
    pause 0.4

    exit


testcase archive_survives_rollback:
    # Reading a document is a state change like any other, so rolling back past
    # it must unwind it — including the knowledge it granted.
    $ _test.transition_timeout = 0.05

    $ persistent.s32_playtest_consent = False
    click "Start"
    pause 1.0

    advance until screen "choice"
    click "Thanks. Lead on."
    advance until screen "choice"
    click "Seems straightforward."

    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.5

    assert eval (len(S32State["documents_read"]) >= 1)

    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.4
    run Rollback()
    pause 0.5

    assert eval (len(S32State["documents_read"]) == 0)

    exit
