# Agency — local workflows on top of YuE

Local additions only. Everything here lives outside the upstream code and skill
directories (`src/`, `skills/`, `docs/`) so rebasing on the official repository
stays conflict-free.

## Layout

| Path | Purpose |
| --- | --- |
| `profiles/<artist>/profile.json` | Persistent artist/band identity: `style`, `version`, defaults |
| `profiles/<artist>/notes.md` | Sound card: identity, evolution history, variation log |
| `agency/generate_from_profile.py` | Compose a request from a profile; record the profile used; optionally run `run_yue2.py` |
| `agency/README.md` | This file: the local workflow |

## Generate using an artist profile

```bash
python agency/generate_from_profile.py kate-midnight \
  --lyrics-file my_lyrics.txt \
  --output outputs/kate-song
```

- `--prepare-only` writes `request.json` + `profile_record.json` and exits
  before any model run, so you can review the exact prompt.
- `--variation "dark jazz ballad, 72 BPM"` appends a per-song nuance to the
  base style without touching the profile.
- Every run directory ends up with `profile.json` + `profile_record.json`
  (artist, `profile_version`, `profile_sha256`, variation, request) next to
  the native `result.json` artifacts.
- Native request schema is untouched: the profile is a composer-time concept
  and never enters the pipeline request.

## Changing an artist's sound

1. Generate a baseline and keep the original output directory.
2. Update `style`/`identity` in `profile.json`, bump `version`, log the change
   in `notes.md` under History.
3. Do not mutate a profile mid-song: one version maps to one sound.

## Keeping up with the official repository

`main` mirrors `origin` (multimodal-art-projection/YuE) and is never committed
to directly. All local work happens on `artists`:

```bash
git fetch origin
git checkout main && git pull --ff-only
git checkout artists && git rebase origin/main
```

New local files live under `profiles/` and `agency/`; if upstream ever adds a
directory with the same name, resolve the merge explicitly and note it here.

## Remotes

| Remote | URL |
| --- | --- |
| `origin` | https://github.com/multimodal-art-projection/YuE.git |
| `fork` | https://github.com/simoneaveotti/YuE-artists.git |

Push local work with `git push fork artists`.