import hashlib

from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = self.data
        email = data["email"]
        password = data["password"]

        admin = await self.store.admins.get_by_email(email)

        if admin:
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if admin.password != input_hash:
                admin = None

        if not admin:
            raise HTTPForbidden(reason="Invalid email or password")

        admin_data = AdminSchema().dump(admin)
        session = await new_session(self.request)
        session["admin"] = admin_data

        return json_response(data=admin_data)


class AdminCurrentView(View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        if not self.request.admin:
            raise HTTPUnauthorized()

        return json_response(data=AdminSchema().dump(self.request.admin))
