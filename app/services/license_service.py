from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import logging

from app.models.license import License
from app.models.redeem_log import RedeemLog
from app.models.license_log import LicenseLog

logger = logging.getLogger(__name__)


class LicenseService:
    """授权服务（无设备绑定版本）"""

    @staticmethod
    def get_by_account(db: Session, shadow_account: str) -> Optional[License]:
        """根据影刀账号查询授权"""
        return db.query(License).filter(License.shadow_account == shadow_account).first()

    @staticmethod
    def create_license(db: Session, shadow_account: str, duration_days: int) -> License:
        """创建新授权"""
        expire_at = datetime.utcnow() + timedelta(days=duration_days)
        license = License(
            shadow_account=shadow_account,
            status="active",
            expire_at=expire_at,
            activated_at=datetime.utcnow()
        )
        db.add(license)
        db.commit()
        db.refresh(license)
        logger.info(f"创建授权：account={shadow_account}, expire={expire_at}")
        return license

    @staticmethod
    def extend_license(db: Session, license: License, duration_days: int) -> License:
        """延长授权"""
        now = datetime.utcnow()
        if license.expire_at > now:
            new_expire = license.expire_at + timedelta(days=duration_days)
        else:
            new_expire = now + timedelta(days=duration_days)
        license.expire_at = new_expire
        license.status = "active"
        license.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(license)
        logger.info(f"延长授权：account={license.shadow_account}, 新到期={new_expire}")
        return license

    @staticmethod
    def get_license_status(license: License) -> Tuple[str, int]:
        """获取授权状态和剩余天数"""
        now = datetime.utcnow()
        delta = license.expire_at - now
        remain_days = max(0, delta.days)
        if license.status == "banned":
            return "banned", 0
        if now >= license.expire_at:
            return "expired", 0
        return "active", remain_days

    @staticmethod
    def update_last_check(db: Session, license: License) -> None:
        """更新最后检查时间"""
        license.last_check_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def write_redeem_log(
        db: Session, card_code: str, shadow_account: str, result: str, message: str
    ) -> None:
        """写入兑换日志"""
        log = RedeemLog(card_code=card_code, shadow_account=shadow_account, result=result, message=message)
        db.add(log)
        db.commit()

    @staticmethod
    def write_license_log(
        db: Session, shadow_account: str, action: str, result: str, message: str
    ) -> None:
        """写入授权日志"""
        log = LicenseLog(shadow_account=shadow_account, action=action, result=result, message=message)
        db.add(log)
        db.commit()

    @staticmethod
    def list_licenses(
        db: Session, status: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> Tuple[List[License], int]:
        """查询授权列表"""
        query = db.query(License)
        if status:
            query = query.filter(License.status == status)
        total = query.count()
        licenses = query.order_by(License.created_at.desc()).offset(offset).limit(limit).all()
        return licenses, total

    @staticmethod
    def extend_by_days(db: Session, shadow_account: str, days: int) -> Optional[License]:
        """手动延期指定天数"""
        license = LicenseService.get_by_account(db, shadow_account)
        if not license:
            return None
        now = datetime.utcnow()
        if license.expire_at > now:
            new_expire = license.expire_at + timedelta(days=days)
        else:
            new_expire = now + timedelta(days=days)
        license.expire_at = new_expire
        license.status = "active"
        db.commit()
        db.refresh(license)
        logger.info(f"管理员延期：account={shadow_account}, days={days}")
        return license

    @staticmethod
    def ban_account(db: Session, shadow_account: str) -> Optional[License]:
        """禁用账号"""
        license = LicenseService.get_by_account(db, shadow_account)
        if not license:
            return None
        license.status = "banned"
        db.commit()
        db.refresh(license)
        return license
