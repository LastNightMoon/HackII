from pydantic import BaseModel
from typing import Optional, List

class AudioFilterRequest(BaseModel):
    music_category: List[int]
    text: Optional[str]

class CategoryFilter(BaseModel):
    id: int
    name: str

class AudioBaseInfo(BaseModel):
    id: int
    name: str
    author: Optional[str]
    url: str

class AudioFullInfo(AudioBaseInfo):
    id: int
    name: str
    author: Optional[str]
    music_category: str
    text: Optional[str]
    url: str


