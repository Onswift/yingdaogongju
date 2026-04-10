"""
影刀授权验证 - 心跳上报模块

功能：发送心跳上报

使用方法：
1. 在影刀中创建此模块
2. 修改配置区域的 API_URL
3. 在流程中调用，传入参数
4. 获取返回结果

输入参数：
    params.shadow_account: 影刀账号（必填）

返回结果：
    dict: {
        "success": True/False,
        "status": "授权状态",
        "message": "错误信息（如果有）"
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
    心跳上报

    参数:
        params: 影刀流程参数对象
        params.shadow_account: 影刀账号（字符串）

    返回:
        dict: 心跳结果
    """
    # 获取输入参数
    shadow_account = getattr(params, 'shadow_account', '')

    # 参数校验
    if not shadow_account:
        logger.error("缺少参数：shadow_account")
        return {
            "success": False,
            "status": "error",
            "message": "缺少参数：shadow_account"
        }

    # 发送请求
    try:
        resp = requests.post(
            f"{API_URL}/heartbeat",
            json={"shadow_account": shadow_account},
            timeout=10
        )
        result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            return {
                "success": True,
                "status": data.get("status"),
                "message": ""
            }
        else:
            msg = result.get("message", "心跳失败")
            logger.warning(f"心跳失败：{msg}")
            return {
                "success": False,
                "status": "invalid",
                "message": msg
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"网络错误：{e}")
        return {
            "success": False,
            "status": "error",
            "message": f"网络错误：{e}"
        }
    except Exception as e:
        logger.error(f"未知错误：{e}")
        return {
            "success": False,
            "status": "error",
            "message": f"未知错误：{e}"
        }
