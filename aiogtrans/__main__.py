#!/usr/bin/env python
from __future__ import annotations

import argparse
import asyncio
import sys

from aiogtrans import Translator


async def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Python Google Translator as a command-line tool"
    )
    parser.add_argument("text", help="The text you want to translate.")
    parser.add_argument(
        "-d",
        "--dest",
        default="en",
        help="The destination language you want to translate. (Default: en)",
    )
    parser.add_argument(
        "-s",
        "--src",
        default="auto",
        help="The source language you want to translate. (Default: auto)",
    )
    parser.add_argument(
        "-c",
        "--detect",
        action="store_true",
        default=False,
        help="Detect the language of the given text instead of translating.",
    )
    args = parser.parse_args()

    try:
        async with Translator() as translator:
            if args.detect:
                detected = await translator.detect(args.text)
                print(f"[{detected.lang}, {detected.confidence}] {args.text}")
            else:
                translated = await translator.translate(
                    args.text, dest=args.dest, src=args.src
                )
                print(
                    f"[{translated.src}] {translated.origin}\n"
                    f"    ->\n"
                    f"[{translated.dest}] {translated.text}\n"
                    f"[pron.] {translated.pronunciation}"
                )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Translation failed: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
