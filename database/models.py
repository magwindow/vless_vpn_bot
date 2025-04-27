from sqlalchemy import String, BigInteger, DateTime, select, Column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import os

# Загрузка переменных окружения
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


# Базовый класс моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Пример модели пользователя
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tg_username: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    full_name = Column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class VlessKey(Base):
    __tablename__ = 'vless_keys'

    id: Mapped[int] = mapped_column(primary_key=True)
    key_id: Mapped[str] = mapped_column(String(255))
    uuid: Mapped[str] = mapped_column(String(255))  # UUID клиента
    access_url: Mapped[str] = mapped_column(String(512))  # ссылка для подключения
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)  # Telegram chat id
    user_name: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    total_limit_gb: Mapped[float] = mapped_column(default=0.0)  # лимит
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # срок действия
    protocol: Mapped[str] = mapped_column(String(50), default="vless")  # на всякий случай
    flow: Mapped[str] = mapped_column(String(255), nullable=True)  # flow типа xtls-rprx-vision


# Подключение к БД и фабрика сессий
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def add_user_if_not_exists(user_id: int, username: str = None, full_name: str = None):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()
            if not user:
                new_user = User(id=user_id, tg_username=username, full_name=full_name)
                session.add(new_user)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
