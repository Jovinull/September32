# Synthetic playtest reports

**Nothing here came from a person.** Every file is generated, every session code
contains `SYNTH`, and every file carries a `note` field saying so.

They exist so that `s32 playtest summarize`, the privacy check and the schema
validator can be tested without waiting for a wave — and so that a change to the
report format has something concrete to break against.

Real feedback goes in `playtests/raw/`, which is gitignored. If a file in this
directory ever stops saying `SYNTHETIC`, something has gone badly wrong.

Regenerate with the script recorded in
[`../../../docs/playtest/PLAYTEST_DATA.md`](../../../docs/playtest/PLAYTEST_DATA.md).
