# Решение проектной работы 3 спринта

## [Task 1](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/tasks/01_django.md)

Добавлена [первая версия api](https://github.com/dimk00z/Admin_panel_sprint_2/tree/main/movies_admin/api/v1), в которой реализованы выгрузка json в формате [django_openapi.yml](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/files/django_openapi.yml).
Вся логика прописана в [views.py](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/movies_admin/api/v1/views.py).
Queryset собирается по фильмам с prefetch_related по "persons", "film_genres". Использована агрегация по жанрам и ролям персон.

## [Task 2](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/tasks/02_docker.md), [Task 3](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/tasks/03_nginx.md)

Для развертывания проекта используется docker-compose.

Файл [docker-compose.yaml](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/docker-compose.yaml) содержит описание трех контейнеров проекта:

1. `postges_movie_db` - контейнер для развертывания postgres. В текущих настройках файлы базы данных связаны с путем `../postgres`

2. `movies_admin` - контейнер с бэкэндом django на основе [Dockerfile_django](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/Dockerfile_django). При развертывании в образ устанавливаются зависимости [production.txt](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/movies_admin/requirements/production.txt). Сервер работает через `gunicorn`.
3. `nginx` - контейнер с nginx веб-сервером на основе [Dockerfile_nginx](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/nginx/Dockerfile_nginx) для отдачи статики и проброса с movies_admin:8000.

## Запуск проекта

1. Для корректной работы в movies_admin необходим `.env` файл на основе [.env_example](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/movies_admin/.env_example).
2. `docker-compose up -d --build` - для построения и запуска контейнеров.
Предполагается, что первичные миграции проведены и в базе есть данные администратора.
3. Пример ссылок:

http://localhost/admin/

http://localhost/api/v1/movies/

http://localhost/api/v1/movies/00af52ec-9345-4d66-adbe-50eb917f463a/

4. `docker-compose down -v`

___


# Проектное задание: ETL

В предыдущем модуле вы реализовывали механизм для полнотекстового поиска. Теперь улучшим его: научим его работать с новой схемой и оптимизируем количество элементов для обновления.

## Подсказки

Перед тем как вы приступите к выполнению задания, дадим несколько подсказок:

1. Прежде чем выполнять задание, подумайте, сколько ETL-процессов вам нужно.
2. Для валидации конфига советуем использовать pydantic.
3. Для построения ETL-процесса используйте корутины.
4. Чтобы спокойно переживать падения Postgres или Elasticsearch, используйте решение с техникой `backoff` или попробуйте использовать одноимённую библиотеку.
5. Ваше приложение должно уметь восстанавливать контекст и начинать читать с того места, где оно закончило свою работу.
6. При конфигурировании ETL-процесса подумайте, какие параметры нужны для запуска приложения. Старайтесь оставлять в коде как можно меньше «магических» значений.
7. Желательно, но необязательно сделать составление запросов в БД максимально обобщённым, чтобы не пришлось постоянно дублировать код. При обобщении не забывайте о том, что все передаваемые значения в запросах должны экранироваться.
8. Использование тайпингов поможет сократить время дебага и повысить понимание кода ревьюерами, а значит работы будут проверяться быстрее :)
9. Обязательно пишите, что делают функции в коде.
10. Для логирования используйте модуль `logging` из стандартной библиотеки Python.

Желаем вам удачи в написании ETL! Вы обязательно справитесь 💪 

**Решение задачи залейте в папку `postgres_to_es` вашего репозитория.**


