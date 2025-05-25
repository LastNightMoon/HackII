from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AudioUploadRequest(BaseModel):
    author: Optional[str] = None
    description: Optional[str] = None

class AudioFilterRequest(BaseModel):
    category: Optional[int] = None
    author: Optional[str] = None
    search_query: Optional[str] = None
    limit: int = 100
    offset: int = 0

class AudioBaseInfo(BaseModel):
    id: int
    name: str
    author: Optional[str] = None
    url: str

# class AudioFullInfo(AudioBaseInfo):
#     description: Optional[str] = None
#     duration: Optional[float] = None
#     file_size: Optional[int] = None
#     created_at: datetime
#     updated_at: datetime

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