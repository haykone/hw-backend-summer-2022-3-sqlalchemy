# Добавил HTTPBadRequest
from aiohttp.web import (HTTPBadRequest, HTTPConflict, HTTPNotFound,
                         HTTPUnauthorized)
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.models import AnswerModel
from app.quiz.schemes import (ListQuestionSchema, QuestionSchema,
                              ThemeIdSchema, ThemeListSchema, ThemeSchema)
from app.web.app import View
from app.web.utils import json_response


class ThemeAddView(View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        if not self.request.admin:
            raise HTTPUnauthorized()

        title = self.data["title"]
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict(reason="Theme already exists")

        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @response_schema(ThemeListSchema)
    async def get(self):
        if not self.request.admin:
            raise HTTPUnauthorized()

        themes = await self.store.quizzes.list_themes()
        return json_response(data={"themes": [ThemeSchema().dump(t) for t in themes]})


class QuestionAddView(View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        if not self.request.admin:
            raise HTTPUnauthorized()

        data = self.data

        theme = await self.store.quizzes.get_theme_by_id(data["theme_id"])
        if not theme:
            raise HTTPNotFound(reason="Theme not found")

        if await self.store.quizzes.get_question_by_title(data["title"]):
            raise HTTPConflict(reason="Question already exists")

        answers_data = data["answers"]
        if len(answers_data) < 2:
            raise HTTPBadRequest(reason="At least 2 answers required")

        correct_answers = [a for a in answers_data if a["is_correct"] is True]
        if len(correct_answers) != 1:
            raise HTTPBadRequest(
                reason="Exactly one correct answer is required")

        answers = [
            AnswerModel(title=a["title"], is_correct=a["is_correct"])
            for a in answers_data
        ]

        question = await self.store.quizzes.create_question(
            title=data["title"],
            theme_id=data["theme_id"],
            answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        if not self.request.admin:
            raise HTTPUnauthorized()

        theme_id = self.request.query.get("theme_id")
        if theme_id:
            theme_id = int(theme_id)

        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        return json_response(data={"questions": [QuestionSchema().dump(q) for q in questions]})
