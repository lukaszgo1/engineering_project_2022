import atexit
import contextlib
import itertools
from typing import Dict, Iterator, Optional, Sequence, Type

import mariadb
from typing_extensions import Self  # Python 3.11 adds native support

if True:  # remove when backend becomes a standalone app
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
import app_constants


class MariadbConnector:

    def __init__(
        self,
        host: str,
        user_name: str,
        password: str,
        port_number: int,
        db_name: Optional[str] = None
    ) -> None:
        self._con_obj = mariadb.Connection(
            user=user_name,
            password=password,
            host=host,
            port=port_number,
            database=db_name
        )
        atexit.register(self._close_con)

    def _close_con(self) -> None:
        self._con_obj.close()

    @contextlib.contextmanager
    def auto_committing_cursor(self) -> Iterator[mariadb.Cursor]:
        try:
            with contextlib.closing(
                self._con_obj.cursor(dictionary=True)
            ) as cursor:
                yield cursor
        finally:
            self._con_obj.commit()

    def execute_and_commit(self, statement: str, seq: Sequence[str] = tuple()):
        with self.auto_committing_cursor() as cursor:
            cursor.execute(statement, seq)

    def execute_statements(self, statements):
        for s in statements:
            self.execute_and_commit(s)

    def insert(
        self,
        table_name: str,
        col_names: Sequence[str],
        col_values: Sequence[str]
    ) -> int:
        col_names_str = ', '.join(col_names)
        ph = ', '.join(itertools.repeat('?', len(col_values)))  # placeholders
        with self.auto_committing_cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {table_name} ({col_names_str}) VALUES ({ph})",
                col_values
            )
            inserted_id = cursor.lastrowid
            if inserted_id is None:
                raise RuntimeError("Failed to insert record")
            return inserted_id

    def fetch_one(
        self,
        col_names: Sequence[str],
        table_name: str,
        seq: Sequence[str],
        condition_string: str
    ) -> Dict:
        cn = ', '.join(col_names)
        with self.auto_committing_cursor() as cursor:
            cursor.execute(
                f"SELECT {cn} from {table_name} WHERE {condition_string}",
                seq
            )
            return cursor.fetchone()

    def _fetch_all_helper(
        self,
        *args
    ) -> Iterator[Dict]:
        with self.auto_committing_cursor() as cursor:
            cursor.execute(*args)
            yield from cursor.fetchall()

    def fetch_all(
        self,
        col_names: Sequence[str],
        table_name: str
    ) -> Iterator[Dict]:
        yield from self._fetch_all_helper(
            f"SELECT {', '.join(col_names)} from {table_name}"
        )

    def fetch_all_matching(
        self,
        table_name: str,
        col_names: Sequence[str],
        condition_str: str,
        seq: Sequence[str]
    ) -> Iterator[Dict]:
        col_names_str = ', '.join(col_names)
        yield from self._fetch_all_helper(
            f"SELECT {col_names_str} from {table_name} WHERE {condition_str}",
            seq
        )

    def delete_record(
        self,
        table_name: str,
        condition_string: str,
        seq: Sequence[str]
    ) -> None:
        with self.auto_committing_cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {table_name} WHERE {condition_string}",
                seq
            )

    def update_record(
        self,
        table_name: str,
        col_names: Sequence[str],
        col_values: Sequence[str],
        condition_str: str,
        condition_values: Sequence[str]
    ) -> None:
        cols_to_update_str = ", ".join((f"{_} = ?" for _ in col_names))
        update_statement = "UPDATE {0} SET {1} WHERE {2}".format(
            table_name,
            cols_to_update_str,
            condition_str
        )
        with self.auto_committing_cursor() as cursor:
            cursor.execute(
                update_statement,
                list(itertools.chain(col_values, condition_values))
            )

    @classmethod
    def from_config(cls: Type[Self]) -> Self:
        return cls(
            host=app_constants.DB_HOST,
            user_name=app_constants.db_user,
            password=app_constants.db_password,
            port_number=app_constants.db_port,
            db_name=app_constants.db_name
        )
