from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.response import success_response, error_response, ErrorCode
from app.schemas.license import RedeemRequest, LicenseCheckRequest
from app.services.card_service import CardService
from app.services.license_service import LicenseService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["用户接口"])


@router.post("/redeem", response_model=dict, summary="兑换卡密")
async def redeem(req: RedeemRequest, db: Session = Depends(get_db)):
    """
    兑换卡密授权

    - **card_code**: 卡密
    - **shadow_account**: 影刀账号
    """
    try:
        # 1. 查询卡密
        card = CardService.get_by_code(db, req.card_code)
        if not card:
            LicenseService.write_redeem_log(db, req.card_code, req.shadow_account, "failure", "卡密不存在")
            return error_response(ErrorCode.CARD_NOT_FOUND, "卡密不存在")

        # 2. 校验卡密
        is_valid, msg = CardService.validate_card(card)
        if not is_valid:
            LicenseService.write_redeem_log(db, req.card_code, req.shadow_account, "failure", msg)
            if "已被使用" in msg:
                return error_response(ErrorCode.CARD_ALREADY_USED, msg)
            elif "作废" in msg:
                return error_response(ErrorCode.CARD_DISABLED, msg)
            else:
                return error_response(ErrorCode.CARD_EXPIRED, msg)

        # 3. 查询或创建授权
        license = LicenseService.get_by_account(db, req.shadow_account)

        # 检查是否已有授权（用于提示用户）
        has_existing_license = license is not None
        old_expire_at = license.expire_at.isoformat() if license and license.expire_at else None

        if not license:
            license = LicenseService.create_license(db, req.shadow_account, card.duration_days)
        else:
            license = LicenseService.extend_license(db, license, card.duration_days)

        # 4. 标记卡密已使用
        CardService.mark_used(db, card, req.shadow_account)

        # 5. 写日志
        LicenseService.write_redeem_log(db, req.card_code, req.shadow_account, "success", f"兑换成功")
        LicenseService.write_license_log(db, req.shadow_account, "redeem", "success", f"兑换成功，卡密：{req.card_code}")

        # 6. 返回结果
        status, remain_days = LicenseService.get_license_status(license)
        return success_response(data={
            "status": status,
            "expire_at": license.expire_at.isoformat(),
            "remain_days": remain_days,
            "has_existing_license": has_existing_license,
            "old_expire_at": old_expire_at,
            "added_days": card.duration_days
        })

    except Exception as e:
        logger.exception("兑换失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/check-license", response_model=dict, summary="校验授权")
async def check_license(req: LicenseCheckRequest, db: Session = Depends(get_db)):
    """
    校验授权状态

    - **shadow_account**: 影刀账号
    """
    try:
        # 1. 查询授权
        license = LicenseService.get_by_account(db, req.shadow_account)
        if not license:
            LicenseService.write_license_log(db, req.shadow_account, "check", "failure", "授权不存在")
            return error_response(ErrorCode.LICENSE_NOT_FOUND, "授权不存在")

        # 2. 获取状态
        status, remain_days = LicenseService.get_license_status(license)

        # 3. 更新最后检查时间
        LicenseService.update_last_check(db, license)

        # 4. 写日志
        LicenseService.write_license_log(db, req.shadow_account, "check", "success", f"状态：{status}")

        return success_response(data={
            "status": status,
            "expire_at": license.expire_at.isoformat(),
            "remain_days": remain_days
        })

    except Exception as e:
        logger.exception("校验授权失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))


@router.post("/heartbeat", response_model=dict, summary="心跳上报")
async def heartbeat(req: LicenseCheckRequest, db: Session = Depends(get_db)):
    """
    心跳上报（轻量级校验）

    - **shadow_account**: 影刀账号
    """
    try:
        license = LicenseService.get_by_account(db, req.shadow_account)
        if not license:
            return error_response(ErrorCode.LICENSE_NOT_FOUND, "授权不存在")

        status, remain_days = LicenseService.get_license_status(license)
        LicenseService.update_last_check(db, license)
        LicenseService.write_license_log(db, req.shadow_account, "heartbeat", "success", f"状态：{status}")

        return success_response(data={
            "status": status,
            "expire_at": license.expire_at.isoformat(),
            "remain_days": remain_days
        })

    except Exception as e:
        logger.exception("心跳上报失败")
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))
