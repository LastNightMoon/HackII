from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    def __repr__(self):
        fields = ', '.join(f"{k}={getattr(self, k)!r}" for k in self.__mapper__.columns.keys())
        return f"{self.__class__.__name__}({fields})"

    def __str__(self):
        return self.__repr__()


class Category(Base):
    __tablename__ = 'category'
    category_id: int = Column(Integer, primary_key=True, autoincrement=True)
    label: str = Column(String)
    owner_music_meta = relationship("MusicMeta", back_populates="owner_category")


class MusicMeta(Base):
    __tablename__ = 'music_meta'
    music_id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String)
    music_category: int = Column(Integer, ForeignKey('category.category_id'))
    text_music: str = Column(String)
    url: str = Column(String)
    search_vector = Column(TSVECTOR)

    owner_category = relationship("Category", back_populates="owner_music_meta")

class MusicQueue(Base):
    __tablename__ = 'music_queue'
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    url: str = Column(String)

