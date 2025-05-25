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

class AudioUploadRequest(BaseModel):
    author: Optional[str]
    description: Optional[str]

class AudioUploadResponse(BaseModel):
    status: str
    file_id: int
    url: str
    message: Optional[str] = None

class AudioFileResponse(BaseModel):
    content: bytes
    content_type: str
    file_name: str

class AudioVersionComparison(BaseModel):
    original_version: AudioBaseInfo
    restored_version: AudioBaseInfo
    differences: List[str]