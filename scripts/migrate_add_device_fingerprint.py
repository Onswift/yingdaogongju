#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加设备指纹字段

用于单设备登录功能，向 licenses 表添加：
- device_fingerprint: 设备指纹
- last_device_seen_at: 最后设备活跃时间

使用方法：
    python scripts/migrate_add_device_fingerprint.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def migrate():
    """执行数据库迁移"""

    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)

    # 检查字段是否已存在
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('licenses')]

    print(f"当前 licenses 表字段：{columns}")

    # 检查是否需要迁移
    needs_device_fingerprint = 'device_fingerprint' not in columns
    needs_last_device_seen_at = 'last_device_seen_at' not in columns

    if not needs_device_fingerprint and not needs_last_device_seen_at:
        print("✓ 数据库已经是最新版本，无需迁移")
        return True

    print("\n开始执行数据库迁移...")

    with engine.connect() as conn:
        try:
            # 添加 device_fingerprint 字段
            if needs_device_fingerprint:
                print("  添加 device_fingerprint 字段...")
                conn.execute(text(
                    "ALTER TABLE licenses ADD COLUMN device_fingerprint VARCHAR(64) NULL"
                ))
                print("  ✓ device_fingerprint 字段已添加")

            # 添加 last_device_seen_at 字段
            if needs_last_device_seen_at:
                print("  添加 last_device_seen_at 字段...")
                conn.execute(text(
                    "ALTER TABLE licenses ADD COLUMN last_device_seen_at DATETIME NULL"
                ))
                print("  ✓ last_device_seen_at 字段已添加")

            conn.commit()

            print("\n✓ 数据库迁移完成！")
            print("\n新增字段说明：")
            print("  - device_fingerprint: 设备指纹（用于单设备登录验证）")
            print("  - last_device_seen_at: 最后设备活跃时间（用于追踪设备最后上线时间）")

            return True

        except Exception as e:
            conn.rollback()
            print(f"\n✗ 数据库迁移失败：{e}")
            return False


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
