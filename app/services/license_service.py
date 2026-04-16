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
        expire_at = datetime.now() + timedelta(days=duration_days)
        license = License(
            shadow_account=shadow_account,
            status="active",
            expire_at=expire_at,
            activated_at=datetime.now()
        )
        db.add(license)
        db.commit()
        db.refresh(license)
        logger.info(f"创建授权：account={shadow_account}, expire={expire_at}")
        return license

    @staticmethod
    def extend_license(db: Session, license: License, duration_days: int) -> License:
        """延长授权"""
        now = datetime.now()
        if license.expire_at > now:
            new_expire = license.expire_at + timedelta(days=duration_days)
        else:
            new_expire = now + timedelta(days=duration_days)
        license.expire_at = new_expire
        license.status = "active"
        license.updated_at = datetime.now()
        db.commit()
        db.refresh(license)
        logger.info(f"延长授权：account={license.shadow_account}, 新到期={new_expire}")
        return license

    @staticmethod
    def get_license_status(license: License) -> Tuple[str, int]:
        """获取授权状态和剩余天数"""
        now = datetime.now()
        delta = license.expire_at - now
        remain_days = max(0, delta.days)

        # 永久授权（9999 天）
        if remain_days >= 9000:
            return "permanent", 9999

        if license.status == "banned":
            return "banned", 0
        if now >= license.expire_at:
            return "expired", 0
        return "active", remain_days

    @staticmethod
    def update_last_check(db: Session, license: License) -> None:
        """更新最后检查时间"""
        license.last_check_at = datetime.now()
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
        now = datetime.now()
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

    @staticmethod
    def unban_account(db: Session, shadow_account: str) -> Optional[License]:
        """解禁账号"""
        license = LicenseService.get_by_account(db, shadow_account)
        if not license:
            return None
        license.status = "active"
        db.commit()
        db.refresh(license)
        return license

    @staticmethod
    def check_and_bind_device(db: Session, shadow_account: str, device_fingerprint: str) -> Tuple[bool, str, Optional[License]]:
        """
        检查并绑定设备指纹

        返回：(是否允许，消息，License 对象)
        """
        license = LicenseService.get_by_account(db, shadow_account)
        if not license:
            return False, "授权不存在", None

        # 检查授权状态
        status, _ = LicenseService.get_license_status(license)
        if status != "active":
            return False, f"授权状态异常：{status}", license

        # 未绑定设备，首次绑定
        if not license.device_fingerprint:
            license.device_fingerprint = device_fingerprint
            license.last_device_seen_at = datetime.now()
            db.commit()
            logger.info(f"设备绑定：account={shadow_account}, fingerprint={device_fingerprint[:16]}...")
            return True, "设备已绑定", license

        # 设备指纹匹配
        if license.device_fingerprint == device_fingerprint:
            license.last_device_seen_at = datetime.now()
            db.commit()
            return True, "设备验证通过", license

        # 设备不匹配，拒绝
        logger.warning(f"设备不匹配：account={shadow_account}, 已绑定={license.device_fingerprint[:16]}..., 请求={device_fingerprint[:16]}...")
        return False, "该账号已在其他设备登录，如需切换设备请联系管理员解绑", license

    @staticmethod
    def unbind_device(db: Session, shadow_account: str) -> Tuple[bool, str]:
        """
        解绑设备

        返回：(是否成功，消息)
        """
        license = LicenseService.get_by_account(db, shadow_account)
        if not license:
            return False, "授权不存在"

        if not license.device_fingerprint:
            return False, "该账号未绑定设备"

        license.device_fingerprint = None
        license.last_device_seen_at = None
        db.commit()
        logger.info(f"设备解绑：account={shadow_account}")
        return True, "设备已解绑"

    @staticmethod
    def undo_redeem(db: Session, card_code: str, shadow_account: str) -> tuple:
        """
        撤销兑换（恢复卡密，扣除授权天数）

        返回：
            (success: bool, message: str)
        """
        from app.services.card_service import CardService

        # 1. 查询卡密
        card = CardService.get_by_code(db, card_code)
        if not card:
            return False, "卡密不存在"

        if card.status != "used":
            return False, "卡密未使用，无法撤销"

        if card.used_by != shadow_account:
            return False, "该卡密不是此账号兑换的"

        # 2. 查询授权
        license = LicenseService.get_by_account(db, shadow_account)
        if not license:
            return False, "授权不存在"

        # 3. 恢复卡密状态
        card.status = "unused"
        card.used_by = None
        card.used_at = None
        db.commit()

        # 4. 扣除授权天数（从到期时间减去）
        from datetime import timedelta
        license.expire_at = license.expire_at - timedelta(days=card.duration_days)

        # 如果到期时间已过，设置为过期
        if license.expire_at < datetime.now():
            license.status = "expired"

        license.updated_at = datetime.now()
        db.commit()
        db.refresh(license)

        # 5. 写日志
        LicenseService.write_license_log(db, shadow_account, "undo_redeem", "success",
            f"撤销兑换，卡密：{card_code}, 扣除{card.duration_days}天")

        logger.info(f"撤销兑换：account={shadow_account}, card={card_code}")
        return True, f"已撤销兑换，扣除{card.duration_days}天授权"
