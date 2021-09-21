from pydantic import BaseSettings, Field


class PostgresSettings(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="DB_HOST")
    port: str = Field(..., env="DB_PORT")
    options: str = "-c search_path=content"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
