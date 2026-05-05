"""
影刀授权验证 - 心跳上报模块（支持单设备登录）

功能：发送心跳上报

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
API_URL = "http://8.138.108.144:8001/api"  # 服务器 API 地址

# ==================== 导入依赖 ====================
import requests
import logging
import hashlib
import socket
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_disk_serial():
    """获取硬盘序列号（Windows）"""
    try:
        result = subprocess.check_output(
            "wmic diskdrive get serialnumber",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode(errors="ignore").strip().split("\n")
        serials = [s.strip() for s in result if s.strip() and s.strip().lower() != "serialnumber"]
        return serials[0] if serials else "unknown"
    except Exception as e:
        logger.warning(f"获取硬盘序列号失败：{e}")
        return "unknown"


def generate_device_fingerprint(shadow_account):
    """生成设备指纹：账号 + 主机名 + 硬盘序列号"""
    try:
        hostname = socket.gethostname()
        disk_serial = get_disk_serial()
        data = f"{shadow_account}|{hostname}|{disk_serial}"
        return hashlib.sha256(data.encode()).hexdigest()[:64]
    except Exception as e:
        logger.warning(f"生成设备指纹失败：{e}")
        return None


# ==================== 主函数 ====================
def main(params):
    shadow_account = getattr(params, 'shadow_account', '')

    if not shadow_account:
        return {"success": False, "status": "error", "message": "缺少参数：shadow_account"}

    device_fingerprint = generate_device_fingerprint(shadow_account)

    try:
        req_data = {"shadow_account": shadow_account}
        if device_fingerprint:
            req_data["device_fingerprint"] = device_fingerprint

        resp = requests.post(f"{API_URL}/heartbeat", json=req_data, timeout=10)
        result = resp.json()

        if result.get("code") == 0:
            data = result.get("data", {})
            return {"success": True, "status": data.get("status"), "message": ""}
        else:
            return {"success": False, "status": "invalid", "message": result.get("message", "心跳失败")}

    except requests.exceptions.RequestException as e:
        return {"success": False, "status": "error", "message": f"网络错误：{e}"}
    except Exception as e:
        return {"success": False, "status": "error", "message": f"未知错误：{e}"}
