from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Card(Base):
    """卡密表"""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(64), unique=True, index=True, nullable=False)
    card_type = Column(String(16), nullable=False)  # month/quarter/year
    duration_days = Column(Integer, nullable=False)  # 30/90/365
    status = Column(String(16), default="unused")  # unused/used/disabled/expired
    used_by = Column(String(64), nullable=True)  # shadow_account
    used_at = Column(DateTime, nullable=True)
    expire_at = Column(DateTime, nullable=True)  # 卡密自身有效期
    source = Column(String(64), nullable=True)  # 来源
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
