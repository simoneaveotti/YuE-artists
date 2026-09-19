#!/usr/bin/env python3
"""Compose a YuE2 request from an artist/band profile and optionally run it.

Reads <repo>/profiles/<artist>/profile.json, injects the persistent style
prompt into a fresh request, records exactly which profile produced it, and
optionally launches the official run_yue2.py helper on it.

The pipeline accepts only native request fields (style, lyrics, cot, seed, ...);
the profile reference is therefore recorded separately as profile_record.json
inside the output directory, never inside the request itself.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROFILES = REPO / "profiles"
RUN_YUE2 = REPO / "skills" / "yue2-music" / "scripts" / "run_yue2.py"

ALLOWED_REQUEST_FIELDS = {"style", "tags", "lyrics", "cot", "seed",
                          "abc", "abc_path", "cfg_scale", "id"}
PASSTHROUGH_ARGS = ("model", "vae", "revision", "vae_revision",
                    "offline", "device", "memory_budget_gib")


def load_profile(artist):
    path = PROFILES / artist / "profile.json"
    if not path.is_file():
        available = sorted(p.name for p in PROFILES.iterdir()
                           if (p / "profile.json").is_file())
        raise SystemExit(f"Unknown artist '{artist}'. Available: {', '.join(available) or 'none'}")
    profile = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict) or not isinstance(profile.get("style"), str):
        raise SystemExit(f"Bad profile {path}: need an object with a 'style' string")
    return path, profile


def read_lyrics(args):
    if args.lyrics and args.lyrics_file:
        raise SystemExit("Give either --lyrics or --lyrics-file, not both")
    if args.lyrics_file:
        return Path(args.lyrics_file).read_text(encoding="utf-8")
    if args.lyrics:
        return args.lyrics
    raise SystemExit("Provide lyrics with --lyrics or --lyrics-file")


def build_request(profile, artist, lyrics, args):
    defaults = profile.get("defaults", {})
    style = profile["style"]
    if args.variation:
        style = f"{style}, {args.variation}".strip()
    request = {
        "id": args.song_id or artist,
        "style": style,
        "lyrics": lyrics,
        "cot": args.cot or defaults.get("cot", "full"),
    }
    if args.cfg_scale is not None:
        request["cfg_scale"] = args.cfg_scale
    elif "cfg_scale" in defaults:
        request["cfg_scale"] = defaults["cfg_scale"]
    seed = args.seed if args.seed is not None else defaults.get("seed")
    if seed is not None:
        request["seed"] = seed
    return request


def profile_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_profile_record(directory, artist, profile, digest, request, variation):
    (directory / "profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record = {
        "artist": artist,
        "profile_version": profile.get("version"),
        "profile_sha256": digest,
        "variation": variation,
        "request": request,
    }
    (directory / "profile_record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def runner_args(args, request_file, output):
    command = [sys.executable, RUN_YUE2, "generate", "--request", request_file,
               "--output", output]
    for name in PASSTHROUGH_ARGS:
        value = getattr(args, name)
        if value is None and name in ("offline",):
            value = False
        if value is None or value is False:
            continue
        if isinstance(value, bool):
            command.append(f"--{name.replace('_', '-')}")
        else:
            command.append(f"--{name.replace('_', '-')}")
            command.append(str(value))
    return command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artist", nargs="?", help="Name of the profile directory under profiles/")
    parser.add_argument("--list", action="store_true", help="List available artist profiles and exit")
    parser.add_argument("--lyrics", help="Lyrics text with section tags such as [Verse]")
    parser.add_argument("--lyrics-file", type=Path)
    parser.add_argument("--variation", help="Per-song nuance appended to the profile style")
    parser.add_argument("--song-id", help="Overrides the request id (defaults to the artist name)")
    parser.add_argument("--cot", choices=("full", "melody", "off"))
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cfg-scale", type=float, dest="cfg_scale")
    parser.add_argument("--output", type=Path,
                        help="Fresh destination for the run (or, with --prepare-only, for the request files)")
    parser.add_argument("--prepare-only", action="store_true",
                        help="Write request.json + profile_record.json and exit without running the model")
    parser.add_argument("--offline", action="store_true")
    for name in PASSTHROUGH_ARGS:
        if name == "offline":
            continue
        parser.add_argument(f"--{name.replace('_', '-')}", dest=name)
    args = parser.parse_args()

    if args.list or args.artist is None:
        available = sorted(p.name for p in PROFILES.iterdir()
                           if (p / "profile.json").is_file())
        for artist in available or ["<none yet>"]:
            print(artist)
        return 0

    if args.output is None:
        raise SystemExit("--output is required unless --list is given")
    path, profile = load_profile(args.artist)
    lyrics = read_lyrics(args)
    request = build_request(profile, args.artist, lyrics, args)

    if args.prepare_only:
        output = args.output
        try:
            output.mkdir(parents=True)
        except FileExistsError:
            raise SystemExit(f"Destination already exists: {output}")
        (output / "request.json").write_text(
            json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_profile_record(output, args.artist, profile,
                             profile_sha256(path), request, args.variation)
        print(f"Prepared request in {output} (no model run)")
        return int(any(field not in ALLOWED_REQUEST_FIELDS for field in request))

    staging = args.output.with_name(args.output.name + ".request")
    staging.mkdir(parents=True)
    (staging / "request.json").write_text(
        json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    command = runner_args(args, staging / "request.json", args.output)
    print(" ".join(str(c) for c in command), flush=True)
    try:
        code = subprocess.call(command)
    except KeyboardInterrupt:
        code = 130
    if code == 0 and args.output.is_dir():
        write_profile_record(args.output, args.artist, profile,
                             profile_sha256(path), request, args.variation)
    return code


if __name__ == "__main__":
    sys.exit(main())