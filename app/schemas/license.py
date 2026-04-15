from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class RedeemRequest(BaseModel):
    """兑换请求"""
    card_code: str = Field(..., description="卡密")
    shadow_account: str = Field(..., description="影刀账号")


class RedeemResponse(BaseModel):
    """兑换响应"""
    status: str = Field(..., description="授权状态")
    expire_at: datetime = Field(..., description="到期时间")
    remain_days: int = Field(..., description="剩余天数")


class LicenseCheckRequest(BaseModel):
    """授权校验请求"""
    shadow_account: str = Field(..., description="影刀账号")
    device_fingerprint: Optional[str] = Field(None, description="设备指纹（用于单设备登录）")


class LicenseCheckResponse(BaseModel):
    """授权校验响应"""
    status: str = Field(..., description="授权状态")
    expire_at: datetime = Field(..., description="到期时间")
    remain_days: int = Field(..., description="剩余天数")


class LicenseResponse(BaseModel):
    """授权响应"""
    id: int
    shadow_account: str
    status: str
    expire_at: datetime
    activated_at: Optional[datetime]
    last_check_at: Optional[datetime]
    device_fingerprint: Optional[str] = None  # 设备指纹
    created_at: datetime

    class Config:
        from_attributes = True


class LicenseListResponse(BaseModel):
    """授权列表响应"""
    total: int
    licenses: List[LicenseResponse]


class AdminExtendRequest(BaseModel):
    """手动延期请求"""
    shadow_account: str = Field(..., description="影刀账号")
    days: int = Field(..., ge=1, description="延期天数")
