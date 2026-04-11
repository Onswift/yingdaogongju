"""
影刀授权验证 - 基础验证模块

功能：验证影刀账号的授权状态

使用方法：
1. 在影刀中创建此模块
2. 修改配置区域的 API_URL
3. 在流程中调用，传入 shadow_account 参数
4. 获取返回结果

输入参数：
    params.shadow_account: 影刀账号（必填）

返回结果：
    dict: {
        "success": True/False,
        "status": "active/expired/banned",
        "remain_days": 剩余天数，
        "expire_at": "到期时间",
        "message": "错误信息（如果有）"
    }
"""

# ==================== 配置区域 ====================
API_URL = "http://8.138.108.144:8001/api"  # 服务器 API 地址

# ==================== 导入依赖 ====================
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 主函数 ====================
def main(params):
    """
    验证授权状态

    参数:
        params: 影刀流程参数对象
        params.shadow_account: 影刀账号（字符串）

    返回:
        dict: 验证结果
    """
    # 获取输入参数
    shadow_account = getattr(params, 'shadow_account', '')

    # 参数校验
    if not shadow_account:
        logger.error("缺少参数：shadow_account")
        return {
            "success": False,
            "status": "error",
            "remain_days": 0,
            "expire_at": "",
            "message": "缺少参数：shadow_account"
        }

    logger.info(f"正在验证账号：{shadow_account}")

    # 发送请求
    try:
        resp = requests.post(
            f"{API_URL}/check-license",
            json={"shadow_account": shadow_account},
            timeout=10
        )
        result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            logger.info(f"验证通过 - 状态:{data.get('status')}, 剩余:{data.get('remain_days')}天")
            return {
                "success": True,
                "status": data.get("status"),
                "remain_days": data.get("remain_days"),
                "expire_at": data.get("expire_at"),
                "message": ""
            }
        else:
            msg = result.get("message", "验证失败")
            logger.warning(f"验证失败：{msg}")
            return {
                "success": False,
                "status": "invalid",
                "remain_days": 0,
                "expire_at": "",
                "message": msg
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"网络错误：{e}")
        return {
            "success": False,
            "status": "error",
            "remain_days": 0,
            "expire_at": "",
            "message": f"网络错误：{e}"
        }
    except Exception as e:
        logger.error(f"未知错误：{e}")
        return {
            "success": False,
            "status": "error",
            "remain_days": 0,
            "expire_at": "",
            "message": f"未知错误：{e}"
        }
