from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class RedeemLog(Base):
    """兑换日志表"""
    __tablename__ = "redeem_logs"

    id = Column(Integer, primary_key=True, index=True)
    card_code = Column(String(64), index=True, nullable=False)
    shadow_account = Column(String(64), index=True, nullable=False)
    result = Column(String(16), nullable=False)  # success/failure
    message = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
