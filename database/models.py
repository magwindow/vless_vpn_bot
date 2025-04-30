from sqlalchemy import String, BigInteger, DateTime, select, Column, Integer, Boolean, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


# Базовый класс моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    is_paid: Mapped[bool] = mapped_column(default=False)
    tg_username: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    trial_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Новое поле для подсчёта рефералов
    referral_count: Mapped[int] = mapped_column(BigInteger, default=0)


# Модель ключа
class VlessKey(Base):
    __tablename__ = 'vless_keys'

    id: Mapped[int] = mapped_column(primary_key=True)
    key_id: Mapped[str] = mapped_column(String(255), nullable=False)
    uuid: Mapped[str] = mapped_column(String(255), nullable=False)
    access_url: Mapped[str] = mapped_column(String(512), nullable=False)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    user_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    total_limit_gb: Mapped[float] = mapped_column(default=0.0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    protocol: Mapped[str] = mapped_column(String(50), default="vless", nullable=False)
    flow: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    promo_code_id = Column(Integer, ForeignKey('promo_codes.id'), nullable=True)
    promo_code = relationship('PromoCode', back_populates='vless_keys')


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer, default=1)
    uses = Column(Integer, default=0)
    total_gb = Column(Integer, nullable=False)
    expiry_days = Column(Integer, nullable=False)

    vless_keys = relationship("VlessKey", back_populates="promo_code")


class PaymentRecord(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    payment_id = Column(String, unique=True)
    user_id = Column(BigInteger)
    tariff_key = Column(String)
    is_paid = Column(Boolean, default=False)


# Подключение к БД и фабрика сессий
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


# Добавление пользователя
async def add_user_if_not_exists(user_id: int, ref_id: Optional[int] = None, username: Optional[str] = None,
                                 full_name: Optional[str] = None, is_paid: bool = False, referral_count: int = 0):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalar_one_or_none()
            if not user:
                trial_end = datetime.utcnow() + timedelta(days=3)
                new_user = User(
                    id=user_id,
                    referrer_id=ref_id,
                    tg_username=username,
                    full_name=full_name,
                    trial_end_date=trial_end,
                    is_paid=is_paid,
                    referral_count=referral_count
                )
                session.add(new_user)


# Инициализация БД
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
