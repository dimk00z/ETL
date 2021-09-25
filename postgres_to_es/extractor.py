import logging
from typing import Dict

import psycopg2

from models import FilmWork, Person


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

    def fetch_persons(self, row: psycopg2.extras.DictRow, movie: FilmWork):
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
                genres=row["genres"],
            )
        for persons in ("directors", "actors", "writers"):
            if row[persons]:
                for person in row[persons]:
                    getattr(movies[movie_id], persons).add(
                        Person(id=person["id"], full_name=person["name"], role=persons[:-1])
                    )

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
            fw.type,
            fw.description,
            fw.rating as rating,
            fw.created_at, 
            fw.updated_at, 
            ARRAY_AGG(DISTINCT g.name) AS genres,
	        JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'director') AS directors,
            JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'actor') AS actors,
            JSON_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'writer') AS writers
            FROM content.film_work fw
            LEFT OUTER JOIN content.genre_film_work gfw ON fw.id = gfw.film_work_id
            LEFT OUTER JOIN content.genre g ON (gfw.genre_id = g.id)
            LEFT OUTER JOIN content.person_film_work pfw ON (fw.id = pfw.film_work_id)
            LEFT OUTER JOIN content.person p ON (pfw.person_id = p.id)
            WHERE fw.id IN ({})
            GROUP BY fw.id, fw.title, fw.description, fw.rating;
        """
        movies_id_cursor: psycopg2.extras.DictCursor = self.pg_conn.cursor(name="movies_id_cursor")
        movies_id_cursor.execute(movies_id_query)

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

            yield movies
