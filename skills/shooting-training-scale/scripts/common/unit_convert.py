# -*- coding: utf-8 -*-
"""训练数据单位转换和标准化模块。

提供射击训练中常用的数据转换函数，包括时间单位转换、
心率分类、定型时长评级、训练量综合评估等。

所有函数均为纯函数，不涉及任何 IO 操作。
"""

from __future__ import annotations

from typing import Dict


def minutes_to_hours(min_val: float, decimal: int = 1) -> float:
    """分钟转小时。

    Args:
        min_val: 分钟数值。
        decimal: 保留小数位数，默认 1 位。

    Returns:
        转换后的小时数。

    Example:
        >>> minutes_to_hours(90)
        1.5
        >>> minutes_to_hours(45, decimal=2)
        0.75
    """
    result = min_val / 60.0
    return round(result, decimal)


def seconds_to_minutes(sec_val: float) -> float:
    """秒转分钟。

    Args:
        sec_val: 秒数值。

    Returns:
        转换后的分钟数（保留 1 位小数）。

    Example:
        >>> seconds_to_minutes(90)
        1.5
    """
    return round(sec_val / 60.0, 1)


def bpm_classify(bpm: float) -> str:
    """心率分类。

    根据静息心率数值判定健康等级（射击运动员适用标准）。

    Args:
        bpm: 静息心率值（次/分钟）。

    Returns:
        心率等级字符串：
        - "优秀" (<=55)
        - "良好" (<=65)
        - "正常" (<=75)
        - "偏高" (>75)

    Example:
        >>> bpm_classify(52)
        '优秀'
        >>> bpm_classify(80)
        '偏高'
    """
    if bpm <= 55:
        return "优秀"
    elif bpm <= 65:
        return "良好"
    elif bpm <= 75:
        return "正常"
    else:
        return "偏高"


def hold_time_classify(seconds: float) -> str:
    """定型时长评级。

    根据空枪定型保持时长判定等级。

    阈值标准（射击运动员空枪基础定型）：
    - "优秀" >= 60 秒
    - "良好" >= 45 秒
    - "合格" >= 30 秒
    - "需加强" < 30 秒

    Args:
        seconds: 定型保持时长（秒）。

    Returns:
        评级字符串。

    Example:
        >>> hold_time_classify(55)
        '良好'
        >>> hold_time_classify(25)
        '需加强'
    """
    if seconds >= 60:
        return "优秀"
    elif seconds >= 45:
        return "良好"
    elif seconds >= 30:
        return "合格"
    else:
        return "需加强"


def rounds_to_string(rounds: int) -> str:
    """发数格式化。

    将整数发数转换为带千位分隔符的中文字符串。

    Args:
        rounds: 弹药发数（整数）。

    Returns:
        格式化后的字符串，如 "1,234发"。

    Example:
        >>> rounds_to_string(1234)
        '1,234发'
        >>> rounds_to_string(500)
        '500发'
    """
    formatted = f"{rounds:,}"
    return f"{formatted}发"


def normalize_score(raw: float, max_val: float = 100) -> float:
    """百分制标准化。

    将原始分数按满分值标准化到百分制。

    Args:
        raw: 原始分数。
        max_val: 原始满分值，默认 100。

    Returns:
        标准化后的百分制得分（保留 1 位小数）。

    Example:
        >>> normalize_score(85, 100)
        85.0
        >>> normalize_score(38, 50)
        76.0
    """
    if max_val <= 0:
        return 0.0
    return round(raw / max_val * 100, 1)


def training_volume_classify(
    empty_triggers: int,
    live_rounds: int,
    hold_min: float,
) -> Dict[str, str]:
    """训练量综合评估。

    根据空枪扳机数、实弹发数、定型时长三个维度分别评级，
    并给出综合评级。

    评级标准（日训练量）：
    - 空枪：>=200 "达标"，>=100 "一般"，<100 "不足"
    - 实弹：>=50 "达标"，>=20 "一般"，<20 "不足"
    - 定型：>=60min "达标"，>=30min "一般"，<30min "不足"
    - 综合：三项均达标为 "优秀"，两项达标为 "良好"，
             一项达标为 "一般"，零项达标为 "不足"

    Args:
        empty_triggers: 日空枪扳机数。
        live_rounds: 日实弹发数。
        hold_min: 日定型时长（分钟）。

    Returns:
        包含各维度和综合评级的字典，格式如：
        {"空枪": "达标", "实弹": "一般", "定型": "不足", "综合": "一般"}。

    Example:
        >>> training_volume_classify(150, 30, 45)
        {'空枪': '一般', '实弹': '一般', '定型': '一般', '综合': '一般'}
    """
    # 空枪评级
    if empty_triggers >= 200:
        empty_level = "达标"
    elif empty_triggers >= 100:
        empty_level = "一般"
    else:
        empty_level = "不足"

    # 实弹评级
    if live_rounds >= 50:
        live_level = "达标"
    elif live_rounds >= 20:
        live_level = "一般"
    else:
        live_level = "不足"

    # 定型评级
    if hold_min >= 60:
        hold_level = "达标"
    elif hold_min >= 30:
        hold_level = "一般"
    else:
        hold_level = "不足"

    # 综合评级
    pass_count = sum(1 for lvl in [empty_level, live_level, hold_level] if lvl == "达标")

    if pass_count == 3:
        overall = "优秀"
    elif pass_count == 2:
        overall = "良好"
    elif pass_count == 1:
        overall = "一般"
    else:
        overall = "不足"

    return {
        "空枪": empty_level,
        "实弹": live_level,
        "定型": hold_level,
        "综合": overall,
    }


# ---------------------------------------------------------------------------
# 测试入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("unit_convert.py 模块测试")
    print("=" * 60)

    # 1. minutes_to_hours 测试
    print("\n[1] minutes_to_hours 测试")
    print(f"    90 分钟 = {minutes_to_hours(90)} 小时")
    print(f"    45 分钟 = {minutes_to_hours(45, decimal=2)} 小时")
    print(f"    0 分钟  = {minutes_to_hours(0)} 小时")

    # 2. seconds_to_minutes 测试
    print("\n[2] seconds_to_minutes 测试")
    print(f"    90 秒  = {seconds_to_minutes(90)} 分钟")
    print(f"    180 秒 = {seconds_to_minutes(180)} 分钟")
    print(f"    45 秒  = {seconds_to_minutes(45)} 分钟")

    # 3. bpm_classify 测试
    print("\n[3] bpm_classify 测试")
    for bpm in [50, 58, 63, 72, 80]:
        level = bpm_classify(bpm)
        print(f"    {bpm} bpm -> {level}")

    # 4. hold_time_classify 测试
    print("\n[4] hold_time_classify 测试")
    for sec in [70, 50, 35, 20]:
        level = hold_time_classify(sec)
        print(f"    {sec} 秒 -> {level}")

    # 5. rounds_to_string 测试
    print("\n[5] rounds_to_string 测试")
    for rounds in [500, 1234, 10000, 0]:
        print(f"    {rounds} -> {rounds_to_string(rounds)}")

    # 6. normalize_score 测试
    print("\n[6] normalize_score 测试")
    print(f"    85/100 = {normalize_score(85, 100)}%")
    print(f"    38/50  = {normalize_score(38, 50)}%")
    print(f"    92/120 = {normalize_score(92, 120)}%")

    # 7. training_volume_classify 测试
    print("\n[7] training_volume_classify 测试")
    test_cases = [
        (250, 60, 75, "全达标"),
        (150, 30, 45, "一般组合"),
        (50, 10, 20, "不足组合"),
        (200, 50, 30, "两项达标"),
    ]
    for empty, live, hold, desc in test_cases:
        result = training_volume_classify(empty, live, hold)
        print(f"    空枪={empty}, 实弹={live}, 定型={hold}min ({desc})")
        print(f"      -> {result}")

    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
