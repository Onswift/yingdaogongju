from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class License(Base):
    """授权表（支持设备绑定）"""
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    shadow_account = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(String(16), default="active")  # active/expired/banned
    expire_at = Column(DateTime, nullable=False)
    activated_at = Column(DateTime, nullable=True)
    last_check_at = Column(DateTime, nullable=True)
    device_fingerprint = Column(String(64), nullable=True)  # 设备指纹（单设备登录）
    last_device_seen_at = Column(DateTime, nullable=True)  # 最后设备活跃时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
