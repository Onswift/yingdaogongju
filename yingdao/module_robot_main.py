"""
影刀机器人主流程 - 调用授权验证模块示例

这个模块演示如何在影刀中调用其他功能模块

流程说明：
1. 调用「授权验证模块」检查账号授权
2. 如果授权通过，执行机器人任务
3. 定期调用「心跳模块」上报状态
4. 如果授权失败，调用「卡密兑换模块」兑换卡密

使用前需要：
1. 已创建以下模块：
   - module_check_license（授权验证）
   - module_redeem_card（卡密兑换）
   - module_heartbeat（心跳上报）
2. 修改本模块的配置
"""

# ==================== 配置区域 ====================
API_URL = "http://8.138.108.144:8001/api"  # 服务器 API 地址
SHADOW_ACCOUNT = "test_user"               # 影刀账号
TEST_CARD_CODE = ""                        # 测试卡密（可选）
MAX_ROUNDS = 10                            # 最大运行轮数
HEARTBEAT_INTERVAL = 3                     # 每多少轮发送一次心跳

# ==================== 导入依赖 ====================
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 主函数 ====================
def main(params):
    """
    机器人主流程

    参数:
        params: 影刀流程参数对象
        params.shadow_account: 影刀账号（可选，默认使用配置的）
        params.card_code: 卡密代码（可选，用于兑换）
    """
    # 获取参数（优先使用传入参数，否则使用配置）
    shadow_account = getattr(params, 'shadow_account', SHADOW_ACCOUNT)
    card_code = getattr(params, 'card_code', TEST_CARD_CODE)

    print("=" * 50)
    print("影刀机器人 - 主流程")
    print("=" * 50)
    print(f"账号：{shadow_account}")
    print("=" * 50)

    # ==================== 步骤 1: 检查授权 ====================
    print("\n[步骤 1] 检查授权状态...")

    # 调用授权验证模块
    from module_check_license import main as check_license

    check_result = check_license(type('Params', (), {'shadow_account': shadow_account})())

    if check_result.get("success"):
        print(f"✓ 授权验证通过")
        print(f"  状态：{check_result.get('status')}")
        print(f"  剩余：{check_result.get('remain_days')}天")
        print(f"  到期：{check_result.get('expire_at')}")
        has_license = True
    else:
        print(f"✗ 授权验证失败：{check_result.get('message')}")
        has_license = False

    # ==================== 步骤 2: 如果没有授权，尝试兑换 ====================
    if not has_license and card_code:
        print("\n[步骤 2] 尝试兑换卡密...")

        from module_redeem_card import main as redeem_card

        redeem_result = redeem_card(type('Params', (), {
            'shadow_account': shadow_account,
            'card_code': card_code
        })())

        if redeem_result.get("success"):
            print(f"✓ 兑换成功")
            print(f"  状态：{redeem_result.get('status')}")
            print(f"  剩余：{redeem_result.get('remain_days')}天")
            has_license = True
        else:
            print(f"✗ 兑换失败：{redeem_result.get('message')}")

    # 如果没有授权且无法兑换，退出
    if not has_license:
        print("\n[终止] 无有效授权，机器人无法运行")
        return {
            "success": False,
            "reason": "no_license"
        }

    # ==================== 步骤 3: 执行机器人任务 ====================
    print("\n[步骤 3] 执行机器人任务...")

    from module_heartbeat import main as heartbeat

    round_count = 0

    for i in range(MAX_ROUNDS):
        round_count += 1

        # 定期发送心跳
        if round_count % HEARTBEAT_INTERVAL == 0:
            print(f"  [心跳] 第 {round_count} 轮...")
            hb_result = heartbeat(type('Params', (), {'shadow_account': shadow_account})())
            if not hb_result.get("success"):
                print(f"  [警告] 心跳异常：{hb_result.get('message')}")
                # 可以选择继续或退出

        print(f"  执行第 {i+1} 轮任务...")
        # 在这里写你的实际业务逻辑
        time.sleep(1)

    print("\n" + "=" * 50)
    print("任务执行完成")
    print("=" * 50)

    return {
        "success": True,
        "rounds_completed": round_count
    }


# ==================== 简单调用示例 ====================
def simple_main(params):
    """
    简单版本 - 只验证授权，不执行任务

    参数:
        params.shadow_account: 影刀账号
    """
    shadow_account = getattr(params, 'shadow_account', '')

    from module_check_license import main as check_license

    result = check_license(type('Params', (), {'shadow_account': shadow_account})())

    if result.get("success"):
        print(f"✓ 授权通过 - 剩余{result.get('remain_days')}天")
    else:
        print(f"✗ 授权失败：{result.get('message')}")

    return result
