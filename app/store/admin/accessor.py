import hashlib

from sqlalchemy import select

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        admin_email = self.app.config.admin.email
        admin = await self.get_by_email(admin_email)

        if not admin:
            await self.create_admin(
                email=admin_email,
                password=self.app.config.admin.password
            )

    async def get_by_email(self, email: str) -> AdminModel | None:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def create_admin(self, email: str, password: str) -> AdminModel:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        admin = AdminModel(email=email, password=hashed_password)
        async with self.app.database.session() as session:
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
        return admin
