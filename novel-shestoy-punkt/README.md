# «Шестой пункт»

Вторая книга цикла «Материальный вопрос». Мир первой книги, новые герои. Косметолог из Верхнегорска читает открытое пособие по перестройке вещества и нарушает его шестой пункт — «живое не трогать», — начиная с собственного тела. Городское фэнтези с триллером, 18+.

## Документы

- [00-plan.md](00-plan.md) — замысел, мир через полтора года после пособия, правила магии для живого, персонажи, поглавный план.
- [REVIEW.md](REVIEW.md) — чек-лист ревью главы отдельным агентом.
- Главы — в `chapters/`.

## Озвучка и YouTube

Как у первой книги, только голос женский (Silero `xenia`) и свой плейлист «Шестой пункт — аудиокнига» на том же канале:

```bash
pip install silero omegaconf torch pillow google-api-python-client google-auth-oauthlib   # и ffmpeg с libass
python novel-shestoy-punkt/tools/make_media.py --chapter 01-stakan-vody
python novel-shestoy-punkt/tools/upload_youtube.py --all            # первый раз: --login
```

Файлы глав (`.mp3`, `.srt`, `.png`, `.mp4`) ложатся в `media/`; `*.uploaded.json` и `playlist.json` нужно закоммитить, чтобы главы не загружались повторно.
