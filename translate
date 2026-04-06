#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import asyncio
import sys

from aiogtrans import Translator


async def main() -> None:
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
                result = await translator.detect(args.text)
                print(f"[{result.lang}, {result.confidence}] {args.text}")
            else:
                result = await translator.translate(
                    args.text, dest=args.dest, src=args.src
                )
                print(
                    f"[{result.src}] {result.origin}\n"
                    f"    ->\n"
                    f"[{result.dest}] {result.text}\n"
                    f"[pron.] {result.pronunciation}"
                )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Translation failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
