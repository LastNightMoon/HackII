import os
from typing import Type, List

import requests
from sqlalchemy.dialects import postgresql

from DataBaseManager import Base


def get_text_sql(stmt):
    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def pipeline_sql(query, table: Type[Base]) -> List[Base]:
    if not isinstance(query, str):
        query = get_text_sql(query)
    response = requests.post(
        os.environ.get("DB_API"),
        json={"text": query, "model_name": table.__name__}
    )
    data = response.json()  # словарь: {"ok": true, "response": [...]}

    if not data or not data.get("ok", False):
        raise Exception(f"Ошибка SQL: {data.get('response')}")

    items = data["response"]
    return [table(**item) for item in items]
