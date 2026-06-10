from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import mapped_column
from database import Base

class MediaItemDB(Base):
    __tablename__ = "media_items"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    category = mapped_column(String, index=True)
    title = mapped_column(String, nullable=True)
    source_url = mapped_column(String, nullable=True)
    cover_url = mapped_column(String, nullable=True)
    description = mapped_column(Text, nullable=True)
    rating = mapped_column(Integer, default=0)
    comment = mapped_column(Text, nullable=True)