import logging

from elasticsearch import helpers
from elasticsearch.client import Elasticsearch as ES_client


class ESLoader:
    def __init__(self, es: ES_client, data_for_loading: dict = {}, index_name: str = "movies") -> None:
        self.es = es
        self.index_name = index_name

    def create_index(self) -> None:

        index_exist: bool = False
        settings: dict = {
            "settings": {
                "refresh_interval": "1s",
                "analysis": {
                    "filter": {
                        "english_stop": {"type": "stop", "stopwords": "_english_"},
                        "english_stemmer": {"type": "stemmer", "language": "english"},
                        "english_possessive_stemmer": {"type": "stemmer", "language": "possessive_english"},
                        "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                        "russian_stemmer": {"type": "stemmer", "language": "russian"},
                    },
                    "analyzer": {
                        "ru_en": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                                "english_possessive_stemmer",
                                "russian_stop",
                                "russian_stemmer",
                            ],
                        }
                    },
                },
            },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "keyword"},
                    "imdb_rating": {"type": "float"},
                    "genre": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "ru_en", "fields": {"raw": {"type": "keyword"}}},
                    "description": {"type": "text", "analyzer": "ru_en"},
                    "director": {"type": "text", "analyzer": "ru_en"},
                    "actors_names": {"type": "text", "analyzer": "ru_en"},
                    "writers_names": {"type": "text", "analyzer": "ru_en"},
                    "actors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text", "analyzer": "ru_en"},
                        },
                    },
                    "writers": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text", "analyzer": "ru_en"},
                        },
                    },
                },
            },
        }
        try:
            check_index: bool = self.es.indices.exists(self.index_name)
            if not check_index:
                create_result: dict = self.es.indices.create(index=self.index_name, ignore=400, body=settings)
                if "error" in create_result:
                    raise elasticsearch.RequestError
                logging.info(create_result)
            else:
                logging.info(f"Index {self.index_name} already exists")
            index_exist = True
        except elasticsearch.RequestError:
            logging.error(create_result["error"])
        finally:
            self.created_index = index_exist
            return self.created_index

    def bulk_index(self, transformed_data: dict) -> None:
        try:
            response = helpers.bulk(self.es, body=transformed_data, index="employees")
            print("\nactions RESPONSE:", response)
        except Exception as e:
            print("\nERROR:", e)
