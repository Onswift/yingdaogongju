"""
影刀授权验证 - 卡密兑换模块

功能：兑换卡密（带重复兑换检查）

使用方法：
1. 在影刀中创建此模块
2. 修改配置区域的 API_URL
3. 在流程中调用，传入参数
4. 获取返回结果

输入参数：
    params.shadow_account: 影刀账号（必填）
    params.card_code: 卡密代码（必填）

返回结果：
    dict: {
        "success": True/False,
        "status": "授权状态",
        "remain_days": 剩余天数，
        "expire_at": "到期时间",
        "has_existing_license": True/False,  # 是否已有授权
        "old_expire_at": "原到期时间",
        "added_days": 增加的天数，
        "message": "错误信息（如果有）",
        "warning": "警告信息（如重复兑换）"
    }
"""

# ==================== 配置区域 ====================
API_URL = "http://localhost:8000/api"  # 修改为你的服务器地址

# ==================== 导入依赖 ====================
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 主函数 ====================
def main(params):
    """
    兑换卡密（带重复兑换检查）

    参数:
        params: 影刀流程参数对象
        params.shadow_account: 影刀账号（字符串）
        params.card_code: 卡密代码（字符串）
        params.force_redeem: 是否强制兑换（忽略警告）

    返回:
        dict: 兑换结果
    """
    # 获取输入参数
    shadow_account = getattr(params, 'shadow_account', '')
    card_code = getattr(params, 'card_code', '')
    force_redeem = getattr(params, 'force_redeem', False)

    # 参数校验
    if not shadow_account:
        logger.error("缺少参数：shadow_account")
        return {
            "success": False,
            "message": "缺少参数：shadow_account"
        }

    if not card_code:
        logger.error("缺少参数：card_code")
        return {
            "success": False,
            "message": "缺少参数：card_code"
        }

    # ==================== 步骤 1: 检查账号是否已有授权 ====================
    try:
        check_resp = requests.post(
            f"{API_URL}/check-license",
            json={"shadow_account": shadow_account},
            timeout=10
        )
        check_result = check_resp.json()

        if check_result.get("code") == 0:
            # 账号已有授权
            data = check_result.get("data", {})
            if data.get("status") == "active" and data.get("remain_days", 0) > 0:
                if not force_redeem:
                    # 返回警告，让用户确认
                    return {
                        "success": False,
                        "need_confirm": True,
                        "warning": f"该账号已有有效授权（剩余{data.get('remain_days')}天，到期：{data.get('expire_at')}）",
                        "current_status": data.get("status"),
                        "current_remain_days": data.get("remain_days"),
                        "current_expire_at": data.get("expire_at"),
                        "message": "检测到账号已有授权，继续兑换将累加天数。请确认后再次尝试（设置 force_redeem=True）。"
                    }
    except Exception as e:
        logger.warning(f"检查现有授权失败：{e}，继续兑换流程")

    logger.info(f"正在兑换卡密：{card_code} - 账号：{shadow_account}")

    # ==================== 步骤 2: 发送兑换请求 ====================
    try:
        resp = requests.post(
            f"{API_URL}/redeem",
            json={
                "card_code": card_code,
                "shadow_account": shadow_account
            },
            timeout=10
        )
        result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            logger.info(f"兑换成功 - 状态:{data.get('status')}, 剩余:{data.get('remain_days')}天")

            # 构建返回结果
            response = {
                "success": True,
                "status": data.get("status"),
                "remain_days": data.get("remain_days"),
                "expire_at": data.get("expire_at"),
                "has_existing_license": data.get("has_existing_license", False),
                "old_expire_at": data.get("old_expire_at"),
                "added_days": data.get("added_days"),
                "message": ""
            }

            # 如果有警告信息（累加兑换）
            if data.get("has_existing_license"):
                response["warning"] = f"累加兑换成功！原授权 +{data.get('added_days')}天"

            return response
        else:
            msg = result.get("message", "兑换失败")
            logger.warning(f"兑换失败：{msg}")
            return {
                "success": False,
                "message": msg
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"网络错误：{e}")
        return {
            "success": False,
            "message": f"网络错误：{e}"
        }
    except Exception as e:
        logger.error(f"未知错误：{e}")
        return {
            "success": False,
            "message": f"未知错误：{e}"
        }
