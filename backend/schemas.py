from pydantic import BaseModel
from typing import Optional

class MediaItemBase(BaseModel):
    category: str
    title: Optional[str] = None
    source_url: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[int] = 0
    comment: Optional[str] = None
    tags: Optional[str] | list[str] = None
    created_date: Optional[str] = None

class MediaItemCreate(MediaItemBase):
    is_import: bool

class MediaItem(MediaItemBase):
    id: int

    class Config:
        from_attributes = True