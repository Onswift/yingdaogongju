from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class LicenseLog(Base):
    """授权日志表"""
    __tablename__ = "license_logs"

    id = Column(Integer, primary_key=True, index=True)
    shadow_account = Column(String(64), index=True, nullable=False)
    action = Column(String(32), nullable=False)  # redeem/check/heartbeat/admin_update
    result = Column(String(16), nullable=False)  # success/failure
    message = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
