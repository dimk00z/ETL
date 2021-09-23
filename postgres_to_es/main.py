import atexit
import logging
from datetime import datetime
from typing import Dict, List, Tuple

import elasticsearch
import psycopg2
from redis import Redis

from connections import (
    close_pg_conn,
    connect_to_elastic,
    connect_to_postges,
    connect_to_redis,
)
from extractor import PostgresExtractor
from setting_loaders import load_etl_settings

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def load():
    pass


def start_etl(pg_conn, es):
    postgres_extractor: PostgresExtractor = PostgresExtractor(pg_conn=pg_conn)
    i = 0
    # with generator
    for extracted_movies in postgres_extractor.extract_data():
        print(len(extracted_movies))
        i += 1

    # transformer = transform(loader, Transformer())

    # extractor = extract(transformer, PostgresExtractor(pg_conn))

    # etl(extractor)


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
