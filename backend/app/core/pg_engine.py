from typing import Annotated, Any

import psycopg2
import psycopg2.extras
from loguru import logger
from pydantic import BaseModel, Field

from .config import settings

POSTGRES_DB: str = settings.POSTGRES_DB
POSTGRES_USER: str = settings.POSTGRES_USER
POSTGRES_PASSWORD: str = settings.POSTGRES_PASSWORD
POSTGRES_SERVER: str = settings.POSTGRES_SERVER
POSTGRES_PORT: int = settings.POSTGRES_PORT
CONNECTION = None
CURSOR = None


class PsqlEngine(BaseModel):
    dbname: Annotated[str, Field(default=POSTGRES_DB)]
    user: Annotated[str, Field(default=POSTGRES_USER)]
    password: Annotated[str, Field(default=POSTGRES_PASSWORD)]
    host: Annotated[str, Field(default=POSTGRES_SERVER)]
    port: Annotated[int, Field(default=POSTGRES_PORT)]
    conn: Annotated[int, Field(default=CONNECTION)]
    cursor: Annotated[int, Field(default=CURSOR)]

    def model_post_init(self, context: Any):
        self.connect_db()

    def connect_db(self):
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        self.conn.set_session(autocommit=False)
        return self

    def re_connect(self):
        self.connect_db()

    def execute_cmd(
        self, stmt: str, cursor_factory=psycopg2.extras.NamedTupleCursor
    ) -> None:
        try:
            if not self.conn:
                self.re_connect()
            if not self.cursor:
                self.cursor = self.conn.cursor(cursor_factory=cursor_factory)
            self.cursor.execute(stmt)
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            logger.error(f"Error sql statement: {stmt}")
            self.conn.rollback()
        finally:
            self.close_connect()

    def execute_query(
        self,
        stmt: str,
        cursor_factory=psycopg2.extras.NamedTupleCursor,
        first: bool = False,
    ) -> list[Any]:
        try:
            if not self.conn:
                self.re_connect()
            if not self.cursor:
                self.cursor = self.conn.cursor(cursor_factory=cursor_factory)
            self.cursor.execute(stmt)
            result = self.cursor.fetchall()
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            logger.error(f"Error sql statement: {stmt}")
            self.conn.rollback()
        finally:
            self.close_connect()
        return result[0] if first and result else result

    def insert_mogrify(self, table_name: str, values: list[tuple[Any, ...]]) -> None:
        try:
            if not self.conn:
                self.re_connect()
            if not self.cursor:
                self.cursor = self.conn.cursor()
            placeholders = ",".join(["%s"] * len(values[0]))
            args_str = ",".join(
                self.cursor.mogrify(f"({placeholders})", value).decode("utf-8")
                for value in values
            )
            self.cursor.execute(f"insert into {table_name} values {args_str};")
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            logger.error(
                f"Error sql statement: insert into {table_name} values {args_str};"
            )
            self.conn.rollback()
        finally:
            self.close_connect()

    def close_connect(self) -> None:
        try:
            self.cursor.close()
            self.conn.close()
            self.cursor = None
            self.conn = None
        except Exception as e:
            logger.error(e)
