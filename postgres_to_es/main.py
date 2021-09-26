import logging
from datetime import datetime
from os import environ
from time import sleep
from typing import List

import elasticsearch
import psycopg2
from dotenv import load_dotenv
from redis import Redis

from connections import (
    close_pg_conn,
    connect_to_elastic,
    connect_to_postges,
    connect_to_redis,
)
from extractor import PostgresExtractor
from loader import ESLoader
from setting_loaders import load_etl_settings
from state import RedisStorage, State
from transformer import Transformer

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)
load_dotenv()


def start_etl(pg_conn, es_loader: ESLoader, state: State):

    last_state = state.get_state("last_updated_at")
    postgres_extractor: PostgresExtractor = PostgresExtractor(
        pg_conn=pg_conn,
        cursor_limit=int(environ.get("POSTGRES_PAGE_LIMIT")),
        last_state=last_state if last_state else "",
    )
    loaded_films_number: int = 0
    for extracted_movies in postgres_extractor.extract_data():

        transformer = Transformer(extracted_movies=extracted_movies)
        transformed_movies: List[dict] = transformer.transform_movies()
        es_loader.bulk_index(transformed_data=transformed_movies, last_state=last_state)

        loaded_films_number = len(extracted_movies)
        logging.info(f"Loaded {loaded_films_number} movies to Elasticsearch")

        last_updated_at = extracted_movies[-1].updated_at
        state.set_state("last_updated_at", last_updated_at)

    if loaded_films_number == 0:
        logging.info("There no films for ETL")


def create_es_index(elastic_settings):
    es: elasticsearch.client.Elasticsearch = connect_to_elastic(elastic_settings.host)
    es_loader = ESLoader(es=es, index_name=elastic_settings.index)
    es_loader.drop_index()
    es_loader.create_index()
    es.transport.close()


def main():
    logging.info(f"Start etl_app at {datetime.now()}")

    postgres_settings, elastic_settings, redis_settings = load_etl_settings()

    repeat_time = int(environ.get("REPEAT_TIME"))

    if environ.get("ES_SHOULD_DROP_INDEX") == "TRUE":
        create_es_index(elastic_settings)

    while True:
        pg_conn: psycopg2.extensions.connection = connect_to_postges(postgres_settings.dict())
        redis_adapter: Redis = connect_to_redis(redis_settings.dict())
        state = State(storage=RedisStorage(redis_adapter=redis_adapter, redis_db=environ.get("REDIS_DB")))
        es: elasticsearch.client.Elasticsearch = connect_to_elastic(elastic_settings.host)

        es_loader = ESLoader(es)

        start_etl(pg_conn=pg_conn, es_loader=es_loader, state=state)
        close_pg_conn(pg_conn=pg_conn)
        es.transport.close()
        logging.info(f"Script is waiting {repeat_time} seconds for restart")
        sleep(repeat_time)


if __name__ == "__main__":
    main()
