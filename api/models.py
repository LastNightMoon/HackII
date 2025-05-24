from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class AudioRecord(BaseModel):
    id: int
    name: str
    author: Optional[str] = None
    description: Optional[str] = None
    file_name: str
    original_file_name: str
    category: Optional[int] = None
    text: Optional[str] = None
    restored: bool = False
    restoration_date: Optional[date] = None


class AudioRecordShort(BaseModel):
    id: int
    name: str
    file_name: str
    category: Optional[int] = None


class UploadResponse(BaseModel):
    status: str
    archive_url: str
    record_id: int


class CategoryResponse(BaseModel):
    id: int
    label: str