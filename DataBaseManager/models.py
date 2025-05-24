from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    category_id: int = Column(Integer, primary_key=True)
    label: str = Column(String)

    owner_music_meta = relationship("MusicMeta", back_populates="owner_category")

class MusicMeta(Base):
    __tablename__ = 'music_meta'
    music_id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    music_category: int = Column(Integer)
    text_music: str = Column(String)
    url: str = Column(String)
    search_vector = Column(TSVECTOR)

    owner_category = relationship("Category", back_populates="owner_music_meta")
