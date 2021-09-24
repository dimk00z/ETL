import atexit
import logging
from datetime import datetime
from os import environ
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
from transformer import Transformer

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)
load_dotenv()


def start_etl(pg_conn, es):
    postgres_extractor: PostgresExtractor = PostgresExtractor(pg_conn=pg_conn, cursor_limit=300)

    es_loader = ESLoader(es)
    if environ.get("ES_SHOULD_DROP_INDEX") == "TRUE":
        es_loader.drop_index()
    es_loader.create_index()
    # загрузка данных с ипользованием генератора
    for extracted_movies in postgres_extractor.extract_data():
        transformer = Transformer(extracted_movies=extracted_movies)
        transformed_movies: List[dict] = transformer.transform_movies()
        es_loader.bulk_index(transformed_data=transformed_movies)
        logging.info(f"Loaded {len(extracted_movies)} movies to Elasticsearch")
        # break


def main():
    postgres_settings, elastic_settings, redis_settings = load_etl_settings()
    pg_conn: psycopg2.extensions.connection = connect_to_postges(postgres_settings.dict())
    es: elasticsearch.client.Elasticsearch = connect_to_elastic(elastic_settings.host)
    redis_adapter: Redis = connect_to_redis(redis_settings.dict())
    atexit.register(close_pg_conn, pg_conn=pg_conn)
    while True:
        logging.info(f"Start etl_app at {datetime.now()}")
        start_etl(pg_conn=pg_conn, es=es)
        break


if __name__ == "__main__":
    main()
