# «Шестой пункт»

Вторая книга цикла «Материальный вопрос». Мир первой книги, новые герои. Косметолог из Верхнегорска читает открытое пособие по перестройке вещества и нарушает его шестой пункт — «живое не трогать», — начиная с собственного тела. Городское фэнтези с триллером, 18+.

## Документы

- [00-plan.md](00-plan.md) — замысел, мир через полтора года после пособия, правила магии для живого, персонажи, поглавный план.
- [REVIEW.md](REVIEW.md) — чек-лист ревью главы отдельным агентом.
- Главы — в `chapters/`.

## Озвучка и YouTube

Голос — Microsoft Edge `ru-RU-SvetlanaNeural` через `edge-tts`, как у книги по экономике (нужен интернет; при ошибке 403 обновить пакет: `pip install -U edge-tts`). Офлайн-запасные варианты: `--engine silero` (голос `xenia`) и `--engine rhvoice`. Свой плейлист «Шестой пункт — аудиокнига» на том же канале:

```bash
pip install edge-tts pillow google-api-python-client google-auth-oauthlib   # и ffmpeg
python tools/shestoy/make_media.py --chapter 01-stakan-vody
python tools/shestoy/upload_youtube.py --all            # первый раз: --login
```

Файлы глав (`.mp3`, `.srt`, `.png`, `.mp4`) ложатся в `media/`; `*.uploaded.json` и `playlist.json` нужно закоммитить, чтобы главы не загружались повторно.
