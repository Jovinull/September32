# Sending feedback

## The short version

1. Play to the end of Act 1.
2. Fill in the questionnaire that came with the build.
3. Send it back, with `playtest-report.json` attached if you kept one.

Please do that **before playing a second time**.

## Your session code

The end-of-act screen shows a code like `S32-KQ7MPB`. Write it at the top of the
questionnaire.

It exists so that a questionnaire and a report can be matched up without a name
attached to either. It is generated from a random number this installation made
up the first time you ran the game. It says nothing about you or your computer,
and if you reinstall you will get a different one.

You can also find it on the first line of `playtest-summary.md` in your save
folder.

## The report

If you agreed to keep one, click **Generate playtest report** on the end-of-act
screen. It writes two files into your save folder:

- `playtest-report.json` — the one to send
- `playtest-summary.md` — the same information, readable

**Please open the summary before you send anything.** It is short, it is in
plain English, and it is the only way to be sure of what you are handing over.
If anything in it looks like it should not be there, say so instead of sending
it: that is a bug in the game, and a serious one.

### Where the save folder is

The end-of-act screen prints the full path. If you would rather find it
yourself:

- **Windows** — `%APPDATA%\RenPy\September32-1`
- **Linux** — `~/.renpy/September32-1`

### What the report contains

Which scenes you saw and in what order, which options you took, which documents
you opened, whether you opened the calendar, which promises you made and whether
you kept them, how far through the week you got, and roughly how many seconds
the game was in front of you.

### What it does not contain

Your name. Your email address. Your username. Your computer's name. Any file
path. Your IP address. Any hardware identifier. The date or time you played.
Anything from outside this game.

The game refuses to write the file at all if any of those appear in it. That is
a check in the code, not a promise in a document.

### It is never uploaded

There is no network code in this game. No server, no account, no analytics, no
crash reporting. The file sits in your save folder until you decide to send it,
and if you never send it nobody will ever see it.

If you said no to the report, the game deleted it rather than merely stopping,
and the questionnaire alone is the more important half anyway.

## If something went wrong

Copy this and fill in what you can. Partial is fine.

```
Build version:        (the main menu shows it, bottom right)
What happened:

What you expected:

What you were doing:

Screenshot:           (optional)
Save file:            (optional)
Playtest report:      (optional)
```

If the game showed you a Ren'Py error screen, the text of it is the single most
useful thing you can send. `errors.txt` next to the game has the same text.

## Thank you

Genuinely. Reading something unfinished and then writing down what you thought
is a lot of work, and it is the only way this gets better.
