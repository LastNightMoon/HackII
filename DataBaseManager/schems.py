import pydantic

from DataBaseManager import Base


class SQLBase(pydantic.BaseModel):
    text: str
    model_name: str


class SQLResponse(pydantic.BaseModel):
    response: list | str
    ok: bool = True
