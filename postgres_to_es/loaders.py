import logging

import backoff
import elasticsearch
import psycopg2
from psycopg2.extras import DictCursor
from urllib3.exceptions import NewConnectionError


def backoff_hdlr(details):
    logging.error(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )


@backoff.on_exception(backoff.expo, (psycopg2.Error, psycopg2.OperationalError), on_backoff=backoff_hdlr)
def load_postges(postgres_settings: dict) -> psycopg2.extensions.connection:
    pg_conn: psycopg2.extensions.connection = psycopg2.connect(**postgres_settings, cursor_factory=DictCursor)
    return pg_conn


@backoff.on_exception(backoff.expo, (ValueError, NewConnectionError), on_backoff=backoff_hdlr)
def load_elastic(host: str) -> elasticsearch.client.Elasticsearch:
    es: elasticsearch.client.Elasticsearch = elasticsearch.Elasticsearch(host, verify_certs=True)
    if not es.ping():
        raise ValueError("Connection failed")
    return es


def close_pg_conn(pg_conn: psycopg2.extensions.connection):
    pg_conn.close()
    logging.info("Postgres connection has been closed correctly")
