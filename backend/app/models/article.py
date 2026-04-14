from typing import List

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base



class Article(Base):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)#主键自增
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id")) #外键
    author: Mapped["User"] = relationship(back_populates="articles")
    tags: Mapped[List["Tag"]] = relationship("Tag",back_populates="articles",secondary="article_tag")

class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    articles: Mapped[List[Article]] = relationship("Article",back_populates="tags",secondary="article_tag")

class ArticleTag(Base):
    __tablename__ = "article_tag"
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("article.id"),primary_key= True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"),primary_key= True)