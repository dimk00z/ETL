# Проектное задание: ETL.

## Актуальное задание на третий спринт

[Актуальное задание](https://practicum.yandex.ru/learn/middle-python/courses/af061b15-1607-45f2-8d34-f88d4b21765a/sprints/5436/topics/c8fc5bcc-06bd-4098-acd2-306c2e3d8e82/lessons/b48733fd-637c-4f34-b1a1-25103549e4f3/) отличается от того, что указано в репозитории. В задании нет указания для использования корутин и асинхронности, поэтому в моем решении их нет. Так же не вижу смысла в текущем виде их применять.

Так же в [схеме](https://github.com/dimk00z/ETL/blob/main/tasks_files/es_schema.txt) предложены логические ошибки по записи жанров и режиссеров. Даны поля `genre` и `director`, хотя понятно, что там будут использованы множественные записи. Использовал `genres` и `directors`по аналогии с записями актеров и сценаристов.

# Решение проектного задания

## Состав проекта

Для развертывания проекта используется docker-compose.

Файл [docker-compose.yaml](https://github.com/dimk00z/ETL/blob/main/docker-compose.yaml) содержит описание трех образов проекта:

1. `postges_movie_db` - образ для развертывания postgres. В текущих настройках файлы базы данных связаны с путем `../postgres`

2. `movies_admin` - образ с бэкэндом django на основе [Dockerfile_django](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/Dockerfile_django). При развертывании в образ устанавливаются зависимости [production.txt](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/movies_admin/requirements/production.txt). Сервер работает через `gunicorn`.
3. `nginx` - образ с nginx веб-сервером на основе [Dockerfile_nginx](https://github.com/dimk00z/Admin_panel_sprint_2/blob/main/nginx/Dockerfile_nginx) для отдачи статики и проброса с movies_admin:8000.
4. `elasticsearch` - образ с Elasticsearch v.7.14.1 для хранения поисковых индексов
5. `redis` - Redis для хранения состояния
6. `postgres_to_es` - сервис для загрузки индексов из Postgres в Elasticsearch

## Описание ETL реализации

- `main.py` - основной скрипт для запуска ETL. Весь процесс предстваляет собой бесконечный цикл с задержкой выполнения `REPEAT_TIME` из переменных окружения;
  - `def main` - подгружает настройки для баз данных, и вызывает `start_etl`. По выполнению закрывает коннекты;
  - `def start_etl` - основная функция загрузки данных; 
- `connections.py` - содержит соединения с Postgres, ES, Redis. Все используют `backoff` для возможности переподключений;
- `state.py` - классы для сохранения состояний по аналогии с предложенными в теории;
- `extractor.py` - загружает данные из Postgres в лимитах `POSTGRES_PAGE_LIMIT` и отдает их в режиме генератора списком из dataclass. Данные подгружаются частями;
- `transformer.py` - преобразует в необходимый для Elascticseacrh вид;
- `loader.py` - создает индекс при необходимости, пишет в ES;
- `models.py` - описание dataclasses для удобства выгрузки и валидации;
- `setting_loaders.py` - подгружаются настройки для сервисов с использованием `pydantic`;
- [`signals.py`](https://github.com/dimk00z/ETL/blob/main/movies_admin/movies/signals.py) - прописал сигналы для обновления поля `updated_at` при изменении дополнительных таблиц.


## Запуск проекта

1. Для корректной работы необходим `.env` файл на основе `env_example`. Важно: если `ES_SHOULD_DROP_INDEX=TRUE`, то индекс и запись в redit сбросятся.
2. Предполагается, что по пути `../postgres` находятся данные из предыдущих двух спринтов: первичные миграции проведены, в базе есть данные администратора и выгружены данные из sqlite.
4. `docker-compose up -d --build` - для построения и запуска контейнеров.
5. [`http://localhost:9200/movies/_search`] - для проверки работы индекса
6. `docker-compose down -v` -  для удаления контейнеров

Лог выполнения  ETL скрипта:

```python main.py
INFO:root:Start etl_app at 2021-09-27 10:16:52.356840
INFO:elasticsearch:GET http://localhost:9200/ [status:200 request:0.003s]
INFO:elasticsearch:HEAD http://localhost:9200/ [status:200 request:0.002s]
INFO:elasticsearch:DELETE http://localhost:9200/movies [status:200 request:0.361s]
INFO:elasticsearch:PUT http://localhost:9200/movies [status:200 request:1.665s]
INFO:root:{'acknowledged': True, 'shards_acknowledged': True, 'index': 'movies'}
INFO:elasticsearch:GET http://localhost:9200/ [status:200 request:0.004s]
INFO:elasticsearch:HEAD http://localhost:9200/ [status:200 request:0.003s]
INFO:elasticsearch:POST http://localhost:9200/movies/_bulk?refresh=true [status:200 request:0.186s]
INFO:root:Loaded 300 movies to Elasticsearch
INFO:elasticsearch:POST http://localhost:9200/movies/_bulk?refresh=true [status:200 request:0.215s]
INFO:root:Loaded 300 movies to Elasticsearch
INFO:elasticsearch:POST http://localhost:9200/movies/_bulk?refresh=true [status:200 request:0.162s]
INFO:root:Loaded 300 movies to Elasticsearch
INFO:elasticsearch:POST http://localhost:9200/movies/_bulk?refresh=true [status:200 request:0.148s]
INFO:root:Loaded 99 movies to Elasticsearch
INFO:root:Postgres connection has been closed correctly
INFO:root:Script is waiting 60 seconds for restart
```

___


# Проектное задание: ETL (неатуальное)

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


