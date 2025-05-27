import os
from typing import Type, List

import requests
import sqlalchemy
from sqlalchemy.dialects import postgresql

from DataBaseManager import Base, MusicMeta


def get_text_sql(stmt):
    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def pipeline_sql(query, table: Type[Base] = None) -> List[Base]:
    if not isinstance(query, str):
        query = get_text_sql(query)
    response = requests.post(
        os.environ.get("DB_API"),
        json={"text": query, "model_name": "none" if table is None else table.__name__}
    )
    data = response.json()  # словарь: {"ok": true, "response": [...]}

    if not data or not data.get("ok", False):
        raise Exception(f"Ошибка SQL: {data.get('response')}")

    items = data["response"]

    if table is None:
        return list()
    return [table(**item) for item in items]


def select_music_by_id(id):
    res = pipeline_sql(sqlalchemy.select(MusicMeta).where(MusicMeta.music_id == id), MusicMeta)
    if len(res) == 0:
        return None
    return res[0]
