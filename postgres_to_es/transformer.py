from typing import List


class Transformer:
    def __init__(self, extracted_movies: dict) -> None:
        self.extracted_movies = extracted_movies

    def transform_movies(self) -> List[dict]:
        transformed_movies: List[dict] = []
        for film_id, film_work in self.extracted_movies.items():
            # print(film_id, film_work)
            transformed_movie = {
                "id": film_id,
                "imdb_rating": film_work.rating,
                "title": film_work.title,
                "description": film_work.description,
                "genre": [genre for genre in film_work.genres],
                "director": [director.full_name for director in film_work.directors],
            }
            if film_work.writers:
                transformed_movie["writers"] = [
                    {"id": writer.id, "name": writer.full_name} for writer in film_work.writers
                ]
            if film_work.actors:
                transformed_movie["actors"] = [
                    {"id": actor.id, "name": actor.full_name} for actor in film_work.actors
                ]
            transformed_movies.append(transformed_movie)

        # print(transformed_movies)
        return transformed_movies
