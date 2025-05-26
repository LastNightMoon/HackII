import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.variable_environment import VarEnv
from DataBaseManager.models import Category, MusicMeta, MusicQueue, Base
from typing import List, Type, Optional


class DataBaseManager:
    def __init__(self,
                 db_url=f'postgresql+psycopg2://{VarEnv.DBUSER}:{VarEnv.DBPASSWORD}@{VarEnv.DBHOST}/{VarEnv.DBNAME}'):
        self.engine = create_engine(db_url, echo=True)

    def execute_commit(self, command):
        with self.engine.connect() as session:
            try:
                result = session.execute(command)
                session.commit()
                return result.all()
            except sqlalchemy.exc.ResourceClosedError:
                return "OK"

    def select(self, model: Type[Base],
               filter_condition: Optional[dict] = None,
               limit: Optional[int] = None,
               offset: Optional[int] = None) -> List[Base]:
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

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()


db = DataBaseManager()
if __name__ == "__main__":
    print(db.select_music_by_id(0))
    print(db.select(Category))
