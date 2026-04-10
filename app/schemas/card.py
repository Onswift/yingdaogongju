from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CardGenerateRequest(BaseModel):
    """批量生成卡密请求"""
    card_type: str = Field(..., description="卡密类型：month/quarter/year")
    duration_days: int = Field(..., description="有效天数")
    quantity: int = Field(1, ge=1, le=100, description="生成数量")
    source: Optional[str] = Field(None, description="来源标识")
    expire_days: Optional[int] = Field(None, description="卡密自身有效期（天）")


class CardResponse(BaseModel):
    """卡密响应"""
    id: int
    card_code: str
    card_type: str
    duration_days: int
    status: str
    used_by: Optional[str]
    used_at: Optional[datetime]
    expire_at: Optional[datetime]
    source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CardListResponse(BaseModel):
    """卡密列表响应"""
    total: int
    cards: List[CardResponse]


class DisableCardRequest(BaseModel):
    """作废卡密请求"""
    card_code: str = Field(..., description="卡密")


class UndoRedeemRequest(BaseModel):
    """撤销兑换请求"""
    card_code: str = Field(..., description="卡密代码")
    shadow_account: str = Field(..., description="影刀账号")
