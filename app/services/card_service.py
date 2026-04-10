from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import logging
import secrets
import string

from app.models.card import Card

logger = logging.getLogger(__name__)


def generate_card_code(length: int = 16) -> str:
    """生成卡密"""
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(length))
    chunks = [random_part[i:i+4] for i in range(0, len(random_part), 4)]
    return f"LIC-{'-'.join(chunks)}"


class CardService:
    """卡密服务"""

    @staticmethod
    def create_card(
        db: Session,
        card_type: str,
        duration_days: int,
        source: Optional[str] = None,
        expire_days: Optional[int] = None
    ) -> Card:
        """创建单张卡密"""
        card_code = generate_card_code()
        expire_at = datetime.now() + timedelta(days=expire_days) if expire_days else None

        card = Card(
            card_code=card_code,
            card_type=card_type,
            duration_days=duration_days,
            status="unused",
            source=source,
            expire_at=expire_at
        )

        db.add(card)
        db.commit()
        db.refresh(card)
        logger.info(f"创建卡密：{card_code}, 类型：{card_type}")
        return card

    @staticmethod
    def generate_cards(
        db: Session,
        card_type: str,
        duration_days: int,
        quantity: int,
        source: Optional[str] = None,
        expire_days: Optional[int] = None
    ) -> List[Card]:
        """批量生成卡密"""
        cards = []
        for _ in range(quantity):
            card = CardService.create_card(db, card_type, duration_days, source, expire_days)
            cards.append(card)
        logger.info(f"批量生成 {quantity} 张卡密，类型：{card_type}")
        return cards

    @staticmethod
    def get_by_code(db: Session, card_code: str) -> Optional[Card]:
        """根据卡密查询"""
        return db.query(Card).filter(Card.card_code == card_code).first()

    @staticmethod
    def validate_card(card: Card) -> tuple:
        """校验卡密是否可用"""
        if card.status == "used":
            return False, "卡密已被使用"
        if card.status == "disabled":
            return False, "卡密已被作废"
        if card.status == "expired":
            return False, "卡密已过期"
        if card.expire_at and card.expire_at < datetime.now():
            return False, "卡密已过期"
        return True, ""

    @staticmethod
    def mark_used(db: Session, card: Card, shadow_account: str) -> None:
        """标记卡密已使用"""
        card.status = "used"
        card.used_by = shadow_account
        card.used_at = datetime.now()
        db.commit()
        logger.info(f"卡密 {card.card_code} 已使用，账号：{shadow_account}")

    @staticmethod
    def disable(db: Session, card_code: str) -> bool:
        """作废卡密"""
        card = CardService.get_by_code(db, card_code)
        if not card or card.status == "used":
            return False
        card.status = "disabled"
        db.commit()
        logger.info(f"卡密 {card_code} 已作废")
        return True

    @staticmethod
    def list_cards(
        db: Session,
        status: Optional[str] = None,
        card_type: Optional[str] = None,
        used_by: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple:
        """查询卡密列表"""
        query = db.query(Card)
        if status:
            query = query.filter(Card.status == status)
        if card_type:
            query = query.filter(Card.card_type == card_type)
        if used_by:
            query = query.filter(Card.used_by.like(f"%{used_by}%"))
        if source:
            query = query.filter(Card.source == source)
        total = query.count()
        cards = query.order_by(Card.created_at.desc()).offset(offset).limit(limit).all()
        return cards, total
