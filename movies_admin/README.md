# Техническое задание

Создать API, возвращающий список фильмов в формате, описанном в [openapi-файле 💾](/files/django_openapi.yml), и позволяющий получить информацию об одном фильме.

Проверить результат работы API можно при помощи Postman. Запустите сервер на `127.0.0.1:8000` и воспользуйтесь тестами [из файла 💾](/files/postman_tests.json).

# Решение 3 проектного задания

1. Проинициализирован проект Django `python manage.py startproject config .`
2. Перенесены настройки в `config\settings`  с разделением на настройки `dev.py` и `production.py`
3. Настройки БД подгружаются из .env/переменных окружения
4. Добавлено приложение movies `python manage.py startapp movies `
5. Прописаны модели данных `Genre, Person, FilmWork, GenreFilmWork, PersonFilmWork`
6. Добавлена миграция данных
7. Проинициализированы `Genre, Person, FilmWork` в администраторском интерфейсе

