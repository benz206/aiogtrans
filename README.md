# aiogtrans

aiogtrans is a **free** and **unlimited** python library that implements the Google Translate API asynchronously. This uses the [Google Translate Ajax API](https://translate.google.com) and [httpx](https://www.python-httpx.org) to make api calls.

Compatible with Python 3.10+.

## Features

-  Fast and semi-reliable
	- Uses the same api that google translate uses
	- Reverse Engineered
-  Auto language detection
-  Bulk translations with bounded concurrency
-  Optional in-memory LRU cache
-  Automatic retries on network errors and 429/5xx responses
-  Customizable service URL
-  HTTP/2 support
-  Fully typed (ships `py.typed`)

## HTTP/2 support

HTTP/2 is enabled by default. You can check the protocol used through the `.response.http_version` of a `Translated` or `Detected` object:

```py
>>> (await translator.translate('테스트')).response.http_version
# 'HTTP/2'
```

### How does this library work?

The translate.google.com web app talks to Google through an internal RPC endpoint (`/_/TranslateWebserverUi/data/batchexecute`). This library sends the same requests the web app does and parses the response. Since this is an undocumented API, Google could change or block it at any time.

### Why not use googletrans?

It seems [Suhun Han](https://github.com/ssut) has abandoned the project, at the time of this writing it's been nearly a year and a half since the last commit.

I have decided to move on and update this project.

## Installation

```bash
$ pip install aiogtrans
```

## Basic Usage

If a source language is not given, google translate attempts to detect the source language. Use the translator as an async context manager so the underlying HTTP client is closed.

```python
>>> from aiogtrans import Translator
>>> async with Translator() as translator:
...     await translator.translate('안녕하세요.')
...     await translator.translate('안녕하세요.', dest='ja')
...     await translator.translate('veritas lux mea', src='la')
# Translated(src='ko', dest='en', origin='안녕하세요.', text='hello.', pronunciation=None)
# Translated(src='ko', dest='ja', origin='안녕하세요.', text='こんにちは。', pronunciation=None)
# Translated(src='la', dest='en', origin='veritas lux mea', text='truth is my light', pronunciation=None)
```

Language names work as well as codes, e.g. `dest='japanese'`.

### Customize service URL

You can use another google translate domain for translation. If multiple URLs are provided, the program will randomly choose a domain.

```python
>>> from aiogtrans import Translator
>>> translator = Translator(service_urls=[
        'translate.google.com',
        'translate.google.co.kr',
    ])
```

### Bulk Translations

`translate_bulk` translates a list of strings concurrently over a single HTTP client. At most `concurrency` requests (default 10) are in flight at once.

```python
>>> translations = await translator.translate_bulk(['The quick brown fox', 'jumps over', 'the lazy dog'], dest='ko')
>>> for translation in translations:
...    print(translation.origin, ' -> ', translation.text)
# The quick brown fox  ->  민첩한 갈색여우
# jumps over  ->  뛰어넘다
# the lazy dog  ->  게으른 개
```

### Language Detection

The detect method, as its name implies, identifies the language used in a given sentence. Google no longer returns a confidence score, so `confidence` is `None`.

```python
>>> from aiogtrans import Translator
>>> async with Translator() as translator:
...     await translator.detect('이 문장은 한글로 쓰여졌습니다.')
...     await translator.detect('この文章は日本語で書かれました。')
# Detected(lang='ko', confidence=None)
# Detected(lang='ja', confidence=None)
```

### Caching, retries and errors

```python
>>> translator = Translator(
...     cache_capacity=1000,   # cache up to 1000 results in memory (0 disables, the default)
...     retries=3,             # attempts on network errors and 429/5xx responses
...     raise_exception=True,  # raise HTTPError on a non-200 response
... )
```

Failed requests raise `aiogtrans.TranslationError` (`HTTPError` is a subclass). Invalid language codes and text over 15,000 characters raise `ValueError`.

## aiogtrans as a command line application

```bash
$ aiogtrans -h
usage: aiogtrans [-h] [-d DEST] [-s SRC] [-c] text

Python Google Translator as a command-line tool

positional arguments:
  text                  The text you want to translate.

options:
  -h, --help            show this help message and exit
  -d DEST, --dest DEST  The destination language you want to translate.
                        (Default: en)
  -s SRC, --src SRC     The source language you want to translate. (Default:
                        auto)
  -c, --detect          Detect the language of the given text instead of
                        translating.

$ aiogtrans "veritas lux mea" -s la -d en
[la] veritas lux mea
    ->
[en] truth is my light
[pron.] None

$ aiogtrans -c "안녕하세요."
[ko, None] 안녕하세요.
```

`python -m aiogtrans` works as well.

## Note on Library Usage

**DISCLAIMER**: this is an unofficial library using the web API of translate.google.com and also is not associated with Google.

-  **The maximum character limit on a single text is 15,000.**

-  Due to limitations of the web version of google translate, this API does not guarantee that the library would work properly at all times (so please use this library if you don't care about stability).

-  **Important:** If you want to use a stable API, it is highly recommended that you use Google's official translate API [https://cloud.google.com/translate/docs](https://cloud.google.com/translate/docs).

-  If you get HTTP 5xx error or errors like #6, it's probably because Google has banned your client IP address.

## Contributing

Contributions are currently discouraged, I am writing this fork as a personal project and if I ever do decide to open up to contributions I will change this.

Of course you're more then welcome to fork this and make your own changes

## Development

```bash
$ uv sync              # create .venv with dev dependencies
$ uv run pytest        # tests
$ uv run ruff check .  # lint
$ uv run ruff format . # format
$ uv run mypy          # type check
```

## License

**aiogtrans** is licensed under the MIT License. The terms are as follows:

The MIT License (MIT)

Copyright (c) 2022 Ben Zhou 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
