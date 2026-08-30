# The journal and credits screens, opened from inside a run.
#
# They read a lot of engine state — beliefs, inventory, commitments,
# contradictions — which makes them an unusually good canary for a state-shape
# change that nothing else notices.

testcase smoke_journal:
    $ _test.transition_timeout = 0.05

    click "Start"
    pause 1.0

    advance until screen "choice"
    click "How do you know about the archive job?"

    advance until screen "choice"
    click "What happens if something isn't labelled?"

    # Play through to the photograph, so the journal has something in it rather
    # than three empty columns. `advance` cannot dismiss a choice screen, so the
    # menu is clicked explicitly; the priority chain makes this order reliable
    # (see smoke_director_runs).
    # archive_intro's accession record.
    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.4

    advance until screen "choice" timeout 40.0
    click "Put it in the maybe pile."

    # The photograph's catalogue card.
    advance until screen "s32_document" timeout 40.0
    click "Close"
    pause 0.4

    advance until eval (len(S32State.get("inventory", [])) >= 1) timeout 40.0

    run ShowMenu("s32_journal")
    pause 0.8

    assert eval (len(s32_journal_facts("known")) >= 1)
    assert eval (len(s32_journal_items()) >= 1)

    click "Return"
    pause 0.4

    exit
