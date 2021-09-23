import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set

import psycopg2


@dataclass(frozen=True)
class Person:
    id: str
    full_name: str
    role: str


@dataclass
class FilmWork:
    title: str
    description: str = None
    rating: float = field(default=0.0)
    type: str = None
    created_at: datetime = None
    updated_at: datetime = None
    actors: Set[Person] = field(default_factory=set)
    directors: Set[Person] = field(default_factory=set)
    writers: Set[Person] = field(default_factory=set)
    genres: Set[str] = field(default_factory=set)


class PostgresExtractor:
    def __init__(
        self,
        pg_conn: psycopg2.extensions.connection,
        last_state: str = "",
        cursor_limit: int = 200,
    ) -> None:
        self.pg_conn = pg_conn
        self.last_state: str = last_state
        self.cursor_limit = cursor_limit

    def fetch_person(self, row: psycopg2.extras.DictRow, movie: FilmWork):
        try:
            roles_dict_name = f'{row["role"]}s'
            getattr(movie, roles_dict_name).add(
                Person(id=row["id"], full_name=row["full_name"], role=row["role"])
            )
        except AttributeError as e:
            logging.error(f"{e}, {row}")

    def fetch_movie_row(self, row: psycopg2.extras.DictRow, movies: Dict[str, FilmWork]):
        movie_id = row["fw_id"]
        if movie_id not in movies:
            movies[movie_id] = FilmWork(
                title=row["title"],
                description=row["description"],
                rating=row["rating"],
                type=row["type"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        if row["id"]:
            self.fetch_person(row=row, movie=movies[movie_id])
        if row["name"]:
            movies[movie_id].genres.add(row["name"])

    def extract_data(self) -> Dict[str, FilmWork]:
        movies_id_query: str = " ".join(
            [
                "SELECT id, updated_at",
                "FROM content.film_work",
                f"WHERE updated_at > '{self.last_state}'" if self.last_state else "",
                "ORDER BY updated_at;",
            ]
        )
        movies_info_query: str = """
            SELECT
            fw.id as fw_id, 
            fw.title, 
            fw.description, 
            fw.rating, 
            fw.type, 
            fw.created_at, 
            fw.updated_at, 
            pfw.role, 
            p.id, 
            p.full_name,
            g.name
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN ({});"""
        movies_id_cursor: psycopg2.extras.DictCursor = self.pg_conn.cursor(name="movies_id_cursor")
        movies_id_cursor.execute(movies_id_query)
        # movies: Dict[str, FilmWork] = {}
        # i = 0
        while data := movies_id_cursor.fetchmany(self.cursor_limit):
            movies: Dict[str, FilmWork] = {}
            movies_extented_data_cursor: psycopg2.extras.DictCursor = self.pg_conn.cursor(
                name="movies_extented_data_cursor"
            )
            movies_extented_data_query = movies_info_query.format(",".join((f"'{id}'" for id, _ in data)))
            movies_extented_data_cursor.execute(movies_extented_data_query)
            movies_extented_data = movies_extented_data_cursor.fetchall()

            for movie_row in movies_extented_data:
                self.fetch_movie_row(row=movie_row, movies=movies)
            movies_extented_data_cursor.close()
            # print(i)
            # i += 1
            yield movies
        # return movies
