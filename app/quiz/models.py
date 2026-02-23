from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


class ThemeModel(BaseModel):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)

    questions = relationship(
        "QuestionModel", cascade="all, delete-orphan", back_populates="theme")


class QuestionModel(BaseModel):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    theme_id = Column(ForeignKey(
        "themes.id", ondelete="CASCADE"), nullable=False)

    theme = relationship("ThemeModel", back_populates="questions")
    answers = relationship(
        "AnswerModel", cascade="all, delete-orphan", back_populates="question")


class AnswerModel(BaseModel):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(ForeignKey(
        "questions.id", ondelete="CASCADE"), nullable=False)

    question = relationship("QuestionModel", back_populates="answers")
