import logging
from typing import Dict, List, Tuple

import backoff
import elasticsearch
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor, execute_values
from pydantic.error_wrappers import ValidationError
from urllib3.exceptions import NewConnectionError

from models import ElasticSettings, PostgresSettings

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def backoff_hdlr(details):
    logger.error(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, (psycopg2.Error, psycopg2.OperationalError), on_backoff=backoff_hdlr)
def load_postges(postgres_settings: dict) -> psycopg2.extensions.connection:
    pg_conn = psycopg2.connect(**postgres_settings, cursor_factory=DictCursor)
    return pg_conn


@backoff.on_exception(backoff.expo, (ValueError, NewConnectionError), on_backoff=backoff_hdlr)
def load_elastic(host: str) -> elasticsearch.client.Elasticsearch:
    es: elasticsearch.client.Elasticsearch = elasticsearch.Elasticsearch(host, verify_certs=True)
    if not es.ping():
        raise ValueError("Connection failed")
    return es


def main():
    try:
        postgres_settings = PostgresSettings().dict()
        elastic_settings = ElasticSettings()
        logger.info((postgres_settings, elastic_settings))
    except ValidationError as e:
        logger.error("Could load settings from enviromentals or .env")
        raise SystemExit
    pg_conn: psycopg2.extensions.connection = load_postges(postgres_settings)
    es: elasticsearch.client.Elasticsearch = load_elastic(elastic_settings.host)
    pg_conn.close()


if __name__ == "__main__":
    main()
