from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from api.utils.variable_environment import VarEnv
from DataBaseManager.models import Category, MusicMeta
from typing import List, Type, TypeVar, Optional


class DataBaseManager:
    def __init__(self,
                 db_url=f'postgresql+psycopg2://{VarEnv.DBUSER}:{VarEnv.DBPASSWORD}@{VarEnv.DBHOST}/{VarEnv.DBNAME}'):
        self.engine = create_engine(db_url, echo=True)

    def execute_commit(self, command):
        with self.engine.connect() as session:
            session.execute(command)
            session.commit()
            session.close()

    def select(self, model: Type[TypeVar],
               filter_condition: Optional[dict] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None) -> List[TypeVar]:
        session = self.get_session()
        try:
            query = session.query(model)

            if filter_condition:
                query = query.filter_by(**filter_condition)

            if limit is not None:
                query = query.limit(limit)

            if offset is not None:
                query = query.offset(offset)

            return query.all()
        except Exception as e:
            print(e)
        finally:
            session.close()
            raise Exception("DatabaseSelectError")

    def get_session(self):
        return self.engine.connect()


db = DataBaseManager()
