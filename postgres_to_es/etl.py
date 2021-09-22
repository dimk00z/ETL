import logging
from typing import Dict, List, Tuple

import elasticsearch
import psycopg2

from loaders import load_elastic, load_postges
from setting_loaders import load_etl_settings

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def main():
    postgres_settings, elastic_settings = load_etl_settings()
    pg_conn: psycopg2.extensions.connection = load_postges(postgres_settings.dict())

    es: elasticsearch.client.Elasticsearch = load_elastic(elastic_settings.host)

    pg_conn.close()


if __name__ == "__main__":
    main()
