from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging
import secrets

from app.core.database import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.core.config import settings
from app.schemas.card import CardGenerateRequest, DisableCardRequest, UndoRedeemRequest
from app.schemas.license import AdminExtendRequest
from app.services.card_service import CardService
from app.services.license_service import LicenseService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["管理接口"])


def verify_admin(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    """验证管理员 Token"""
    if not secrets.compare_digest(x_admin_token, settings.ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_admin_token


@router.post("/cards/generate", response_model=dict, summary="批量生成卡密")
async def generate_cards(
    req: CardGenerateRequest,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """批量生成卡密"""
    try:
        cards = CardService.generate_cards(
            db=db,
            card_type=req.card_type,
            duration_days=req.duration_days,
            quantity=req.quantity,
            source=req.source,
            expire_days=req.expire_days
        )
        card_codes = [c.card_code for c in cards]
        return success_response(data={"count": len(cards), "card_codes": card_codes})
    except Exception as e:
        logger.exception("生成卡密失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.get("/cards", response_model=dict, summary="查询卡密列表")
async def list_cards(
    status: Optional[str] = None,
    type: Optional[str] = None,
    used_by: Optional[str] = None,
    source: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """查询卡密列表"""
    try:
        offset = (page - 1) * page_size
        cards, total = CardService.list_cards(db, status=status, card_type=type, used_by=used_by, source=source, limit=page_size, offset=offset)
        return success_response(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "cards": [{
                "id": c.id,
                "card_code": c.card_code,
                "card_type": c.card_type,
                "duration_days": c.duration_days,
                "status": c.status,
                "used_by": c.used_by,
                "used_at": c.used_at.isoformat() if c.used_at else None,
                "expire_at": c.expire_at.isoformat() if c.expire_at else None,
                "source": c.source,
                "created_at": c.created_at.isoformat()
            } for c in cards]
        })
    except Exception as e:
        logger.exception("查询卡密失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/cards/disable", response_model=dict, summary="作废卡密")
async def disable_card(
    req: DisableCardRequest,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """作废卡密"""
    try:
        success = CardService.disable(db, req.card_code)
        if not success:
            return error_response(ErrorCode.BAD_REQUEST, "卡密不存在或已使用")
        return success_response(message="卡密已作废")
    except Exception as e:
        logger.exception("作废卡密失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.get("/licenses", response_model=dict, summary="查询授权列表")
async def list_licenses(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """查询授权列表"""
    try:
        offset = (page - 1) * page_size
        licenses, total = LicenseService.list_licenses(db, status=status, limit=page_size, offset=offset)
        return success_response(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "licenses": [{
                "id": l.id,
                "shadow_account": l.shadow_account,
                "status": l.status,
                "expire_at": l.expire_at.isoformat(),
                "activated_at": l.activated_at.isoformat() if l.activated_at else None,
                "last_check_at": l.last_check_at.isoformat() if l.last_check_at else None,
                "device_fingerprint": l.device_fingerprint,  # 设备指纹
                "created_at": l.created_at.isoformat()
            } for l in licenses]
        })
    except Exception as e:
        logger.exception("查询授权失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/licenses/extend", response_model=dict, summary="手动延期")
async def extend_license(
    req: AdminExtendRequest,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """手动延长用户授权"""
    try:
        license = LicenseService.extend_by_days(db, req.shadow_account, req.days)
        if not license:
            return error_response(ErrorCode.LICENSE_NOT_FOUND, "授权不存在")
        LicenseService.write_license_log(db, req.shadow_account, "admin_update", "success", f"管理员延期 {req.days} 天")
        return success_response(data={
            "shadow_account": req.shadow_account,
            "new_expire_at": license.expire_at.isoformat()
        })
    except Exception as e:
        logger.exception("延期失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/licenses/ban", response_model=dict, summary="禁用账号")
async def ban_account(
    shadow_account: str,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """禁用指定账号"""
    try:
        license = LicenseService.ban_account(db, shadow_account)
        if not license:
            return error_response(ErrorCode.LICENSE_NOT_FOUND, "授权不存在")
        LicenseService.write_license_log(db, shadow_account, "admin_update", "success", "账号被禁用")
        return success_response(message="账号已禁用")
    except Exception as e:
        logger.exception("禁用账号失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/licenses/unban", response_model=dict, summary="解禁账号")
async def unban_account(
    shadow_account: str,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """解禁指定账号"""
    try:
        license = LicenseService.unban_account(db, shadow_account)
        if not license:
            return error_response(ErrorCode.LICENSE_NOT_FOUND, "授权不存在")
        LicenseService.write_license_log(db, shadow_account, "admin_update", "success", "账号被解禁")
        return success_response(message="账号已解禁")
    except Exception as e:
        logger.exception("解禁账号失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/licenses/unbind-device", response_model=dict, summary="解绑设备")
async def unbind_device(
    shadow_account: str,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """解绑指定账号的设备（允许重新绑定新设备）"""
    try:
        success, message = LicenseService.unbind_device(db, shadow_account)
        if not success:
            return error_response(ErrorCode.BAD_REQUEST, message)
        LicenseService.write_license_log(db, shadow_account, "admin_update", "success", "设备被解绑")
        return success_response(message=message)
    except Exception as e:
        logger.exception("解绑设备失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/licenses/undo-redeem", response_model=dict, summary="撤销兑换")
async def undo_redeem(
    req: UndoRedeemRequest,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """撤销卡密兑换（恢复卡密，扣除授权天数）"""
    try:
        success, message = LicenseService.undo_redeem(db, req.card_code, req.shadow_account)
        if not success:
            return error_response(ErrorCode.BAD_REQUEST, message)
        return success_response(message=message)
    except Exception as e:
        logger.exception("撤销兑换失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.get("/logs/redeem", response_model=dict, summary="兑换日志")
async def list_redeem_logs(
    shadow_account: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """查询兑换日志"""
    try:
        offset = (page - 1) * page_size
        query = db.query(RedeemLog)
        if shadow_account:
            query = query.filter(RedeemLog.shadow_account == shadow_account)
        total = query.count()
        logs = query.order_by(RedeemLog.created_at.desc()).offset(offset).limit(page_size).all()
        return success_response(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "logs": [{
                "id": log.id,
                "card_code": log.card_code,
                "shadow_account": log.shadow_account,
                "result": log.result,
                "message": log.message,
                "created_at": log.created_at.isoformat()
            } for log in logs]
        })
    except Exception as e:
        logger.exception("查询兑换日志失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.get("/logs/license", response_model=dict, summary="授权日志")
async def list_license_logs(
    shadow_account: Optional[str] = None,
    action: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """查询授权日志"""
    try:
        offset = (page - 1) * page_size
        query = db.query(LicenseLog)
        if shadow_account:
            query = query.filter(LicenseLog.shadow_account == shadow_account)
        if action:
            query = query.filter(LicenseLog.action == action)
        total = query.count()
        logs = query.order_by(LicenseLog.created_at.desc()).offset(offset).limit(page_size).all()
        return success_response(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "logs": [{
                "id": log.id,
                "shadow_account": log.shadow_account,
                "action": log.action,
                "result": log.result,
                "message": log.message,
                "created_at": log.created_at.isoformat()
            } for log in logs]
        })
    except Exception as e:
        logger.exception("查询授权日志失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))
