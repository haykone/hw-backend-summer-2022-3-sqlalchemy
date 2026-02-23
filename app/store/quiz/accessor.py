from collections.abc import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import AnswerModel, QuestionModel, ThemeModel


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        theme = ThemeModel(title=title)
        async with self.app.database.session() as session:
            session.add(theme)
            await session.commit()
            await session.refresh(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> ThemeModel | None:
        query = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_theme_by_id(self, id_: int) -> ThemeModel | None:
        async with self.app.database.session() as session:
            return await session.get(ThemeModel, id_)

    async def list_themes(self) -> Sequence[ThemeModel]:
        query = select(ThemeModel)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def create_question(
        self, title: str, theme_id: int, answers: Iterable[AnswerModel]
    ) -> QuestionModel:
        question = QuestionModel(
            title=title,
            theme_id=theme_id,
            answers=list(answers)
        )

        async with self.app.database.session() as session:
            session.add(question)
            await session.commit()

            query = (
                select(QuestionModel)
                .where(QuestionModel.id == question.id)
                .options(selectinload(QuestionModel.answers))
            )
            result = await session.execute(query)
            return result.scalar_one()

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        query = (
            select(QuestionModel)
            .where(QuestionModel.title == title)
            .options(selectinload(QuestionModel.answers))
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def list_questions(
        self, theme_id: int | None = None
    ) -> Sequence[QuestionModel]:
        query = select(QuestionModel).options(
            selectinload(QuestionModel.answers))
        if theme_id:
            query = query.where(QuestionModel.theme_id == theme_id)

        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalars().unique().all()
