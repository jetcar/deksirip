# Локальная озвучка книги

## Быстрый старт

```powershell
python tools/book/setup_local_voice.py
python tools/book/local_voice.py doctor
```

Установщик использует Python 3.12, кладёт xVibePocketTTS и его `.venv` в `.voice/`, затем ставит в это окружение `rusvoice[accent,ui]`, Kokoro и `deckrun-mcp`.

Русская озвучка создаётся через xVibePocketTTS, английская — через нативный Kokoro без русского акцента.

## Команды

```powershell
# Просмотреть текст после нормализации и расстановки ударений
python tools/book/local_voice.py explain --text "Ст+арый з+амок закрыт на зам+ок."

# Markdown очищается перед синтезом; рядом создаётся *.prepared.txt
python tools/book/local_voice.py synthesize `
  --text-file book/01-hunter-gatherers.md `
  --output book/audio/local/01-hunter-gatherers.wav

# Английская женская озвучка; по умолчанию используется af_heart
python tools/book/local_voice.py synthesize `
  --lang en `
  --voice af_heart `
  --text-file book/chapters-en/00-intro.md `
  --output book/audio-en/00-intro-kokoro.wav

# Один или несколько PNG/JPG превращаются в MP4 с локальной дорожкой
python tools/book/local_voice.py video `
  --audio book/audio/local/01-hunter-gatherers.wav `
  --image book/images/slide-01.png `
  --image book/images/slide-02.png `
  --output book/video/01-hunter-gatherers-local.mp4
```

Для омографов ставить `+` перед ударной гласной: `п+исать` и `пис+ать`. `synthesize` сначала вызывает слой rusvoice и передаёт результат в xVibe с отключённой повторной акцентуацией.

## Deckrun

Проектный `.codex/config.toml` запускает локальный stdio-сервер из окружения xVibe. `doctor` проверяет список MCP-инструментов и вызывает `get_slide_format`.

Локальный stdio-процесс Deckrun всё равно обращается к сервису Deckrun для схемы и PDF-рендера. Без ключа доступны `get_slide_format` и `generate_slide_deck`; локальное видео собирается командой `video` через FFmpeg.

`deckrun-mcp 1.1.1` использует API MCP 1.x, поэтому установщик закрепляет `mcp<2`.

После первой загрузки моделей xVibe можно работать офлайн:

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
python tools/book/local_voice.py synthesize --text "Пров+ерка." --output test.wav
```

## TikTok Shorts

```powershell
python tools/book/make_tiktok.py --lang ru --id 44
python tools/book/make_tiktok.py --lang en --id 11
```

Скрипт создаёт отдельную TikTok-версию с озвучкой, полноэкранным видеорядом, встроенными субтитрами, SRT и манифестом проверки в `book/shorts[-en]/out/tiktok/`.
