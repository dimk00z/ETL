import logging
from os import environ
from typing import Dict, List, Tuple

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values
from models import PostgresSettings, ElasticSettings
from pydantic.error_wrappers import ValidationError

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)


def main():
    try:
        postgres_settings = PostgresSettings().dict()
        elastic_settings = ElasticSettings().dict()
        logger.info((postgres_settings, elastic_settings))
    except ValidationError as e:
        logger.error("Could load settings from enviromentals or .env")
        raise SystemExit

    try:
        with psycopg2.connect(
            **postgres_settings, cursor_factory=DictCursor
        ) as pg_conn:
            pass
    except (psycopg2.Error, psycopg2.OperationalError) as e:
        logger.error(e)
    finally:
        if "pg_conn" in locals():
            pg_conn.close()


if __name__ == "__main__":
    main()
