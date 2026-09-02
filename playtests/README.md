# playtests/

Where feedback lands.

```
raw/          one directory per session code -- GITIGNORED
aggregate/    filled-in analysis templates, which may be committed
```

`raw/` holds what real people wrote: questionnaires, reports, bug reports, and
anything they said in a message. It is gitignored and nothing automated writes
to version control from here.

Nothing in this directory is sent to a language model by any tooling in this
repository. `s32 playtest summarize` counts and lists; it does not interpret.

Synthetic material for the test suite lives in `tests/fixtures/playtests/`, and
every file there is marked `SYNTHETIC`.

See [`docs/playtest/WAVE_1_PLAN.md`](../docs/playtest/WAVE_1_PLAN.md).
