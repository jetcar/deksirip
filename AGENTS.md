# Скрипты

Все скрипты — в `tools/<проект>/`, запуск из корня репозитория: `python tools/<проект>/<скрипт>.py`.
Секреты — в `tools/secrets/`. Новые скрипты — туда же. Правила: [tools/README.md](tools/README.md).

# YouTube Shorts

Перед созданием, изменением, сборкой или публикацией русских либо английских Shorts прочитай и выполни [book/shorts/PROMOTION.md](book/shorts/PROMOTION.md). Правила применяются к `book/shorts/`, `book/shorts-en/`, `tools/book/make_short.py`, `tools/book/make_short_en.py` и связанным задачам публикации. Если текущий шаблон не проходит обязательную схему и контроль качества, сначала исправь шаблон; не выпускай новый ролик по старой схеме.

Для TikTok дополнительно прочитай [book/shorts/TIKTOK.md](book/shorts/TIKTOK.md), по умолчанию анимируй утверждённые ключевые кадры локально через `tools/book/animate_wan22.py` и собирай RU/EN версии через `tools/book/make_tiktok.py --scene-folder`. Не публикуй в TikTok текстовую карточку из YouTube-шаблона.
